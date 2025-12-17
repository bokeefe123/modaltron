"""
Modal entry point for Modaltron game server.
Runs a FastAPI server with WebSocket support for real-time multiplayer gameplay.
"""
import modal

app = modal.App("modaltron")

# Build image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "starlette>=0.32.0",
        "uvicorn>=0.24.0",
        "websockets>=12.0",
        "aiofiles>=23.0.0",
    )
    .add_local_dir("server", remote_path="/root/server")
    .add_local_dir("../web", remote_path="/root/web")
)


@app.function(
    image=image,
    scaledown_window=300,  # Keep warm for 5 minutes during active games
    region="us-west",
    experimental_options={"input_plane_region": "us-west"}
)
@modal.concurrent(max_inputs=100)  # Handle many concurrent WebSocket connections
@modal.asgi_app()
def serve():
    """ASGI entry point for Modal."""
    import sys
    sys.path.insert(0, "/root")
    from server.server import create_app
    return create_app()


# For local development
if __name__ == "__main__":
    import uvicorn
    import sys
    import os
    
    # Add server to path for local dev
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    from server.server import create_app
    app = create_app()
    uvicorn.run(app, host="0.0.0.0", port=8080)

