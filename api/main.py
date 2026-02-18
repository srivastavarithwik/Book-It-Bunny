"""
FastAPI app: exposes the Book-It-Bunny agent to the frontend.
Run from project root: uvicorn api.main:app --reload
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Load .env from project root before importing agent (so MCP subprocess gets keys)
_root = Path(__file__).resolve().parent.parent
_env = _root / ".env"
if _env.exists():
    from dotenv import load_dotenv
    load_dotenv(_env)

from agent_brain import get_compiled_graph

app = FastAPI(title="Book-It-Bunny API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class SearchRequest(BaseModel):
    location: str = "San Francisco, CA"
    cuisine: str = ""
    party_size: int = 2


class SearchResponse(BaseModel):
    search_results: list[dict]


@app.post("/api/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """Run the agent graph with the given search params and return restaurant results."""
    graph = get_compiled_graph()
    initial = {
        "messages": [],
        "search_params": {
            "location": request.location,
            "cuisine": request.cuisine,
            "party_size": request.party_size,
        },
    }
    result = await graph.ainvoke(initial)
    return SearchResponse(search_results=result.get("search_results") or [])


# Serve frontend static files (index.html, assets) at /
frontend_dir = _root / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
