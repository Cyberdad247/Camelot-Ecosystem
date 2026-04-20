# ROTEL (Telemetry)
FROM rust:1.84-slim as builder
WORKDIR /app
COPY . .
RUN cargo build --release

FROM debian:12
WORKDIR /app
COPY --from=builder /app/target/release/rotel .
CMD ["./rotel"]