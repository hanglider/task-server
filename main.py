import os
import socket
from server_routes import app
import uvicorn

def get_host():
    """Retrieve the host IP address dynamically."""
    name = socket.gethostname()
    return socket.gethostbyname(name)

def main():
    host = os.getenv("HOST", "192.168.1.107")
    port = int(os.getenv("PORT", 5000))

    print(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    main()
