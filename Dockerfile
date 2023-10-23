ARG BUILD_FROM
FROM ${BUILD_FROM}
ARG BUILD_ARCH

# Install Microsoft-tts
WORKDIR /usr/src
#ENV PIP_BREAK_SYSTEM_PACKAGES=1

SHELL ["/bin/bash", "-o", "pipefail", "-c"]


# COPY requirements.txt ./
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
#     && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# Copy files
WORKDIR /
COPY rootfs /
ADD wyoming-microsoft-tts ./
# COPY run.sh /
# RUN chmod 770 /run.sh

# EXPOSE 10200

HEALTHCHECK --start-period=10m \
    CMD echo '{ "type": "describe" }' \
        | nc -w 1 localhost 10200 \
        | grep -q "microsoft" \
        || exit 1
