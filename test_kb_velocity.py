import os
import time
import shutil
import tempfile
from pathlib import Path
from unittest.mock import patch
from dotenv import load_dotenv

# Ensure environment is loaded
load_dotenv()

from src.core.knowledge import get_knowledge_base

def test_kb_velocity():
    # 1. Scaffold temporary directory tree
    temp_dir = tempfile.mkdtemp(prefix="autoswarm_kb_test_")
    try:
        temp_path = Path(temp_dir)
        
        # Valid files
        valid_dir = temp_path / "valid"
        valid_dir.mkdir()
        for i in range(10):
            (valid_dir / f"doc_{i}.txt").write_text(f"This is a valid text document {i}.")
            (valid_dir / f"note_{i}.md").write_text(f"# Markdown Note {i}\nSome content.")
            
        # Nested empty folders & directories
        nested_dir = temp_path / "nested" / "empty"
        nested_dir.mkdir(parents=True)
        
        # Unsupported / fake binary files
        invalid_dir = temp_path / "binaries"
        invalid_dir.mkdir()
        (invalid_dir / "fake.exe").write_bytes(b"\x00\x01\x02")
        (invalid_dir / "image.png").write_bytes(b"\x89PNG\r\n\x1a\n")
        (invalid_dir / "data.dat").write_bytes(os.urandom(128))
        
        total_valid_files = 20

        # Mock the hardcoded Path("workspace") in knowledge.py to point to our temp_dir
        with patch('src.core.knowledge.Path') as MockPath:
            # We only mock the particular Path("workspace") call
            def mock_path(path_str, *args, **kwargs):
                if path_str == "workspace":
                    return temp_path
                return Path(path_str, *args, **kwargs)
            
            MockPath.side_effect = mock_path

            # 2. Initialize the patched KB
            print("[*] Initializing Knowledge Base...")
            kb = get_knowledge_base()
            
            # Extract valid files recognized by our patch
            valid_files_detected = kb.valid_flat_files
            
            # Assert 1: Only approved files detected (no directories, no .exe/.png)
            assert len(valid_files_detected) == total_valid_files, f"Expected {total_valid_files} valid files, found {len(valid_files_detected)}"
            for fpath in valid_files_detected:
                assert Path(fpath).suffix.lower() in {".txt", ".md"}, f"Invalid file type detected: {fpath}"
                assert Path(fpath).is_file(), f"Directory detected as file: {fpath}"
            
            # 3. Execute forced ingest
            print(f"[*] Starting ingestion of {len(valid_files_detected)} documents...")
            
            # Drop existing table context to ensure fresh count for test
            if kb.vector_db.exists():
                kb.vector_db.drop()
            kb.vector_db.create()
                
            start_time = time.time()
            
            # Actual ingestion based on the extracted valid files
            for filepath in valid_files_detected:
                text_content = Path(filepath).read_text(errors="ignore")
                kb.insert(
                    text_content=text_content,
                    name=Path(filepath).name,
                    metadata={"source": "velocity_test", "path": filepath}
                )
                
            end_time = time.time()
            delta_t = end_time - start_time
            
            # 4. Log timestamp delta & calculate velocity
            velocity = total_valid_files / delta_t if delta_t > 0 else 0
            count = 0
            if kb.vector_db.exists():
                df = kb.vector_db.table.to_pandas()
                count = len(df)
                
                if count > 0:
                    # Agno lancedb uses 'embedding' by default
                    emb_col = 'embedding' if 'embedding' in df.columns else 'vector'
                    if emb_col in df.columns:
                        sample_emb = df.iloc[0][emb_col]
                        assert len(sample_emb) > 0, "Empty embedding array detected."
                        assert any(float(x) != 0.0 for x in sample_emb), "Dense vector contains only floating zeros."
                        print(f"    - Vector Dim:    {len(sample_emb)}")
                    else:
                        print("    - Vector Check:  [WARN] No embedding/vector column found in schema.")

                
            print(f"[*] Ingestion Complete:")
            print(f"    - Time elapsed:  {delta_t:.3f} seconds")
            print(f"    - Velocity:      {velocity:.2f} docs/sec")
            print(f"    - Vectors Stored:{count}")
            
            # Assert 2: Final vector count matches valid file count
            assert count == total_valid_files, f"Vector count mismatch: Expected {total_valid_files}, got {count}"
            
            print("\n[SUCCESS] Knowledge Base Velocity & Integrity Test Passed.")

    finally:
        # 5. Clean up temporary directory
        shutil.rmtree(temp_dir, ignore_errors=True)
        print(f"[*] Cleaned up temporary directory: {temp_dir}")

if __name__ == "__main__":
    test_kb_velocity()
