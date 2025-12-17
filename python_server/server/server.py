"""
Main server implementation using FastAPI with WebSocket support.
Port of server/core/Server.js and server/launcher.js
"""
import os
import asyncio
from typing import Dict, Optional
from starlette.applications import Starlette
from starlette.routing import Route, WebSocketRoute, Mount
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect

from .socket_client import SocketClient
from .collection import Collection
from .repositories.room_repository import RoomRepository
from .controllers.rooms_controller import RoomsController
from .event_emitter import EventEmitter


class Server(EventEmitter):
    """
    Main game server that handles WebSocket connections and room management.
    """
    
    def __init__(self, config: Optional[Dict] = None):
        super().__init__()
        
        self.config = config or {'port': 8080}
        self.clients: Collection[SocketClient] = Collection([], 'id', True)
        
        # Initialize repositories and controllers
        self.room_repository = RoomRepository()
        self.rooms_controller = RoomsController(self.room_repository)
        
        print(f"Server initialized")
    
    async def handle_websocket(self, websocket: WebSocket) -> None:
        """Handle a new WebSocket connection."""
        print(f"WebSocket connection attempt from {websocket.client}")
        print(f"Headers: {dict(websocket.headers)}")
        client = None
        try:
            # Accept with 'websocket' subprotocol - client requests this
            print("Accepting WebSocket connection...")
            await websocket.accept(subprotocol='websocket')
            print("WebSocket connection accepted!")
            
            # Get client IP (from headers or connection)
            ip = websocket.client.host if websocket.client else 'unknown'
            headers = dict(websocket.headers)
            if 'x-real-ip' in headers:
                ip = headers['x-real-ip']
            
            # Create socket client with 1ms interval for batching
            client = SocketClient(websocket, interval=0.001, ip=ip)
            self.clients.add(client)
            
            print(f"Client {client.id} connected from {ip}")
            
            # Attach to rooms controller
            self.rooms_controller.attach(client)
            self.emit('client', client)
            
            # Start client message loop
            await client.start()
            
            while True:
                data = await websocket.receive_text()
                await client.on_message(data)
                
        except WebSocketDisconnect:
            print(f"Client {client.id if client else 'unknown'} disconnected normally")
        except Exception as e:
            import traceback
            print(f"WebSocket error for client {client.id if client else 'unknown'}: {e}")
            traceback.print_exc()
        finally:
            if client:
                await self._on_socket_disconnection(client)
    
    async def _on_socket_disconnection(self, client: SocketClient) -> None:
        """Handle client disconnection."""
        print(f"Client {client.id} disconnected")
        await client.on_close()
        self.clients.remove(client)


def create_app() -> Starlette:
    """Create and configure the Starlette application."""
    print("=" * 50)
    print("Creating Modaltron app...")
    print("=" * 50)
    
    try:
        # Initialize server
        server = Server()
        print("Server instance created")
    except Exception as e:
        print(f"Error creating server: {e}")
        import traceback
        traceback.print_exc()
        raise
    
    # Determine web directory path
    web_dir = os.environ.get('WEB_DIR', '/root/web')
    print(f"Checking web dir: {web_dir}, exists: {os.path.exists(web_dir)}")
    if not os.path.exists(web_dir):
        # Try relative path for local development
        web_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'web')
        print(f"Trying: {web_dir}, exists: {os.path.exists(web_dir)}")
        if not os.path.exists(web_dir):
            web_dir = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'web')
            print(f"Trying: {web_dir}, exists: {os.path.exists(web_dir)}")
    
    web_dir = os.path.abspath(web_dir) if os.path.exists(web_dir) else None
    print(f"Final web_dir: {web_dir}")
    
    # Define route handlers
    async def homepage(request):
        if web_dir:
            index_path = os.path.join(web_dir, 'index.html')
            if os.path.exists(index_path):
                return FileResponse(index_path)
        return HTMLResponse("<h1>Modaltron Server Running</h1>")
    
    async def health_check(request):
        return HTMLResponse("OK")
    
    async def websocket_handler(websocket: WebSocket):
        await server.handle_websocket(websocket)
    
    # Build routes list
    routes = [
        # Health check endpoint
        Route("/health", health_check),
        # WebSocket route at root - this handles upgrade requests
        WebSocketRoute("/", websocket_handler),
        # HTTP route for serving index
        Route("/", homepage),
    ]
    
    # Add static file mounts
    if web_dir and os.path.exists(web_dir):
        static_dirs = ['css', 'js', 'images', 'sounds', 'font']
        for dir_name in static_dirs:
            dir_path = os.path.join(web_dir, dir_name)
            if os.path.exists(dir_path):
                routes.append(Mount(f"/{dir_name}", StaticFiles(directory=dir_path), name=dir_name))
    
    app = Starlette(debug=True, routes=routes)
    
    print("=" * 50)
    print("App created successfully!")
    print(f"Routes: {[(r.path, type(r).__name__) for r in routes]}")
    print("=" * 50)
    
    return app

