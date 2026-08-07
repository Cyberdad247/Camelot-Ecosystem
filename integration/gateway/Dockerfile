FROM golang:1.22-alpine AS build
WORKDIR /src
COPY go.mod ./
COPY *.go ./
RUN CGO_ENABLED=0 go build -o /gateway .

FROM alpine:3.20
COPY --from=build /gateway /usr/local/bin/gateway
ENV GATEWAY_ADDR=:8788
EXPOSE 8788
ENTRYPOINT ["gateway"]
