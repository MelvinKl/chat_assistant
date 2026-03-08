FROM python:3.14 AS build

ARG DEV 0

WORKDIR /app/assistant

RUN pip install --upgrade pip
RUN pip install uv

COPY assistant .

RUN if [ "$DEV" = 1 ] ; then uv sync --extra dev; else uv sync; fi


FROM python:3.14 

WORKDIR /app/assistant

COPY --from=build /app/assistant/.venv /app/assistant/.venv
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

ENV PATH="/app/assistant/.venv/bin:$PATH"

COPY assistant .

ENV PYTHONPATH=/app/assistant/src

CMD [ ".venv/bin/uvicorn", "assistant.main:app", "--host", "0.0.0.0", "--port", "8080" ]
