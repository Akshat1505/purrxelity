FROM ubuntu:25.04

RUN apt-get update && apt-get install -y build-essential python3 curl && \
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && apt-get clean && \ 
rm -rf /var/lib/apt/lists/*

ENV PATH="/root/.cargo/bin:${PATH}"
WORKDIR /app

