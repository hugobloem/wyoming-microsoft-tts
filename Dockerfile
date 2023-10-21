ARG BUILD_FROM
FROM ${BUILD_FROM}
ARG BUILD_ARCH

# Install Piper
WORKDIR /usr/src

COPY requirements.txt ./

RUN \
    apt-get update \
    && apt-get install -y --no-install-recommends \
        # curl \
        python3 \
        python3-pip \
    \
    && pip3 install --no-cache-dir \
        -r requirements.txt \
    \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /
ADD wyoming-microsoft-tts ./

EXPOSE 10200

# ENTRYPOINT ["bash", "/run.sh"]
ENTRYPOINT ["python3", "/__main__.py"]

# RUN apt-get update && \
#     apt-get install -y python3 python3-pip

# WORKDIR /app

# COPY . /app

# RUN pip3 install -r requirements.txt
