package main

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
)

func TestEncodeRoute(t *testing.T) {
	encoded, err := EncodeRoute(MCPRoute{Target: "camelot", Method: "//STATUS"})
	if err != nil {
		t.Fatal(err)
	}
	if encoded != `{"target":"camelot","method":"//STATUS"}` {
		t.Fatalf("unexpected route: %s", encoded)
	}
}

func TestHTTPHealthRoute(t *testing.T) {
	handler := BuildHTTPHandler(NewTsnetServer("camelot-node-c"))
	req := httptest.NewRequest(http.MethodGet, "/health", nil)
	rec := httptest.NewRecorder()

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("unexpected status: %d", rec.Code)
	}
	var payload map[string]string
	if err := json.Unmarshal(rec.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload["status"] != "ok" || payload["node"] != "Node_C_Omni_Router" {
		t.Fatalf("unexpected payload: %#v", payload)
	}
}

func TestNanoSwarmStatusRoute(t *testing.T) {
	handler := BuildHTTPHandler(NewTsnetServer("camelot-node-c"))
	req := httptest.NewRequest(http.MethodGet, "/v1/nano-swarm/status", nil)
	rec := httptest.NewRecorder()

	handler.ServeHTTP(rec, req)

	if rec.Code != http.StatusOK {
		t.Fatalf("unexpected status: %d", rec.Code)
	}
	var payload NanoSwarmStatus
	if err := json.Unmarshal(rec.Body.Bytes(), &payload); err != nil {
		t.Fatal(err)
	}
	if payload.Status != "ok" || payload.Router != "camelot-node-c" {
		t.Fatalf("unexpected payload: %#v", payload)
	}
	if len(payload.Routes) != 2 {
		t.Fatalf("expected 2 routes, got %d", len(payload.Routes))
	}
}
