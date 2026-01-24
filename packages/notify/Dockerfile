ARG ALPINE_VERSION
FROM alpine:${ALPINE_VERSION}

ENV TELEGRAM_SH_SRC_URL=https://raw.githubusercontent.com/up9cloud/telegram-bot-send.sh/master/tg.ash \
	SLACK_SH_SRC_URL=https://raw.githubusercontent.com/rockymadden/slack-cli/master/src/slack \
	DISCORD_SH_SRC_URL=https://raw.githubusercontent.com/ChaoticWeg/discord.sh/master/discord.sh

RUN apk add --no-cache \
	bash \
	curl \
	jq \
	gettext

RUN set -e; \
	wget ${TELEGRAM_SH_SRC_URL} -O /usr/local/bin/tg.ash; \
	chmod +x /usr/local/bin/tg.ash; \
	ln -s /usr/local/bin/tg.ash /usr/local/bin/tg; \
	wget ${SLACK_SH_SRC_URL} -O /usr/local/bin/slack; \
	chmod +x /usr/local/bin/slack; \
	wget ${DISCORD_SH_SRC_URL} -O /usr/local/bin/discord.sh; \
	chmod +x /usr/local/bin/discord.sh; \
	ln -s /usr/local/bin/discord.sh /usr/local/bin/discord

VOLUME /app
WORKDIR /app
CMD ["bash"]
