# ROTEL (Telemetry Collector) — Multi-stage Docker Build
# Build context: this directory (02_FORGE/KINETIC_ARMORY/rotel/)
FROM rust:1.80-slim AS builder
WORKDIR /app
COPY Cargo.toml Cargo.lock ./
RUN mkdir src && echo 'fn main(){}' > src/main.rs && cargo build --release && rm -rf src
COPY src ./src
RUN cargo build --release

FROM debian:bookworm-slim
WORKDIR /app
COPY --from=builder /app/target/release/rotel .
EXPOSE 4317
CMD ["./rotel"]
