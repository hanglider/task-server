import os
import socket
from asgiref.wsgi import WsgiToAsgi
from server_routes import app
import uvicorn

def get_host():
    """Retrieve the host IP address dynamically."""
    name = socket.gethostname()
    return socket.gethostbyname(name)

def main():
    # Load configuration from environment variables
    host = os.getenv("HOST", "192.168.1.107")#get_host())      # Defaults to machine IP
    port = int(os.getenv("PORT", 5000))       # Defaults to port 5000

    # Wrapping Flask app with ASGI for async support
    asgi_app = WsgiToAsgi(app)

    # Running the Uvicorn ASGI server
    print(f"Starting server on {host}:{port}")
    uvicorn.run(asgi_app, host=host, port=port)

if __name__ == "__main__":
    main()
