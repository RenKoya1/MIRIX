#!/usr/bin/env python3
"""
Mirix - AI Assistant Application
Entry point for the Mirix application.
"""

import sys
import argparse
import os
from pathlib import Path
from dotenv import load_dotenv
from google.oauth2 import id_token
import google.auth.transport.requests
from google.auth import exceptions


load_dotenv()

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def main():
    """Main entry point for Mirix application."""
    parser = argparse.ArgumentParser(description="Mirix AI Assistant Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument(
        "--port", type=int, default=None, help="Port to bind the server to"
    )

    args = parser.parse_args()

    # Determine port from command line, environment variable, or default
    port = args.port
    if port is None:
        port = int(os.environ.get("PORT", 8000))

    print(f"Starting Mirix server on {args.host}:{port}")

    import uvicorn
    from mirix.server import app

    uvicorn.run(app, host=args.host, port=port)


from mirix.agent import AgentWrapper


def handle_memory_request(request):
    request_json = request.get_json(silent=True)
    message = request_json.get("message", [])
    chat_id = request_json.get("chat_id", None)
    name = request_json.get("name", "Unknown User")
    print(request_json)
    if not message:
        return {"error": "Message is required"}, 400
    config_path = os.path.join(os.path.dirname(__file__), "configs/mirix.yaml")
    print("Config path:", config_path)
    agent = AgentWrapper(config_path, user_id=chat_id)
    is_store = request_json.get("is_store", False)
    if is_store:
        print("Storing memory for chat_id:", chat_id)
        agent.send_message(
            message=message,
            memorizing=True,
            force_absorb_content=True,
        )
        print("-----------------------Memory stored successfully")
    else:
        print("Retrieving response for chat_id:", chat_id)
        response = agent.send_message(message=message, memorizing=False)

        print("Response received:", response)
        return {"response": response}


if __name__ == "__main__":
    # main()

    class MockRequest:
        def __init__(self, json_data):
            self._json = json_data
            self.headers = {}

        def get_json(self, silent=True):
            return self._json

    mock_request = MockRequest(
        {
            "message": "Hello, this is a test message.",
            "chat_id": "kfddddjkfdsafda",
            "name": "Test User",
            "is_store": True,
        }
    )
    handle_memory_request(mock_request)
