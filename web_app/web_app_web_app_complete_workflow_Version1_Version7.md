# Complete Workflow: Running LangGraph Web App via `web_app` (SQLite Cloud, Pinecone, LangGraph CLI, and Initialization)

---

## 1. Prerequisites

- Python (recommend using a virtual environment)
- Pinecone API credentials (for vector storage)
- SQLite Cloud connection string (for bookings DB)
- (Optional) Any other cloud storage or API keys required

---

## 2. Clone the Repository and Prepare the Environment

```bash
git clone https://github.com/g0agill/ai_agents_hotel_project.git
cd ai_agents_hotel_project/web_app
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Install LangGraph CLI

```bash
pip install --upgrade "langgraph-cli[inmem]"
```
_or, if you plan to use Docker deployment later:_
```bash
pip install -U langgraph-cli
```

---

## 4. Configure Environment Variables

Create a `.env` file in the `web_app` directory. Example:

```ini
# SQLite Cloud connection
SQLITE_CLOUD_URL=your-sqlite-cloud-connection-string

# Pinecone Vector Store
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENV=your-pinecone-environment
PINECONE_INDEX=your-pinecone-index

# OpenAI API Key (for LLM & embeddings)
OPENAI_API_KEY=your-openai-key
```

---

## 5. **Initialize Database and Vector Store FIRST (critical step!)**

**You must run the initialization script to create the database tables and vector store before starting any server or client!**

```bash
python hotel_reservation_mas.py
```

- This step sets up the SQLite Cloud schema and (if coded) initializes and populates Pinecone index.
- **Do not attempt to test, query, or interact with the DBs until this script runs successfully.**

---

## 6. Check and Edit `langgraph.json`

- Defines your assistants, tools, and integrations.
- Ensure the correct assistants (like `"hotel_reservation_mas"`) are present and referencing proper resources.
- The LangGraph server will read this file.

---

## 7. **How Memory Is Managed (Important!)**

- The code in `web_app` **explicitly uses persistent memory via `MemorySaver`**:
  ```python
  memory = MemorySaver()
  ...
  graph = builder.compile(checkpointer=memory)
  ```
- This means:
  - **All session/chat history is saved and restored across sessions and server restarts**, using the local storage backend of `MemorySaver`.
  - If you want to move to cloud-based persistent memory (e.g., LangGraph Cloud), you would use their memory client or deploy to the hosted platform.
- **If you run on LangGraph Cloud (the hosted platform):**
  - LangGraph Cloud can transparently provide persistent session memory, even if you use a local checkpointer in code.
- **If you run locally:**
  - Memory is as persistent as your local storage (wherever `MemorySaver` saves its state), but it's not cloud-backed unless you change the backend.

---

## 8. Start the LangGraph Server (Development Mode)

```bash
langgraph dev
```
- Must be run from the `web_app` directory (where `langgraph.json` is located).
- The server will read from `langgraph.json` and `.env`.
- The server runs by default on `http://localhost:8123` unless overridden.

---

## 9. Launch the Web Client

The Gradio web client is started as part of `hotel_reservation_mas.py` **when run as a script**.  
Or, you may run a separate `client_chat.py` or similar if provided.

Typical command (if not auto-launched):

```bash
python client_chat.py
```

- This launches a Gradio-based chat interface for user interaction.
- The Gradio client interacts with the local LangGraph server at `http://localhost:8123` (or other specified URL).

---

## 10. (Optional) Connect Local Server to LangSmith WebUI

- Copy your local server URL (e.g., `http://localhost:8123`)
- Go to [LangSmith Studio](https://smith.langchain.com/studio/)
- Connect your server with:
  ```
  https://smith.langchain.com/studio/baseUrl=http://localhost:8123
  ```

---

## 11. Troubleshooting

- **Database errors:** Make sure you ran `hotel_reservation_mas.py` to initialize the database/tables before starting the server or client.
- **Pinecone errors:** Verify API key, environment, and index name.
- **Assistant not found:** Check `langgraph.json` for correct definition.
- **Port issues:** Ensure nothing else is using port 8123.
- **WebUI connection:** Ensure the local server URL matches what you input to LangSmith Studio.
- **Persistent memory issues (local):** Verify where `MemorySaver` saves its state and that it's accessible/writable.
- **Persistent memory issues (cloud):** If you want full cloud persistence and multi-device support, deploy your app on LangGraph Cloud.

---

## **Summary Diagram**

1. `python hotel_reservation_mas.py` (**must be done first!** — initializes DB, tables, and vector store)  
2. `langgraph dev` (starts LangGraph server: reads `langgraph.json` + `.env`)  
3. `python client_chat.py` or auto-launched Gradio app (connects to `http://localhost:8123`)  
4. SQLite Cloud (via SQLAlchemy) and Pinecone vector store  
5. (Optional) LangSmith WebUI for visual interaction  
6. **Memory:**  
   - **Local/dev mode:** persistent via `MemorySaver` (local disk)  
   - **LangGraph Cloud:** persistent, automatic cloud-based memory if deployed there

---

**This workflow ensures you initialize your database and vector store using the correct script before starting the server and running clients.  
It also clarifies that chat/session memory is persistent via `MemorySaver` locally, and can be fully cloud-backed if you use LangGraph Cloud deployment.**