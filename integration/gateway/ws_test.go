package main

import (
	"bufio"
	"crypto/sha1"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"io"
	"net"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"
)

// Minimal WS client for tests: RFC 6455 handshake + unmasked-frame reader.

func httpGet(url string) (string, error) {
	res, err := http.Get(url)
	if err != nil {
		return "", err
	}
	defer res.Body.Close()
	body, err := io.ReadAll(res.Body)
	return string(body), err
}

func httpGetStatus(url string) (int, error) {
	res, err := http.Get(url)
	if err != nil {
		return 0, err
	}
	res.Body.Close()
	return res.StatusCode, nil
}

func wsDial(t *testing.T, ts *httptest.Server, path string) (net.Conn, *bufio.Reader) {
	t.Helper()
	addr := strings.TrimPrefix(ts.URL, "http://")
	conn, err := net.Dial("tcp", addr)
	if err != nil {
		t.Fatal(err)
	}
	t.Cleanup(func() { conn.Close() })

	key := base64.StdEncoding.EncodeToString([]byte("0123456789abcdef"))
	fmt.Fprintf(conn, "GET %s HTTP/1.1\r\nHost: %s\r\nUpgrade: websocket\r\nConnection: Upgrade\r\nSec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n", path, addr, key)

	reader := bufio.NewReader(conn)
	statusLine, err := reader.ReadString('\n')
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(statusLine, "101") {
		t.Fatalf("handshake failed: %s", statusLine)
	}
	var acceptHeader string
	for {
		line, err := reader.ReadString('\n')
		if err != nil {
			t.Fatal(err)
		}
		if strings.HasPrefix(strings.ToLower(line), "sec-websocket-accept:") {
			acceptHeader = strings.TrimSpace(strings.SplitN(line, ":", 2)[1])
		}
		if line == "\r\n" {
			break
		}
	}
	sum := sha1.Sum([]byte(key + wsGUID))
	if acceptHeader != base64.StdEncoding.EncodeToString(sum[:]) {
		t.Fatalf("bad Sec-WebSocket-Accept %q", acceptHeader)
	}
	return conn, reader
}

func wsReadTextFrame(t *testing.T, reader *bufio.Reader, conn net.Conn) string {
	t.Helper()
	if err := conn.SetReadDeadline(time.Now().Add(3 * time.Second)); err != nil {
		t.Fatal(err)
	}
	head := make([]byte, 2)
	if _, err := io.ReadFull(reader, head); err != nil {
		t.Fatalf("frame header: %v", err)
	}
	if head[0]&0x0F != 0x1 {
		t.Fatalf("expected text frame, opcode %d", head[0]&0x0F)
	}
	length := uint64(head[1] & 0x7F)
	switch length {
	case 126:
		ext := make([]byte, 2)
		if _, err := io.ReadFull(reader, ext); err != nil {
			t.Fatal(err)
		}
		length = uint64(binary.BigEndian.Uint16(ext))
	case 127:
		ext := make([]byte, 8)
		if _, err := io.ReadFull(reader, ext); err != nil {
			t.Fatal(err)
		}
		length = binary.BigEndian.Uint64(ext)
	}
	payload := make([]byte, length)
	if _, err := io.ReadFull(reader, payload); err != nil {
		t.Fatal(err)
	}
	return string(payload)
}

func TestSessionEventsOverWebSocket(t *testing.T) {
	_, ts := newTestServer(t)
	conn, reader := wsDial(t, ts, "/v1/sessions/sess-anya-demo-001/events")

	// Give the server a beat to register the subscriber, then fire a turn.
	time.Sleep(50 * time.Millisecond)
	go func() {
		body := `{"sessionId":"sess-anya-demo-001","turnId":"turn-0030","modality":"text","transcript":"read staging status","startedAtMs":1}`
		http.Post(ts.URL+"/v1/voice/turns", "application/json", strings.NewReader(body))
	}()

	var sawAccepted, sawDecision, sawChunk bool
	for i := 0; i < 30 && !(sawAccepted && sawDecision && sawChunk); i++ {
		payload := wsReadTextFrame(t, reader, conn)
		var event SessionEvent
		if err := json.Unmarshal([]byte(payload), &event); err != nil {
			t.Fatalf("event not JSON: %s", payload)
		}
		switch event.Type {
		case "turn.accepted":
			sawAccepted = true
		case "policy.decision":
			sawDecision = true
			if event.Decision == nil || event.Decision.SkillID != "ops.staging.read" {
				t.Fatalf("decision event %+v", event)
			}
		case "reply.chunk":
			sawChunk = true
		}
	}
	if !sawAccepted || !sawDecision || !sawChunk {
		t.Fatalf("missing events: accepted=%t decision=%t chunk=%t", sawAccepted, sawDecision, sawChunk)
	}
}
