"""Main entry point for the OpenMeets backend."""

import uvicorn
from contextlib import asynccontextmanager

from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter

from app import graphql_router
from database import async_engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await async_engine.dispose()


app = FastAPI(
    title="OpenMeets API",
    description="GraphQL API for OpenMeets event management platform",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(graphql_router, prefix="/graphql")


@app.get("/")
async def root():
    return {"message": "Welcome to OpenMeets GraphQL API"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


def main():
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )


if __name__ == "__main__":
    main()