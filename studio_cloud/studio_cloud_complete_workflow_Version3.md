# Complete Workflow: Running LangGraph Studio via `studio_cloud` (Non-containerized, SQLite Cloud)

This workflow provides a comprehensive, step-by-step process for running your LangGraph app locally using the `studio_cloud` folder. It covers environment setup, SQLite Cloud, Pinecone, Langgraph CLI, and integration with the LangSmith WebUI.

---

## 1. Prerequisites

- Python (use a virtual environment for isolation)
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
SQLALCHEMY_DATABASE_URI=sqlite+aiosqlite:///absolute/or/cloud/path/to/your.db

# Pinecone Vector Store
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENV=your-pinecone-environment
PINECONE_INDEX=your-pinecone-index
```

- The `SQLALCHEMY_DATABASE_URI` should begin with `sqlite+aiosqlite://` for SQLite (cloud path if applicable).
- Make sure any other environment variables used in your code or `langgraph.json` are included here.

---

## 5. Check and Edit `langgraph.json`

- This file defines your assistants, tools, and integrations.
- Ensure assistants (like `"hotel_reservation_mas"`) and any tools referencing SQL or Pinecone are properly configured.
- The dev server will read this file to know how to set up your app.

---

## 6. (Optional) Test Database and Pinecone Connections

```python name=test_connections.py
import os
import sqlite3
import pinecone

# Test SQLite
db_path = os.environ["SQLALCHEMY_DATABASE_URI"].replace("sqlite+aiosqlite:///", "")
conn = sqlite3.connect(db_path)
print("SQLite tables:", conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())
conn.close()

# Test Pinecone
pinecone.init(api_key=os.environ["PINECONE_API_KEY"], environment=os.environ["PINECONE_ENV"])
index = pinecone.Index(os.environ["PINECONE_INDEX"])
print("Pinecone stats:", index.describe_index_stats())
```
Run with:
```bash
python test_connections.py
```

---

## 7. Start the LangGraph Server (Development Mode, In-Memory)

From the `studio_cloud` directory (must contain `langgraph.json`):

```bash
langgraph dev
```

This will:
- Launch the LangGraph server locally (default: http://localhost:8123 unless overridden).
- Read configuration from `langgraph.json` and `.env`.
- Make all your assistants, tools, and resource connections available.

---

## 8. (Optional) Connect Local Server to LangSmith WebUI

- Copy your local server URL (e.g., `http://localhost:8123`)
- Go to [LangSmith Studio](https://smith.langchain.com/studio/)
- Connect your server using the following pattern in your browser:
  ```
  https://smith.langchain.com/studio/baseUrl=<URL_OF_YOUR_LOCAL_SERVER>
  ```
  Example:
  ```
  https://smith.langchain.com/studio/baseUrl=http://localhost:8123
  ```

---

## 9. Run the Client Notebook

Open `client_app.ipynb` (or your client script) and run the cells:
```python
client = get_client(url="http://localhost:8123")
# ... rest of the notebook code
```
- The notebook will interact with your assistants, which in turn use SQLite Cloud and Pinecone as configured.

---

## 10. Troubleshooting

- **Database errors:** Double-check your `SQLALCHEMY_DATABASE_URI` and file path accessibility.
- **Pinecone errors:** Verify API key, environment, and index name.
- **Assistant not found:** Ensure your assistant is defined in `langgraph.json`.
- **Port issues:** Make sure nothing else is using port 8123.
- **WebUI connection:** Ensure the local server is running and the URL matches what you share with LangSmith Studio.

---

## **Summary Diagram**
1. `client_app.ipynb` →
2. LangGraph Studio (`langgraph.json` + `.env`) via `langgraph dev` →
3. SQLite Cloud (via SQLAlchemy) and Pinecone vector store
4. (Optional) LangSmith WebUI for visual interaction

---

**This complete workflow ensures your local (cloud-like) LangGraph app is set up to use SQLite Cloud and Pinecone, is accessible to notebooks, and can be easily integrated with LangSmith's WebUI for a full development experience.**