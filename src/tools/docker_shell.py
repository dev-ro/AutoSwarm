
import subprocess
import os
from agno.tools import Toolkit

class DockerShellTools(Toolkit):
    def __init__(self, container_name: str = "autoswarm_sandbox", work_dir: str = "/workspace"):
        super().__init__(name="docker_shell_tools")
        self.container_name = container_name
        self.work_dir = work_dir
        self.register(self.run_in_docker)
        
        # Ensure container is running (idempotent)
        self._ensure_container()

    def _ensure_container(self):
        try:
            # Check if running
            subprocess.run(
                ["docker", "inspect", self.container_name], 
                check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except subprocess.CalledProcessError:
            print(f"[Docker] Starting sandbox container '{self.container_name}'...")
            # Run a lightweight python alpine container that sleeps forever
            # Ensure workspace directory exists locally before mounting
            workspace_abs_path = os.path.abspath('./workspace')
            if not os.path.exists(workspace_abs_path):
                os.makedirs(workspace_abs_path)
                
            src_abs_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
            
            # Remove existing container to apply new mounts (simple reset)
            subprocess.run(["docker", "rm", "-f", self.container_name], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)

            subprocess.run([
                "docker", "run", "-d",
                "--name", self.container_name,
                "-v", f"{workspace_abs_path}:{self.work_dir}", # Mount workspace
                "-v", f"{src_abs_path}:{self.work_dir}/src",   # Mount src
                "-w", self.work_dir,
                "python:3.11-alpine", "sleep", "infinity"
            ], check=True)

    def run_in_docker(self, command: str) -> str:
        """
        Executes a shell command inside the secure Docker sandbox.
        """
        print(f"  [Docker] Executing: {command}")
        try:
            # Use 'docker exec' to run command
            result = subprocess.run(
                ["docker", "exec", self.container_name, "sh", "-c", command],
                capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=30
            )
            output = result.stdout + result.stderr
            return output if output.strip() else "(Command executed with no output)"
        except Exception as e:
            return f"Docker Execution Error: {e}"
