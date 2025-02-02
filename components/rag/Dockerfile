FROM python:3.13 

ARG DEV 0

WORKDIR /app

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install poetry
COPY components/. /app/

WORKDIR /app/rag

# RUN poetry lock --no-update

RUN if [ "$DEV" = 1 ] ; then poetry install --no-root --with dev; else poetry install --no-root; fi

CMD [ "poetry", "run", "uvicorn", "src.main:component_app", "--host", "0.0.0.0", "--port", "8080" ]
