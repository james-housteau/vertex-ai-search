"""Entry point for running the search API service."""

import os

import uvicorn

from search_api.api import app

if __name__ == "__main__":
    host = os.environ["HOST"]
    port = int(os.environ["PORT"])
    uvicorn.run(app, host=host, port=port)
