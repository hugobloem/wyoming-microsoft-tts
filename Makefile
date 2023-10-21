.PHONY: local run update

VERSION := 1.0.0
TAG := hugobloem/wyoming-microsoft-tts
PLATFORMS := linux/amd64,linux/arm64,linux/arm/v7
VOICE := en_GB-SoniaNeural
HOST := 0.0.0.0
PORT := 10200

all:
	docker buildx build . --platform "$(PLATFORMS)" --tag "$(TAG):$(VERSION)" --push

update:
	docker buildx build . --platform "$(PLATFORMS)" --tag "$(TAG):latest" --push

local:
	docker build . -t "$(TAG):$(VERSION)" --build-arg TARGETARCH=linux/arm64

run:
	docker run -it -p '$(PORT):$(PORT)'  "$(TAG):$(VERSION)" --voice "$(VOICE)" --uri 'tcp://$(HOST):$(PORT)' --debug