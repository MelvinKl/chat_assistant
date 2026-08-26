FROM python:3.13-slim

WORKDIR /app

COPY infrastructure/mock-mcp-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY infrastructure/mock-mcp-server/main.py .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
