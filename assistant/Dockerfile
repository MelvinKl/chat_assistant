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
# These measures are applied after application code is copied
RUN if [ "$DEV" = 0 ]; then \
    echo "Applying production security hardening..."; \
    # Ensure application files have secure permissions \
    find /app/assistant -type f -exec chmod 644 {} \; 2>/dev/null || true; \
    find /app/assistant -type d -exec chmod 755 {} \; 2>/dev/null || true; \
    # Remove SUID/SGID bits from executables for security \
    find /app/assistant -type f -perm /4000 -exec chmod a-s {} \; 2>/dev/null || true; \
    find /app/assistant -type f -perm /2000 -exec chmod a-s {} \; 2>/dev/null || true; \
    # Set umask to restrict default permissions for newly created files \
    echo "umask 022" > /etc/profile.d/umask.sh && \
    chmod +x /etc/profile.d/umask.sh && \
    # Ensure temporary directories have safe permissions \
    chmod 1777 /tmp /var/tmp 2>/dev/null || true; \
    # Remove any unnecessary users and groups (keep only essential ones) \
    delgroup -r audio video dialout floppy tape 2>/dev/null || true; \
    fi

# Security hardening for production: drop capabilities, restrict syscalls, etc.
# These will be implemented via Kubernetes security context in Helm chart
CMD [ "uv", "run", "uvicorn", "assistant.main:app", "--host", "0.0.0.0", "--port", "8080" ]
