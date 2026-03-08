FROM python:3.11 

ARG DEV 0

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install uv

COPY components/. /app/

WORKDIR /app/home-assistant

RUN if [ "$DEV" = 1 ] ; then uv sync --extra dev; else uv sync; fi

CMD [ ".venv/bin/uvicorn", "src.main:component_app", "--host", "0.0.0.0", "--port", "8080" ]
