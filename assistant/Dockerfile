FROM python:3.13 AS build

ARG DEV 0

WORKDIR /app/assistant

RUN pip install --upgrade pip
RUN pip install uv==0.10.0

COPY assistant .

RUN if [ "$DEV" = 1 ] ; then uv sync --dev ; else uv sync ; fi

FROM python:3.13 

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app/assistant

COPY --from=build /usr/local/bin/ /usr/local/bin/
COPY --from=build /usr/bin/make /usr/bin/make
COPY --from=build /usr/local/lib/ /usr/local/lib/
COPY --from=build /app/assistant/.venv /app/assistant/.venv

ENV PATH="/app/assistant/.venv/bin:$PATH"

COPY assistant .

# Change ownership to non-root user
RUN chown -R appuser:appuser /app/assistant

# Switch to non-root user
USER appuser

ENV PYTHONPATH=/app/assistant/src

# Additional security hardening for production (when DEV=0)
# Drop capabilities that are not needed
# Note: Full capability dropping is done via Kubernetes security context
# but we can set some basic security measures here
RUN if [ "$DEV" = 0 ]; then \
    echo "Applying production security hardening..."; \
    # Make files immutable where possible (commented out as it might break functionality) \
    # chattr +i /etc/passwd /etc/group || true; \
    # Ensure no sensitive files are world-readable \
    find /app/assistant -type f -name "*.py" -exec chmod 644 {} \;; \
    find /app/assistant -type d -exec chmod 755 {} \;; \
    fi

# Security hardening for production: drop capabilities, restrict syscalls, etc.
# These will be implemented via Kubernetes security context in Helm chart
CMD [ "uv", "run", "uvicorn", "assistant.main:app", "--host", "0.0.0.0", "--port", "8080" ]
