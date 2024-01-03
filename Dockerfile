FROM ubuntu:20.04

ENV LANG C.UTF-8

WORKDIR tmp

ARG DEBIAN_FRONTEND=noninteractive

RUN chmod 777 /tmp
RUN apt-get update && \
    apt-get install -y --no-install-recommends --no-install-suggests wget curl vim ca-certificates autoconf automake bison build-essential clang cmake doxygen flex g++ git libffi-dev libncurses5-dev libtool libsqlite3-dev make mcpp sqlite3 zlib1g-dev zip unzip python3 python3-pip creduce libglib2.0-dev bsdmainutils rsyslog python3-dev default-jdk xz-utils libc6-dev libgmp-dev && \
    pip3 install termcolor pyfiglet networkx

# this command will install the last version of souffle in github
RUN git clone https://github.com/souffle-lang/souffle.git && \
    cd souffle && \
    cmake -S . -DCMAKE_BUILD_TYPE=Debug -DSOUFFLE_DOMAIN_64BIT=ON -B build && \
    cmake --build build -j8 && \
    ln -s /tmp/souffle/build/src/souffle /usr/bin/

# install MuZ
RUN git clone https://github.com/Z3Prover/z3.git && \
    cd z3 && \
    python3 scripts/mk_make.py && \
    cd build && \
    make -j4 && \
    make install

# install DDlog from source code
RUN git clone https://github.com/vmware/differential-datalog.git && \
    cd differential-datalog && \
    wget -qO- https://get.haskellstack.org/ | sh && \
    curl https://sh.rustup.rs -sSf | bash -s -- -y && \
    . $HOME/.cargo/env && \
    rustup component add rustfmt && \
    rustup component add clippy && \
    ./tools/install-flatbuf.sh
ENV PATH=/root/.cargo/bin/:$PATH
ENV PATH=/root/.local/bin:$PATH
ENV PATH=/tmp/differential-datalog/flatbuffers:$PATH
ENV CLASSPATH=/tmp/differential-datalog/flatbuffers/java:$CLASSPATH
RUN cd differential-datalog && \
    stack build && \
    stack install

# install DDlog from last release version
# RUN wget https://github.com/vmware/differential-datalog/releases/download/v1.2.3/ddlog-v1.2.3-20211213235218-Linux.tar.gz && \
#     tar -zxvf ddlog-v1.2.3-20211213235218-Linux.tar.gz && \
#     mkdir /root/.local/ && \
#     cp -r ddlog/bin /root/.local/ && \
#     cp -r ddlog/lib /root/.local/ && \
#     rm ddlog-v1.2.3-20211213235218-Linux.tar.gz && \
#     mv ddlog differential-datalog && \
#     curl https://sh.rustup.rs -sSf | bash -s -- -y && \
#     . $HOME/.cargo/env && \
#     rustup component add rustfmt && \
#     rustup component add clippy
# ENV PATH=/root/.cargo/bin/:$PATH

# install cozodb
RUN pip install "pycozo[embedded,requests,pandas]"
