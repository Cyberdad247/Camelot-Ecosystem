# syntax=docker/dockerfile:1

FROM alpine:3.20 AS builder

RUN apk add --no-cache curl tar

WORKDIR /app
RUN curl -L https://github.com/bytecodealliance/wasmtime/releases/download/v23.0.0/wasmtime-v23.0.0-x86_64-linux.tar.xz | tar -xJ --strip-components=1

FROM alpine:3.20

WORKDIR /app

COPY --from=builder /app/wasmtime /usr/local/bin/wasmtime
COPY target/wasm32-wasip1/release/camelot-edge.wasm ./

# Configure non-root user
RUN adduser -D -u 1000 spv && \
    chown -R spv:spv /app
USER spv

CMD ["wasmtime", "run", "camelot-edge.wasm"]

