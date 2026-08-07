FROM rust:1.85-slim AS build
WORKDIR /src
COPY Cargo.toml ./
COPY src ./src
COPY tests ./tests
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=build /src/target/release/camelot-node-agent /usr/local/bin/camelot-node-agent
ENV NODE_AGENT_ADDR=0.0.0.0:8789
EXPOSE 8789
ENTRYPOINT ["camelot-node-agent"]
