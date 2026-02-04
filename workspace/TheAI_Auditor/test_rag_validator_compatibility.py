import unittest
from pydantic import ValidationError
from rag_validator import RetrievalChunk, ValidatedRAGInput
from unittest.mock import MagicMock

class TestRAGValidatorCompatibility(unittest.TestCase):
    def test_pydantic_v3_compliance(self):
        """
        Test if the validator uses field_validator (v2/v3 style) 
        instead of the deprecated @validator.
        """
        # Valid chunk
        chunk = RetrievalChunk(
            chunk_id="1",
            content="Normal content",
            source_metadata={},
            relevance_score=0.8
        )
        self.assertEqual(chunk.chunk_id, "1")

        # Invalid content (injection)
        with self.assertRaises(ValidationError) as cm:
            RetrievalChunk(
                chunk_id="2",
                content="System override initiated",
                source_metadata={},
                relevance_score=0.9
            )
        self.assertIn("Adversarial pattern detected", str(cm.exception))

        # Low relevance score
        with self.assertRaises(ValidationError):
            RetrievalChunk(
                chunk_id="3",
                content="Safe content",
                source_metadata={},
                relevance_score=0.5
            )

    def test_pinecone_v3_integration(self):
        """
        Simulate Pinecone v3+ response compatibility.
        Pinecone v3 matches are usually objects with id, score, metadata.
        """
        mock_match = MagicMock()
        mock_match.id = "pin-1"
        mock_match.score = 0.95
        mock_match.metadata = {"text": "Pinecone retrieved text", "source": "archive"}

        # Simulate mapping Pinecone match to RetrievalChunk
        chunk = RetrievalChunk(
            chunk_id=mock_match.id,
            content=mock_match.metadata["text"],
            source_metadata=mock_match.metadata,
            relevance_score=mock_match.score
        )
        self.assertEqual(chunk.chunk_id, "pin-1")

    def test_weaviate_v4_integration(self):
        """
        Simulate Weaviate v4 response compatibility.
        Weaviate v4 uses collection-based API, returning objects with properties and metadata.
        """
        # Mock Weaviate v4 object
        mock_obj = MagicMock()
        mock_obj.uuid = "weaviate-uuid"
        mock_obj.properties = {"content": "Weaviate v4 content", "author": "bot"}
        mock_obj.metadata.score = 0.88

        chunk = RetrievalChunk(
            chunk_id=str(mock_obj.uuid),
            content=mock_obj.properties["content"],
            source_metadata=mock_obj.properties,
            relevance_score=mock_obj.metadata.score
        )
        self.assertEqual(chunk.content, "Weaviate v4 content")

    def test_milvus_3_0_integration(self):
        """
        Simulate Milvus 3.0 response compatibility.
        Milvus 3.0 returns results typically as a list of dicts from MilvusClient.search.
        """
        milvus_result = {
            "id": 12345,
            "distance": 0.92,
            "entity": {
                "text": "Milvus 3.0 search result",
                "meta": "important"
            }
        }

        chunk = RetrievalChunk(
            chunk_id=str(milvus_result["id"]),
            content=milvus_result["entity"]["text"],
            source_metadata=milvus_result["entity"],
            relevance_score=milvus_result["distance"]
        )
        self.assertEqual(chunk.relevance_score, 0.92)

if __name__ == "__main__":
    unittest.main()