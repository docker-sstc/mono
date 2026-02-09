# android-ndk

[![Build workflow](https://github.com/docker-sstc/mono/actions/workflows/android-ndk.yml/badge.svg)](https://github.com/docker-sstc/mono/actions)
[![Docker pulls](https://img.shields.io/docker/pulls/sstc/android-ndk.svg)](https://hub.docker.com/r/sstc/android-ndk)

## Usage

```bash
docker run --rm sstc/android-ndk env

docker run --rm -v `pwd`:/app sstc/android-ndk cmake .
```
