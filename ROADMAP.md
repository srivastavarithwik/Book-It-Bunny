# Book-It-Bunny: How to Move Forward

You’re past **Phase 1**: Yelp search via MCP, LangGraph Researcher node, and a frontend. Here’s a clear path to the full agentic system in the spec.

---

## Where you are now

- **Tools (MCP):** `search_restaurants` → Yelp API ✓  
- **Orchestration:** One-shot graph: `search_params` → Researcher → `search_results` ✓  
- **Frontend:** Form → POST /api/search → display results ✓  
- **Missing:** No LLM in the loop, no real “conversation,” no booking, no error handling.

---

## Recommended order of work

### Step 1: Put the LLM in the loop (conversation + ReAct)

**Goal:** User talks in natural language; the agent decides when to search and what to do next.

- **State:** You already have `messages` in `AgentState`; use it. Add or keep `search_results` and `user_selection`.
- **Flow:**  
  - **Router / ReAct node:** LLM (OpenAI) reads `messages`, has access to **tools** (e.g. “search_restaurants” via MCP). It can either call the search tool (through your MCP client) or respond to the user.  
  - **Tool execution:** When the LLM asks to call `search_restaurants`, your graph runs the Researcher (or a generic “execute MCP tool” node), then returns tool output into state and loops back to the LLM.
- **Implementation options:**  
  - **Option A:** One “agent” node: bind MCP tools as LangChain tools, use `create_react_agent` (or a small ReAct loop) inside that node; the node calls the MCP client when the LLM requests a tool.  
  - **Option B:** Keep a dedicated Researcher node for search, and add an “assistant” node that uses the LLM to (1) interpret the last user message, (2) decide “call Researcher” vs “reply”. Use conditional edges: e.g. `assistant → researcher` if “search”, else `assistant → END` with a reply.
- **API:** Change from “single POST /api/search” to a **session-based chat**: e.g. `POST /api/chat` with `{ "message": "Find romantic Italian in Boston for 4" }` and optional `session_id`. Return assistant message(s) and updated state (e.g. `search_results` when a search was run).
- **Frontend:** Replace or augment the form with a **chat UI**: user types a message, sends to `/api/chat`, displays assistant reply and, when relevant, the list of restaurants (from state).

This gives you: **conversation flow**, **user preferences** in the thread, and **ReAct-style** “think → act (search) → respond.”

---

### Step 2: Persist state per session (stateful graph)

**Goal:** Multi-turn conversations and “book the second one” without re-searching.

- **Checkpointing:** Use LangGraph’s checkpointer (e.g. in-memory or Redis) keyed by `session_id` so each request restores the graph state for that session.
- **API:** When the frontend sends `session_id`, the backend loads the graph state for that session, runs the graph with the new message, then saves state again and returns the reply + any new `search_results` / `user_selection`.
- **Frontend:** Keep a `session_id` (from first response or a “new chat” button) and send it with every message.

This gives you the **stateful, cyclic graph** in the spec.

---

### Step 3: User selection and booking (Phase 2 – browser-use)

**Goal:** User can choose a restaurant and time; agent attempts to book via OpenTable/Resy.

- **State:** You already have `user_selection`; use it for “which restaurant” and “date/time/party size” (and optionally “which site”: OpenTable vs Resy).
- **MCP:** Add a second tool in `tools_server`, e.g. `attempt_reservation(restaurant_name, date, time, party_size, site="opentable" | "resy")`. Inside that tool, use **browser-use** (or a Playwright script) to open the site, search for the restaurant, select date/time/party, and try to complete the flow. Return success/failure and a short message (e.g. “Booked” or “No slots; try another time”).
- **Graph:** Add a **Booker** node (and optionally an “assistant” step to confirm with the user). After the user says “book the second one for Saturday 7pm,” the LLM (or a dedicated node) sets `user_selection` from the last `search_results` and chosen time; then the graph runs the Booker node, which calls the new MCP tool. On failure, you can loop back to the assistant for **error handling** (e.g. “That time’s full; here are other options”).
- **Frontend:** When results are shown, add “Book” (or “Select”) on each card; when the user selects one, send a message like “Book [Restaurant Name] for [date] at [time] for [party_size]” so the agent has clear intent.

This delivers **automation** and **error handling (e.g. restaurant full)** from the spec.

---

### Step 4: Polish and scale

- **Error handling:** In the graph, handle “restaurant full,” “no results,” “booking failed” with clear LLM replies and, where useful, suggested next actions.
- **User preferences:** Optionally store dietary restrictions, preferred areas, etc., in state or a small DB and feed them into the LLM context.
- **FastAPI:** You already expose the agent; add auth, rate limits, and (if needed) async job queue for long-running booking attempts.
- **Frontend:** Refine chat UI, show “agent is typing” / “agent is searching” / “agent is booking,” and display structured data (restaurant cards, booking confirmation) cleanly.

---

## Summary

| Step | What you add | Outcome |
|------|----------------|--------|
| **1** | LLM + ReAct (tools = MCP search), session chat API + chat UI | Natural-language search and conversation |
| **2** | Checkpointer, session_id in API and frontend | Stateful, multi-turn flow |
| **3** | MCP booking tool (browser-use), Booker node, user_selection + “Book” in UI | End-to-end discovery + booking |
| **4** | Error handling, preferences, auth, UX polish | Production-ready agent |

If you tell me which step you want to do first (e.g. “Step 1: LLM + chat”), I can outline concrete file changes and code snippets next.
