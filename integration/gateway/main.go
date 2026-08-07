package main

import (
	"log"
	"net/http"
	"os"
	"time"
)

func main() {
	addr := os.Getenv("GATEWAY_ADDR")
	if addr == "" {
		addr = ":8788"
	}
	server := NewServer(60*time.Millisecond, time.Now)
	log.Printf("%s %s listening on %s", serviceName, serviceVersion, addr)
	if err := http.ListenAndServe(addr, server.Handler()); err != nil {
		log.Fatal(err)
	}
}
