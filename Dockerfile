FROM python:3.13-slim

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1

WORKDIR /app

COPY pyproject.toml ./
COPY README.md /app/

# Configure poetry to create venv in project and install dependencies
RUN poetry config virtualenvs.in-project true && \
    poetry lock && \
    poetry install --no-root

COPY app ./app

RUN poetry install --only-root

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]