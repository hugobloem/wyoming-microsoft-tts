ARG BUILD_FROM
FROM ${BUILD_FROM}
ARG BUILD_ARCH

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install Microsoft-tts
WORKDIR /usr/src

COPY setup.py ./pkg/
COPY requirements.txt ./pkg/
ADD ./wyoming-microsoft-tts ./pkg/wyoming-microsoft-tts

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        netcat-traditional \
        curl \
        python3 \
        python3-pip \
    && pip install --no-cache-dir \
        setuptools \
        wheel \
    && pip install ./pkg \
    && rm -rf /var/lib/apt/lists/*

# Copy files
WORKDIR /
COPY rootfs /

HEALTHCHECK --start-period=10m \
    CMD echo '{ "type": "describe" }' \
        | nc -w 1 localhost 10200 \
        | grep -q "microsoft" \
        || exit 1
