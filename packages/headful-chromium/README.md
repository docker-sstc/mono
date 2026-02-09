# headful-chromium

[![Build workflow](https://github.com/docker-sstc/mono/actions/workflows/headful-chromium.yml/badge.svg)](https://github.com/docker-sstc/mono/actions)
[![Docker pulls](https://img.shields.io/docker/pulls/sstc/headful-chromium.svg)](https://hub.docker.com/r/sstc/headful-chromium)

## Usage

### 1. Link Playwright Into Your Local Project

To use the globally installed Playwright inside your project, link it using:

```bash
docker run --rm \
  -v $(pwd):/app \
  -w /app \
  sstc/headful-chromium \
  npm link playwright
```

### 2. Running Automation Tasks

You can run everything in a single container, or split responsibilities

#### Option A: Launch Browser & Run Tasks (Standalone mode)

This will start a browser and immediately run your automation script in the same container:

```bash
docker run --rm \
  --init \
  --ipc=host \
  --privileged \
  -v $(pwd):/app \
  -w /app \
  sstc/headful-chromium \
  ./example-entrypoint.sh node example-standalone.mjs
```

#### Option B: Start Browser Server and Connect Remotely (Server-client mode)

**Step 1:** Start the browser server in a dedicated container:

```bash
docker run --rm \
  --init \
  --ipc=host \
  --name server \
  -p 3000:3000 \
  -v $(pwd):/app \
  -w /app \
  sstc/headful-chromium \
  ./example-entrypoint.sh node example-server.mjs
# If the client is running on a different host than the server, you may need to forward the debugging port using:
# socat TCP-LISTEN:9222,fork,reuseaddr TCP:127.0.0.1:9222
```

**Step 2:** In another terminal/process/container, connect to the running browser server and execute your automation:

```bash
docker run --rm \
  --net host \
  -v $(pwd):/app \
  -w /app \
  sstc/headful-chromium \
  node example-client.mjs
```

## Refs

- Debian versions: https://www.debian.org/releases/
- Ubuntu versions: https://ubuntu.com/about/release-cycle
- Playwright versions: https://github.com/microsoft/playwright/releases
- Playwright docker build files: https://github.com/microsoft/playwright/tree/main/utils/docker
- Playwright docker image tags: https://mcr.microsoft.com/en-us/artifact/mar/playwright/tags
- Playwright connect to remote: https://playwright.dev/docs/docker#remote-connection
- headful commands: https://github.com/MauFournier/puppeteer-headful-with-commands
- Dbus: https://github.com/microsoft/WSL/issues/7915#issuecomment-1163333151

  ```bash
  apt update
  apt install -y notification-daemon
  apt install -y upower
  export DBUS_SESSION_BUS_ADDRESS=unix:path=/run/dbus/system_bus_socket
  export RUNLEVEL=1
  dbus-daemon --session --address=$DBUS_SESSION_BUS_ADDRESS --nofork --nopidfile --syslog-only &
  # service dbus start

  cat << EOF >> /usr/share/dbus-1/services/org.freedesktop.Notifications.service
  [D-BUS Service]
  Name=org.freedesktop.Notifications
  Exec=/usr/lib/notification-daemon/notification-daemon
  EOF

  cat << EOF >> /usr/sbin/policy-rc.d
  #!/bin/sh
  exit 0
  EOF
  ```

- Local test:

  ```bash
  docker build -f debian-12/Dockerfile -t test --build-arg PLAYWRIGHT_VERSION=1.53.1 --progress=plain --no-cache .
  docker run -it --ipc=host -v $(pwd):/app -w /app test /bin/bash
  docker run -v $(pwd):/app -w /app test ./example-entrypoint.sh node example-standalone.mjs
  ```

  ```bash
  node --version
  npm --version
  chromium --version
  ```
