FROM python:3.13 

ARG DEV 0

WORKDIR /app

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install poetry

COPY components/base-library /app/components/base-library
COPY assistant /app/assistant

WORKDIR /app/assistant

RUN if [ "$DEV" = 1 ] ; then poetry install --with dev; else poetry install ; fi
RUN poetry add mcp-timeserver

CMD [ "poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080" ]
