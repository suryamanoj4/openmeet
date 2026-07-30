"""Main entry point for the OpenMeets backend."""

import uvicorn

from config import settings


def main():
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )


if __name__ == "__main__":
    main()
