# hotel_errors_handling/hotel_errors_handling/README.md

# Hotel Errors Handling Project

This project is designed to handle edge cases and errors in a hotel management system using Python. It utilizes the LangChain framework to manage various models and error handling mechanisms effectively.

## Project Structure

```
hotel_errors_handling
├── src
│   ├── __init__.py
│   ├── config
│   │   ├── __init__.py
│   │   └── dependencies.py
│   ├── utils
│   │   ├── __init__.py
│   │   └── setup.py
│   ├── models
│   │   ├── __init__.py
│   │   └── langchain_models.py
│   └── handlers
│       ├── __init__.py
│       └── error_handlers.py
├── requirements.txt
├── setup.py
└── README.md
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