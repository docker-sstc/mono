ARG ALPINE_VERSION
FROM alpine:${ALPINE_VERSION}

RUN apk add --no-cache \
	rsync \
	openssh-client \
	sshpass

WORKDIR /app
ENTRYPOINT ["rsync"]
