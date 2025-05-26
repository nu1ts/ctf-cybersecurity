FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

RUN curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/root/.local/bin:$PATH"

WORKDIR /app

COPY pyproject.toml poetry.lock* /app/

RUN poetry config virtualenvs.create false \
    && poetry install --no-root --only main

COPY backend/ /app/backend/

COPY frontend/ /app/frontend/

WORKDIR /app/frontend

RUN npm install

RUN npm run build

RUN mkdir -p /app/backend/static
RUN cp -r /app/frontend/build/* /app/backend/static/

WORKDIR /app

EXPOSE 8000

CMD ["gunicorn", "todo_api.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]