# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.13
ARG NODE_VERSION=22
ARG UV_VERSION=0.11.11

FROM ghcr.io/astral-sh/uv:${UV_VERSION} AS uv

FROM python:${PYTHON_VERSION}-slim AS backend-dependencies

COPY --from=uv /uv /uvx /bin/

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/opt/venv

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/pyproject.toml backend/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project


FROM backend-dependencies AS backend-runtime

COPY backend/ ./

RUN groupadd --system openmeet \
    && useradd --system --gid openmeet --home-dir /app openmeet \
    && chown -R openmeet:openmeet /app

ENV PATH="/opt/venv/bin:${PATH}"

USER openmeet

EXPOSE 8000

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]


FROM node:${NODE_VERSION}-alpine AS frontend-dependencies

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --ignore-scripts


FROM frontend-dependencies AS frontend-build

COPY frontend/ ./
RUN npm run prepare && npm run build


FROM node:${NODE_VERSION}-alpine AS frontend-runtime

WORKDIR /app

ENV NODE_ENV=production \
    HOST=0.0.0.0 \
    PORT=3000

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci --omit=dev --ignore-scripts \
    && npm cache clean --force

COPY --from=frontend-build --chown=node:node /app/build ./build

USER node

EXPOSE 3000

CMD ["node", "build/index.js"]
