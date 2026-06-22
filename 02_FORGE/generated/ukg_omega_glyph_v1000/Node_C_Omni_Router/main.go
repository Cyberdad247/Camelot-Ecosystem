package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"net/http"
)

type MCPRoute struct {
	Target string `json:"target"`
	Method string `json:"method"`
}

type NanoSwarmStatus struct {
	Status string     `json:"status"`
	Node   string     `json:"node"`
	Router string     `json:"router"`
	Routes []MCPRoute `json:"routes"`
}

type OmniRouterServer struct {
	Hostname string
}

func NewTsnetServer(hostname string) *OmniRouterServer {
	return &OmniRouterServer{Hostname: hostname}
}

func EncodeRoute(route MCPRoute) (string, error) {
	encoded, err := json.Marshal(route)
	if err != nil {
		return "", err
	}
	return string(encoded), nil
}

func NewNanoSwarmStatus(server *OmniRouterServer) NanoSwarmStatus {
	return NanoSwarmStatus{
		Status: "ok",
		Node:   "Node_C_Omni_Router",
		Router: server.Hostname,
		Routes: []MCPRoute{
			{Target: server.Hostname, Method: "//STATUS"},
			{Target: server.Hostname, Method: "//NANO_SWARM_EXPAND"},
		},
	}
}

func BuildHTTPHandler(server *OmniRouterServer) http.Handler {
	mux := http.NewServeMux()
	writeJSON := func(w http.ResponseWriter, payload any) {
		w.Header().Set("Access-Control-Allow-Origin", "*")
		w.Header().Set("Content-Type", "application/json")
		_ = json.NewEncoder(w).Encode(payload)
	}
	mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodOptions {
			writeJSON(w, map[string]string{"status": "ok"})
			return
		}
		writeJSON(w, map[string]string{"status": "ok", "node": "Node_C_Omni_Router"})
	})
	mux.HandleFunc("/v1/nano-swarm/status", func(w http.ResponseWriter, r *http.Request) {
		if r.Method == http.MethodOptions {
			writeJSON(w, map[string]string{"status": "ok"})
			return
		}
		writeJSON(w, NewNanoSwarmStatus(server))
	})
	return mux
}

func Serve(host string, port int) error {
	server := NewTsnetServer("camelot-node-c")
	addr := fmt.Sprintf("%s:%d", host, port)
	return http.ListenAndServe(addr, BuildHTTPHandler(server))
}

func main() {
	serve := flag.Bool("serve", false, "start the Node C HTTP service")
	host := flag.String("host", "127.0.0.1", "HTTP bind host")
	port := flag.Int("port", 4180, "HTTP bind port")
	flag.Parse()

	if *serve {
		if err := Serve(*host, *port); err != nil {
			panic(err)
		}
		return
	}

	server := NewTsnetServer("camelot-node-c")
	route, err := EncodeRoute(MCPRoute{Target: server.Hostname, Method: "//STATUS"})
	if err != nil {
		panic(err)
	}
	fmt.Println(route)
}
