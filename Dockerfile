FROM python:3.13-slim

RUN pip install poetry

ENV POETRY_NO_INTERACTION=1
ENV POETRY_VENV_IN_PROJECT=0

WORKDIR /app

COPY pyproject.toml ./
COPY README.md /app/

# Configure poetry to not create venv in project and install dependencies
RUN poetry config virtualenvs.create false && \
    poetry lock && \
    poetry install --no-root

COPY app ./app

RUN poetry install --only-root

# Remove the PATH modification since we're not using project venv
# ENV PATH="/app/.venv/bin:$PATH"

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]