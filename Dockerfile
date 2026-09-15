FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .

RUN pip install --no-cache-dir --upgrade pip

COPY . .

RUN pip install --no-cache-dir -e ".[dev]"

CMD ["python", "src/ingestion/main.py"]