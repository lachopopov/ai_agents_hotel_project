# Building Multi-agent AI system for Hotel Reservations (Week 4)

This project is a part of Building Multi-agent AI system for Hotel Reservations Course (week 4).

The main goal of this project is to learn LangGraph Server, LangSmith, Gradio and Docker for deployement of multi-agent systems developed using LangGraph framework.

## Project Structure

```
ai_agents_hotel_project
├── studio
│   ├── .env_example
│   ├── hotel_reservation_mas.py
│   ├── langgraph.json
│   ├── requirements.txt
├── studio_cloud
│   ├── .env_example
│   ├── hotel_reservation_mas.py
│   ├── db.py
│   ├── vector_db.py
│   ├── client_app.ipynb
│   ├── langgraph.json
│   ├── requirements.txt
├── web_app
│   ├── .env_example
│   ├── hotel_reservation_mas.py
│   ├── db.py
│   ├── vector_db.py
│   ├── langgraph.json
│   ├── requirements.txt
└── container_app
│   ├── .env_example
│   ├── .DockerFile
│   ├── docker-compose.yml
│   ├── hotel_reservation_mas.py
│   ├── db.py
│   ├── vector_db.py
│   ├── client_chat.py
│   ├── langgraph.json
│   ├── requirements.txt
```

## Langgraph Server from the terminal (Sessions 2 & 3)

First, install Langgraph CLI (in memory):

```
pip install pip install --upgrade "langgraph-cli[inmem]"
```

And after that start the server in the directory with langgraph.json:

```
langgraph dev
```

After that you can connect your server to the WebUI in Langsmith with the link: https://smith.langchain.com/studio/baseUrl=<URL_OF_YOUR_LOCAL_SERVER>

## Langgraph Server from the terminal (Session 5)

First, install Langgraph CLI:

```
pip install -U langgraph-cli
```

After that build a docker image of the langgraph server:

```
langgraph build -t langgraph-server
```

After that build and launch your container app with:

```
docker compose up
```