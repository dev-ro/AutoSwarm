import asyncio
import json
import subprocess
import sys

async def run_test():
    # Start the server as a subprocess
    process = subprocess.Popen(
        [sys.executable, "MCP_Mock_Server/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    def send_request(request):
        try:
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            line = process.stdout.readline()
            if not line:
                return None
            return json.loads(line)
        except Exception as e:
            print(f"Error sending request: {e}")
            return None

    try:
        # 1. Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        print("Sending initialize...")
        init_response = send_request(init_request)
        print("Initialize response:", json.dumps(init_response, indent=2))

        # 2. Initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        process.stdin.write(json.dumps(initialized_notification) + "\n")
        process.stdin.flush()

        # 3. List tools
        list_tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        print("\nSending tools/list...")
        list_tools_response = send_request(list_tools_request)
        print("Tools list response:", json.dumps(list_tools_response, indent=2))

        # 4. Call tool (echo)
        call_echo_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"message": "Hello, MCP!"}
            }
        }
        print("\nSending tools/call (echo)...")
        call_echo_response = send_request(call_echo_request)
        print("Call echo response:", json.dumps(call_echo_response, indent=2))

        # 5. List resources
        list_resources_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "resources/list",
            "params": {}
        }
        print("\nSending resources/list...")
        list_resources_response = send_request(list_resources_request)
        print("Resources list response:", json.dumps(list_resources_response, indent=2))

        # 6. Read resource
        read_resource_request = {
            "jsonrpc": "2.0",
            "id": 5,
            "method": "resources/read",
            "params": {
                "uri": "mock://info"
            }
        }
        print("\nSending resources/read...")
        read_resource_response = send_request(read_resource_request)
        print("Read resource response:", json.dumps(read_resource_response, indent=2))

    finally:
        process.terminate()
        process.wait()

if __name__ == "__main__":
    asyncio.run(run_test())