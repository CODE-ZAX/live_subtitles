import os
import tempfile
import uuid
from pathlib import Path
from typing import Optional
import shutil

from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
import logging
import json
import asyncio

from src.transcriber import Transcriber
from src.subtitle_generator import SubtitleGenerator
from src.utils import overlay_subtitles

# Create FastAPI app
app = FastAPI(
    title="AI Video Transcription API",
    description="Generate subtitles for videos with customizable styling",
    version="1.0.0"
)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Validation error on {request.url}: {exc}")
    logger.error(f"Request body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": exc.errors(),
            "body": str(await request.body())
        }
    )

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create necessary directories
UPLOAD_DIR = Path("uploads")
OUTPUT_DIR = Path("outputs")
STATIC_DIR = Path("frontend/build")

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# Mount static files for React frontend
if STATIC_DIR.exists():
    # Mount the static subdirectory for CSS/JS files
    static_assets_dir = STATIC_DIR / "static"
    if static_assets_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_assets_dir)), name="static")

# Pydantic models for request/response
class SubtitleStyle(BaseModel):
    font_size: int = 28
    font_family: str = "Bangers-Regular.ttf"
    font_color: str = "white"
    highlight_color: str = "yellow"
    bottom_padding: int = 100
    word_mode: bool = True

class ProcessingStatus(BaseModel):
    status: str
    progress: int
    message: str
    task_id: str

# In-memory storage for task status (use Redis in production)
task_status = {}

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, task_id: str):
        await websocket.accept()
        self.active_connections[task_id] = websocket

    def disconnect(self, task_id: str):
        if task_id in self.active_connections:
            del self.active_connections[task_id]

    def update_task_id(self, old_task_id: str, new_task_id: str):
        """Update the task ID mapping without reconnecting the WebSocket"""
        if old_task_id in self.active_connections:
            websocket = self.active_connections[old_task_id]
            del self.active_connections[old_task_id]
            self.active_connections[new_task_id] = websocket

    async def send_progress(self, task_id: str, message: dict):
        logger.info(f"Attempting to send progress for task_id: {task_id}")
        logger.info(f"Active connections: {list(self.active_connections.keys())}")
        if task_id in self.active_connections:
            try:
                await self.active_connections[task_id].send_text(json.dumps(message))
                logger.info(f"Successfully sent progress update for task_id: {task_id}")
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {e}")
                self.disconnect(task_id)
        else:
            logger.warning(f"No WebSocket connection found for task_id: {task_id}")

manager = ConnectionManager()

@app.get("/")
async def root():
    """Serve the React frontend"""
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        return FileResponse(str(STATIC_DIR / "index.html"))
    return {"message": "AI Video Transcription API", "status": "running", "static_dir_exists": STATIC_DIR.exists()}

@app.get("/debug/static")
async def debug_static():
    """Debug endpoint to check static file structure"""
    if not STATIC_DIR.exists():
        return {"error": "Static directory does not exist", "path": str(STATIC_DIR)}
    
    files = []
    for item in STATIC_DIR.rglob("*"):
        if item.is_file():
            files.append(str(item.relative_to(STATIC_DIR)))
    
    return {
        "static_dir": str(STATIC_DIR),
        "files": files,
        "index_exists": (STATIC_DIR / "index.html").exists()
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "API is running"}

@app.websocket("/ws/{task_id}")
async def websocket_endpoint(websocket: WebSocket, task_id: str):
    """WebSocket endpoint for real-time progress updates"""
    await manager.connect(websocket, task_id)
    logger.info(f"WebSocket connected for task: {task_id}")
    
    # Send initial connection confirmation
    await websocket.send_text(json.dumps({
        "type": "connected",
        "task_id": task_id,
        "message": "WebSocket connected successfully"
    }))
    
    try:
        while True:
            # Keep connection alive and handle any incoming messages
            data = await websocket.receive_text()
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong", "message": "Connection alive"}))
                elif message.get("type") == "update_task_id":
                    # Handle task ID updates for temporary connections
                    new_task_id = message.get("new_task_id")
                    if new_task_id and new_task_id != task_id:
                        logger.info(f"Updating WebSocket task ID from {task_id} to {new_task_id}")
                        manager.update_task_id(task_id, new_task_id)
                        task_id = new_task_id
                        logger.info(f"WebSocket task ID updated. Active connections: {list(manager.active_connections.keys())}")
                        await websocket.send_text(json.dumps({
                            "type": "task_id_updated",
                            "new_task_id": new_task_id,
                            "message": "Task ID updated successfully"
                        }))
            except json.JSONDecodeError:
                # Handle plain text messages
                await websocket.send_text(json.dumps({"type": "pong", "message": "Connection alive"}))
    except WebSocketDisconnect:
        manager.disconnect(task_id)
        logger.info(f"WebSocket disconnected for task {task_id}")

@app.get("/manifest.json")
async def serve_manifest():
    """Serve the manifest.json file"""
    manifest_path = STATIC_DIR / "manifest.json"
    if manifest_path.exists():
        return FileResponse(str(manifest_path))
    raise HTTPException(status_code=404, detail="Manifest not found")

@app.post("/api/debug-upload")
async def debug_upload(request: Request):
    """Debug endpoint to see raw request data"""
    try:
        # Get raw body
        body = await request.body()
        logger.info(f"Raw request body: {body}")
        
        # Try to parse as form data
        form = await request.form()
        logger.info(f"Form data: {dict(form)}")
        
        return {
            "raw_body": str(body),
            "form_data": dict(form),
            "content_type": request.headers.get("content-type"),
            "headers": dict(request.headers)
        }
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {"error": str(e)}

@app.post("/api/test-upload")
async def test_upload(
    file: UploadFile = File(...),
    font_size: int = Form(28),
    font_family: str = Form("Bangers-Regular.ttf"),
    font_color: str = Form("white"),
    highlight_color: str = Form("yellow"),
    bottom_padding: int = Form(100),
    word_mode: str = Form("true")
):
    """Test endpoint to debug form data"""
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "font_size": font_size,
        "font_family": font_family,
        "font_color": font_color,
        "highlight_color": highlight_color,
        "bottom_padding": bottom_padding,
        "word_mode": word_mode,
        "word_mode_type": type(word_mode).__name__
    }

@app.post("/api/upload")
async def upload_video(
    file: UploadFile = File(...),
    font_size: int = Form(28),
    font_family: str = Form("Bangers-Regular.ttf"),
    font_color: str = Form("white"),
    highlight_color: str = Form("yellow"),
    bottom_padding: int = Form(100),
    word_mode: str = Form("true")  # Changed to string to handle form data properly
):
    """Upload video and start processing with subtitle generation"""
    
    logger.info(f"Upload request received - File: {file.filename}, Content-Type: {file.content_type}")
    logger.info(f"Form parameters - font_size: {font_size}, word_mode: {word_mode}")
    
    # Convert string boolean to actual boolean
    word_mode_bool = word_mode.lower() in ('true', '1', 'yes', 'on')
    
    # Debug logging
    logger.info(f"Processed parameters - File: {file.filename}, Size: {font_size}, Word mode: {word_mode} -> {word_mode_bool}")
    
    # Validate file type
    if not file.content_type.startswith('video/'):
        logger.error(f"Invalid file type: {file.content_type}")
        raise HTTPException(status_code=400, detail="File must be a video")
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())
    
    # Save uploaded file
    file_extension = Path(file.filename).suffix
    video_filename = f"{task_id}{file_extension}"
    video_path = UPLOAD_DIR / video_filename
    
    try:
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Initialize task status
        task_status[task_id] = {
            "status": "processing",
            "progress": 0,
            "message": "Starting transcription...",
            "video_path": str(video_path),
            "style": {
                "font_size": font_size,
                "font_family": font_family,
                "font_color": font_color,
                "highlight_color": highlight_color,
                "bottom_padding": bottom_padding,
                "word_mode": word_mode_bool
            }
        }
        
        # Start processing in background
        import asyncio
        asyncio.create_task(process_video(task_id))
        
        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Video uploaded successfully. Processing started."
        }
        
    except Exception as e:
        # Clean up on error
        if video_path.exists():
            video_path.unlink()
        print(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")

async def process_video(task_id: str):
    """Process video with subtitles in background"""
    try:
        task_info = task_status[task_id]
        video_path = task_info["video_path"]
        style = task_info["style"]
        
        # Step 1: Transcribe audio
        logger.info(f"Starting Step 1: Transcribing Audio for task {task_id}")
        await send_progress_update(task_id, {
            "step": 1,
            "step_name": "Transcribing Audio",
            "progress": 20,
            "message": "Extracting and transcribing audio...",
            "status": "processing"
        })
        await asyncio.sleep(0.1)  # Small delay to ensure message is sent
        
        logger.info(f"Calling Transcriber for task {task_id}")
        transcriber = Transcriber(video_path)
        transcriber.transcribe_audio()
        transcription = transcriber.get_transcription()
        logger.info(f"Transcription completed for task {task_id}")
        
        # Step 2: Generate subtitles
        logger.info(f"Starting Step 2: Generating Subtitles for task {task_id}")
        await send_progress_update(task_id, {
            "step": 2,
            "step_name": "Generating Subtitles",
            "progress": 50,
            "message": "Creating subtitle file...",
            "status": "processing"
        })
        await asyncio.sleep(0.1)  # Small delay to ensure message is sent
        
        srt_filename = f"{task_id}.srt"
        srt_path = OUTPUT_DIR / srt_filename
        subtitle_generator = SubtitleGenerator()
        subtitle_generator.generate_subtitles(
            transcription, 
            str(srt_path), 
            word_mode=style["word_mode"]
        )
        logger.info(f"Subtitles generated for task {task_id}")
        
        # Step 3: Overlay subtitles
        logger.info(f"Starting Step 3: Creating Video for task {task_id}")
        await send_progress_update(task_id, {
            "step": 3,
            "step_name": "Creating Video",
            "progress": 80,
            "message": "Overlaying subtitles onto video...",
            "status": "processing"
        })
        await asyncio.sleep(0.1)  # Small delay to ensure message is sent
        
        output_filename = f"{task_id}_with_subtitles.mp4"
        output_path = OUTPUT_DIR / output_filename
        
        logger.info(f"Calling overlay_subtitles for task {task_id}")
        overlay_subtitles(
            video_path,
            str(srt_path),
            str(output_path),
            font_size=style["font_size"],
            font=style["font_family"],
            color=style["font_color"],
            bottom_padding=style["bottom_padding"],
            highlight_color=style["highlight_color"]
        )
        logger.info(f"Video overlay completed for task {task_id}")
        
        # Step 4: Finalizing
        logger.info(f"Starting Step 4: Finalizing for task {task_id}")
        await send_progress_update(task_id, {
            "step": 4,
            "step_name": "Finalizing",
            "progress": 95,
            "message": "Finalizing output...",
            "status": "processing"
        })
        await asyncio.sleep(0.1)  # Small delay to ensure message is sent
        
        # Complete
        logger.info(f"Completing task {task_id}")
        task_status[task_id].update({
            "status": "completed",
            "progress": 100,
            "message": "Processing completed successfully!",
            "output_video": output_filename,
            "subtitle_file": srt_filename
        })
        
        await send_progress_update(task_id, {
            "step": 4,
            "step_name": "Finalizing",
            "progress": 100,
            "message": "Processing completed successfully!",
            "status": "completed",
            "output_video": output_filename,
            "subtitle_file": srt_filename
        })
        logger.info(f"Task {task_id} completed successfully")
        
    except Exception as e:
        error_msg = f"Error processing video: {str(e)}"
        task_status[task_id].update({
            "status": "error",
            "progress": 0,
            "message": error_msg
        })
        
        await send_progress_update(task_id, {
            "step": 0,
            "step_name": "Error",
            "progress": 0,
            "message": error_msg,
            "status": "error"
        })

async def send_progress_update(task_id: str, data: dict):
    """Send progress update via WebSocket and update task status"""
    logger.info(f"send_progress_update called for task_id: {task_id} with data: {data}")
    
    # Update task status
    if task_id in task_status:
        task_status[task_id].update({
            "progress": data.get("progress", 0),
            "message": data.get("message", ""),
            "status": data.get("status", "processing")
        })
        logger.info(f"Updated task status for {task_id}: {task_status[task_id]}")
    else:
        logger.warning(f"Task {task_id} not found in task_status")
    
    # Send via WebSocket - try both the real task ID and any temporary task IDs
    sent = False
    if task_id in manager.active_connections:
        await manager.send_progress(task_id, {
            "type": "progress",
            "task_id": task_id,
            **data
        })
        sent = True
    else:
        # Try to find any temporary task ID that might be associated
        for temp_task_id in list(manager.active_connections.keys()):
            if temp_task_id.startswith("temp_"):
                logger.info(f"Trying to send progress to temporary task ID: {temp_task_id}")
                await manager.send_progress(temp_task_id, {
                    "type": "progress",
                    "task_id": task_id,
                    **data
                })
                sent = True
                break
    
    if not sent:
        logger.warning(f"No WebSocket connection found for task_id: {task_id} or any temporary task IDs")

@app.get("/api/status/{task_id}")
async def get_status(task_id: str):
    """Get processing status for a task"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task_status[task_id]

@app.get("/api/download/{task_id}")
async def download_video(task_id: str):
    """Download the processed video with subtitles"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = task_status[task_id]
    if task_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video processing not completed")
    
    output_filename = task_info["output_video"]
    output_path = OUTPUT_DIR / output_filename
    
    if not output_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found")
    
    return FileResponse(
        path=str(output_path),
        filename=output_filename,
        media_type="video/mp4"
    )

@app.get("/api/download/subtitles/{task_id}")
async def download_subtitles(task_id: str):
    """Download the SRT subtitle file"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = task_status[task_id]
    if task_info["status"] != "completed":
        raise HTTPException(status_code=400, detail="Video processing not completed")
    
    subtitle_filename = task_info["subtitle_file"]
    subtitle_path = OUTPUT_DIR / subtitle_filename
    
    if not subtitle_path.exists():
        raise HTTPException(status_code=404, detail="Subtitle file not found")
    
    return FileResponse(
        path=str(subtitle_path),
        filename=subtitle_filename,
        media_type="text/plain"
    )

@app.get("/api/styles")
async def get_default_styles():
    """Get default styling options"""
    return {
        "font_sizes": [16, 20, 24, 28, 32, 36, 40, 44, 48],
        "font_colors": ["white", "black", "yellow", "red", "blue", "green", "orange", "purple"],
        "highlight_colors": ["yellow", "orange", "red", "blue", "green", "purple", "pink"],
        "bottom_padding_range": {"min": 50, "max": 200, "default": 100},
        "default_font": "Bangers-Regular.ttf"
    }

@app.delete("/api/cleanup/{task_id}")
async def cleanup_task(task_id: str):
    """Clean up files for a completed task"""
    if task_id not in task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task_info = task_status[task_id]
    
    # Clean up files
    try:
        if "video_path" in task_info:
            video_path = Path(task_info["video_path"])
            if video_path.exists():
                video_path.unlink()
        
        if "output_video" in task_info:
            output_path = OUTPUT_DIR / task_info["output_video"]
            if output_path.exists():
                output_path.unlink()
        
        if "subtitle_file" in task_info:
            subtitle_path = OUTPUT_DIR / task_info["subtitle_file"]
            if subtitle_path.exists():
                subtitle_path.unlink()
        
        # Remove from memory
        del task_status[task_id]
        
        return {"message": "Task cleaned up successfully"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error cleaning up: {str(e)}")

# Catch-all route for React Router (must be last)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    """Serve React app for client-side routing"""
    # If it's an API route, let it pass through
    if full_path.startswith("api/"):
        raise HTTPException(status_code=404, detail="API endpoint not found")
    
    # If it's a static file request, try to serve it
    if full_path.startswith("static/"):
        static_file = STATIC_DIR / full_path
        if static_file.exists() and static_file.is_file():
            return FileResponse(str(static_file))
    
    # For all other routes, serve the React app
    if STATIC_DIR.exists() and (STATIC_DIR / "index.html").exists():
        return FileResponse(str(STATIC_DIR / "index.html"))
    
    return {"message": "Frontend not available", "path": full_path}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
