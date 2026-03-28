FROM python:3.14 AS build

ARG DEV 0

WORKDIR /app/home-assistant

RUN pip install --upgrade pip
RUN pip install uv==0.10.0

COPY components/. /app/

WORKDIR /app/home-assistant

RUN if [ "$DEV" = 1 ] ; then uv sync --dev ; else uv sync ; fi


FROM python:3.14 

WORKDIR /app/home-assistant

COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /app/home-assistant/.venv /app/home-assistant/.venv

ENV PATH="/app/home-assistant/.venv/bin:$PATH"

COPY components/. /app/

WORKDIR /app/home-assistant

CMD [ "uv", "run", "uvicorn", "src.main:component_app", "--host", "0.0.0.0", "--port", "8080" ]
