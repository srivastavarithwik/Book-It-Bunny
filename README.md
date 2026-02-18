# Book-It-Bunny

An autonomous AI agent built with LangGraph and Browser-use that orchestrates restaurant discovery and automated reservation fulfillment.

## Run with frontend

From the project root (with `.env` and dependencies set up):

```bash
uvicorn api.main:app --reload
```

Then open **http://127.0.0.1:8000** in your browser. Use the form to search by location, optional cuisine, and party size; results come from the agent (MCP → Yelp).

## CLI (no frontend)

```bash
python -m agent_brain.run --location "Boston, MA" --cuisine Italian --party-size 2
```
