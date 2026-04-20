# CRIBO (Bundler) Dockerfile
FROM rust:1.75-slim as builder
WORKDIR /app
COPY CAMELOT_OS/02_FORGE/kinetic/cribo .
RUN cargo build --release

FROM debian:12
WORKDIR /app
COPY --from=builder /app/target/release/cribo .
CMD ["./cribo"]