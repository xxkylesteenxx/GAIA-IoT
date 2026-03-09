FROM python:3.12-slim

LABEL maintainer="xxkylesteenxx"
LABEL description="GAIA IoT Edge Node"

WORKDIR /app

# Install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY . .
RUN pip install --no-cache-dir -e .

# State directory
RUN mkdir -p /gaia-state
ENV GAIA_STATE_ROOT=/gaia-state
ENV GAIA_NODE_ID=gaia-iot-edge

EXPOSE 8080

CMD ["python", "-m", "gaia_iot.entrypoint"]
