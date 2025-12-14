FROM debian:12-slim

ENV PYTHONUNBUFFERED=1

RUN set -ex; \
	apt update; \
	apt install \
		--no-install-recommends \
		-y \
			seafile-cli \
			oathtool \
			ca-certificates \
			gnupg; \
	apt-get clean; \
	rm -rf /var/lib/apt/lists/*

COPY --chmod=755 src/entrypoint.py /entrypoint.py

VOLUME /seafile-client
WORKDIR /seafile-client
ENTRYPOINT ["/entrypoint.py"]
