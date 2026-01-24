# seaf-cli

[![Build workflow](https://github.com/docker-sstc/mono/actions/workflows/seaf-cli.yml/badge.svg)](https://github.com/docker-sstc/mono/actions)
[![Docker pulls](https://img.shields.io/docker/pulls/sstc/seaf-cli.svg)](https://hub.docker.com/r/sstc/seaf-cli)

## Usage

```sh
mkdir -p ~/seafile-client
nano ~/seafile-client/config.json
# {
#   "debug": false, // it will print commands
#   "username": null, // required
#   "password": null, // required
#   "server_url": "", // required, if the server on the same host, try --net=host and set it to http://0.0.0.0:<port> instead
#   "totp_secret": null,
#   "seafile": {
#     "disable_verify_certificate": false,
#     "download_limit": null,
#     "upload_limit": null
#   },
#   "dirs": [
#     {
#       "uuid": "...",
#       "path": "/app/sync_me", // path in container
#       "password": null
#     }
#   ]
# }
docker run -d \
  --name seaf-cli \
  -v ~/seafile-client:/seafile-client \
  -v ~/sync_me:/app/sync_me \
  sstc/seaf-cli

# server on same host, could try
docker run -d \
  --name seaf-cli \
  --net=host \
  -v ~/seafile-client:/seafile-client \
  -v ~/sync_me:/app/sync_me \
  sstc/seaf-cli
```

Following ENVs can override attributes in config.json

```conf
DEBUG=1
USERNAME=username
PASSWORD=password
SERVER_URL=
TOTP_SECRET=
SEAFILE_DISABLE_VERIFY_CERTIFICATE=1
SEAFILE_DOWNLOAD_LIMIT=1000000
SEAFILE_UPLOAD_LIMIT=1000000
```

## Q&A

### urllib.error.HTTPError: HTTP Error 400: Bad Request

Possible issues

- Not enable 2fa, but set totp_secret
- totp_secret is wrong, forgot updating when reenable 2fa

try `docker exec -it seaf-cli /bin/bash` and make sure the command (e.q. `seaf-cli list-remote ...`) works

## Dev memo

```bash
# test
docker build -t seaf-cli . --no-cache

# run
docker run --rm -it --net=host -v /root/seafile-client:/seafile-client seaf-cli

# debug
docker run --rm -it --net=host -v /root/seafile-client:/seafile-client --entrypoint=/bin/bash seaf-cli
# in container
apt update
apt install -y nano procps ntpdate
nano /bin/seaf-cli
/entrypoint.sh
```

## TODO

- hard link log files to stdout: `ln -sf /proc/self/fd/1 /var/log/app.log`
