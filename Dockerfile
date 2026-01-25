FROM python:3.13-slim

# Install nginx + certs
RUN apt-get update \
  && apt-get install -y --no-install-recommends nginx ca-certificates \
  && rm -rf /var/lib/apt/lists/*

# Remove default nginx site to avoid conflicts with our conf.d/default.conf
RUN rm -f /etc/nginx/sites-enabled/default || true

WORKDIR /app

# Install uv
RUN pip install --no-cache-dir uv

# Copy project metadata first (better caching)
COPY pyproject.toml /app/pyproject.toml
COPY uv.lock /app/uv.lock

# Install dependencies from the lock file (creates /app/.venv)
RUN uv sync --frozen

# Copy app code
COPY . /app

# Configure nginx default site
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

ENV PATH="/app/.venv/bin:$PATH"

CMD ["/bin/sh", "/app/start.sh"]