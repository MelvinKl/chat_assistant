FROM python:3.13 AS build

ARG DEV 0

WORKDIR /app/assistant

RUN pip install --upgrade pip
RUN pip install uv==0.10.0

COPY assistant .

RUN if [ "$DEV" = 1 ] ; then uv sync --dev ; else uv sync ; fi
RUN uv sync --dev

FROM python:3.13 

WORKDIR /app/assistant

COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /app/assistant/.venv /app/assistant/.venv

ENV PATH="/app/assistant/.venv/bin:$PATH"

COPY assistant .

ENV PYTHONPATH=/app/assistant/src

CMD [ "uv", "run", "uvicorn", "assistant.main:app", "--host", "0.0.0.0", "--port", "8080" ]
