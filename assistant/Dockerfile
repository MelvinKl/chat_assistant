FROM python:3.13 AS build

ENV POETRY_VIRTUALENVS_PATH=/app/assistant/.venv
ARG DEV 0

WORKDIR /app/assistant

RUN python3 -m venv "${POETRY_VIRTUALENVS_PATH}"
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"

RUN pip install --upgrade pip
RUN pip install poetry

COPY assistant .

RUN poetry config virtualenvs.create false
RUN if [ "$DEV" = 1 ] ; then poetry install --with dev; else poetry install ; fi


FROM python:3.13 


ENV POETRY_VIRTUALENVS_PATH=/app/assistant/.venv
ENV PATH="${POETRY_VIRTUALENVS_PATH}/bin:$PATH"

COPY --from=build ${POETRY_VIRTUALENVS_PATH} ${POETRY_VIRTUALENVS_PATH}
COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/

WORKDIR /app/assistant

COPY assistant .

CMD [ "poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8080" ]
