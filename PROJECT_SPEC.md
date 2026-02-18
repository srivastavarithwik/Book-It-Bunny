Project Brief: Book-It-Bunny
Objective: A high-end AI agentic system for restaurant discovery and automated booking, built with a decoupled, scalable architecture.

1. Architectural Strategy
Orchestration Layer (The Brain): LangGraph. We are using a stateful, cyclic graph to manage the conversation flow, user preferences, and error handling (e.g., if a restaurant is full).

Tooling Layer (The Body): MCP (Model Context Protocol) Server. All external interactions (Yelp API for search and Browser-use for booking) must be encapsulated in a separate MCP server.

Interaction Logic: ReAct pattern within specific Graph nodes.

Automation: browser-use for navigating reservation sites (OpenTable/Resy) when no API is available.

2. The Tech Stack
Language: Python 3.11+

Agent Framework: langgraph, langchain-openai

Tooling Protocol: mcp (Python SDK)

APIs: Yelp Fusion (Search), OpenAI/Anthropic (LLM)

Automation: playwright, browser-use

Backend/API: FastAPI (to expose the agent to a frontend later)

Phase 1: Day 1 "Melt the Ice" Sprint
Goal: Establish the MCP connection between the LangGraph backend and a "Search Tool" that hits the Yelp API.

Initial Task List for Cursor:
Project Structure: Create a directory layout separating /mcp_server (tools) and /agent_backend (logic).

MCP Server Setup:

Initialize a basic MCP server using the Python SDK.

Implement a search_restaurants tool that takes location, cuisine, and party_size.

Hardcode a mock response first, then integrate the real Yelp Fusion API client.

Agent Backend Setup:

Initialize a LangGraph state machine.

Define a State TypedDict to track messages, search_results, and user_selection.

Create a "Researcher" node that connects to the MCP server via stdio transport to call the search tool.

Environment: Create a .env file template for OPENAI_API_KEY and YELP_API_KEY.