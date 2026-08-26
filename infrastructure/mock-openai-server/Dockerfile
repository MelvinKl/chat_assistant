FROM python:3.13-slim

WORKDIR /app

COPY infrastructure/mock-openai-server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY infrastructure/mock-openai-server/main.py .

EXPOSE 11434

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "11434"]
