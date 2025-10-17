"""Main FastAPI application for YouTube to Doc MVP."""

from pathlib import Path
from typing import Dict

from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from starlette.responses import Response

from .processor import process_youtube_video

# Initialize FastAPI app
app = FastAPI(title="YouTube to Doc MVP")

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

# Setup templates
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    """Handle rate limit exceptions."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "error_message": "Rate limit exceeded. Please try again later.",
            "result": False,
        },
        status_code=429,
    )


@app.get("/health")
async def health_check() -> Dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    """Render the home page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "result": False,
        },
    )


@app.post("/", response_class=HTMLResponse)
@limiter.limit("10/minute")
async def process_video(request: Request, video_url: str = Form(...)) -> HTMLResponse:
    """Process a YouTube video and generate documentation."""
    context = {
        "request": request,
        "video_url": video_url,
        "result": False,
        "error_message": None,
        "content": None,
        "video_info": None,
    }

    try:
        # Process the video
        video_info, documentation = await process_youtube_video(video_url)
        
        context["video_info"] = video_info
        context["content"] = documentation
        context["result"] = True
        
    except Exception as e:
        context["error_message"] = f"Error processing video: {str(e)}"
        
        if "not available" in str(e).lower():
            context["error_message"] = (
                "Video not available. Please check that the video is public and the URL is correct."
            )
        elif "transcript" in str(e).lower():
            context["error_message"] = (
                "Transcript not available for this video. Try a different video or check if captions are enabled."
            )

    return templates.TemplateResponse("index.html", context)