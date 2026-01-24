FROM saschpe/android-ndk:35-jdk23.0.2_7-ndk28.0.13004108-cmake3.31.5

ARG CMAKE_VERSION
ENV ANDROID_NDK_HOME=$NDK_ROOT
ENV PATH=$PATH:$ANDROID_SDK_ROOT/cmake/$CMAKE_VERSION/bin

USER root
RUN set -ex; \
	apt update; \
	apt install --no-install-recommends -y \
	libssl-dev \
	zlib1g-dev \
	gperf \
	build-essential \
	wget \
	; \
	wget https://github.com/Kitware/CMake/releases/download/v${CMAKE_VERSION}/cmake-${CMAKE_VERSION}-linux-x86_64.tar.gz -O cmake.tar.gz; \
	tar -xf cmake.tar.gz; \
	mv cmake-${CMAKE_VERSION}-linux-x86_64 $ANDROID_SDK_ROOT/cmake/$CMAKE_VERSION; \
	rm cmake.tar.gz; \
	rm -rf /var/lib/apt/lists/*

VOLUME [ "/app" ]
WORKDIR /app
