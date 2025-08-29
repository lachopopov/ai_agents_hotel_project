# Complete Workflow: Running LangGraph Studio via `studio_cloud` (SQLite Cloud, Pinecone, Langgraph CLI, and Initialization)

---

## 1. Prerequisites

- Python (set up a virtual environment)
- Pinecone API credentials (for vector storage)
- (Optional) Any other cloud storage or API keys needed by your assistants

---

## 2. Clone the Repository and Prepare the Environment

```bash
git clone https://github.com/g0agill/ai_agents_hotel_project.git
cd ai_agents_hotel_project/studio_cloud
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 3. Install LangGraph CLI (In-Memory Version)

```bash
pip install --upgrade "langgraph-cli[inmem]"
```

---

## 4. Configure Environment Variables

Create a `.env` file in the `studio_cloud` directory. Example:

```ini
# SQLite Cloud connection (the path could be a cloud mount or local file)
SQLITE_CLOUD_URL=your-sqlite-cloud-connection-string

# Pinecone Vector Store
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENV=your-pinecone-environment
PINECONE_INDEX=your-pinecone-index
```

---

## 5. **Initialize Database and Vector Store FIRST (do this before any testing or server start!)**

**You must run the initialization script to create the databases and tables before you do any testing or start the LangGraph server.**

```bash
python hotel_reservation_mas.py
```

- This script creates the SQLite Cloud database/tables and initializes the Pinecone index.
- Do **not** attempt to test, query, or interact with the DBs until this script runs successfully.

---

## 6. Check and Edit `langgraph.json`

- Defines your assistants, tools, and integrations.
- Ensure the correct assistants (like `"hotel_reservation_mas"`) are present with correct resource references.
- The dev server will read this file to set up your app.

---

## 7. **How Memory Is Managed (Important!)**

- **No explicit memory backend** is set in code (`MemorySaver`, `MemoryClient`, etc. are NOT used in `studio_cloud`).
- However, **if you run your agents on LangGraph Cloud (the hosted platform, not just locally)**, LangGraph Cloud **automatically provides persistent conversation memory by default**—your session and chat state are stored in the cloud, even if you don't configure this in code!
  - This means session continuity, multi-turn memory, and persistent chat history are maintained for you by the platform.
- **If you run locally (`langgraph dev`)**, memory is ephemeral and only lasts for the session; nothing is stored persistently unless you add a checkpointer.

---

## 8. Start the LangGraph Server (Development Mode, In-Memory)

From the `studio_cloud` directory (must contain `langgraph.json`):

```bash
langgraph dev
```

- This will launch the LangGraph server (default: http://localhost:8123 unless overridden).
- It will read from `langgraph.json` and `.env`.

---

## 9. (Optional) Connect Local Server to LangSmith WebUI

- Copy your local server URL (e.g., `http://localhost:8123`)
- Go to [LangSmith Studio](https://smith.langchain.com/studio/)
- Connect your server with:
  ```
  https://smith.langchain.com/studio/baseUrl=http://localhost:8123
  ```

---

## 10. Run the Client Notebook

Open `client_app.ipynb` and run the cells:
```python
client = get_client(url="http://localhost:8123")
# ... rest of the notebook code
```
- The notebook will interact with your assistants, which in turn use SQLite Cloud and Pinecone as configured.

---

## 11. Troubleshooting

- **Database errors:** Make sure you ran `hotel_reservation_mas.py` to initialize the database/tables before starting the server.
- **Pinecone errors:** Verify API key, environment, and index name.
- **Assistant not found:** Check `langgraph.json` for correct definition.
- **Port issues:** Make sure nothing else is using port 8123.
- **WebUI connection:** Ensure the local server is running and the URL matches what you share with LangSmith Studio.
- **Memory/session issues:** If you need persistent memory, deploy to LangGraph Cloud or implement a checkpointer in your code.

---

## **Summary Diagram**

1. `python hotel_reservation_mas.py` (initialize DB and vector store — **must be done first!**)  
2. `langgraph dev` (LangGraph Studio: reads `langgraph.json` + `.env`)  
3. `client_app.ipynb` (connects to http://localhost:8123)  
4. SQLite Cloud (via SQLAlchemy) and Pinecone vector store  
5. (Optional) LangSmith WebUI for visual interaction  
6. **Memory:**  
   - **Local/dev mode:** ephemeral in-process memory only  
   - **LangGraph Cloud:** persistent, automatic cloud-based memory (no code changes needed)

---

**This workflow ensures you initialize your databases and vector stores using the correct initialization script before starting the server and running clients—matching the actual project requirements.  
It also clarifies that session/chat memory is managed by LangGraph Cloud by default when using their cloud platform, even if you do not configure this explicitly in your code.**