FROM python:3.12-slim

RUN pip install poetry

ENV POETRY_NO_INTERATION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache

WORKDIR /app

COPY pyproject.toml poetry.lock ./

RUN poetry install --only=main --no-root && rm -rf ${POETRY_CACHE_DIR}

COPY app ./app

RUN poetry install --only-root

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]