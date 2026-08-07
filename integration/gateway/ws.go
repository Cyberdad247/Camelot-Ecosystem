package main

import (
	"bufio"
	"crypto/sha1"
	"encoding/base64"
	"encoding/binary"
	"fmt"
	"net"
	"net/http"
	"strings"
)

// Minimal RFC 6455 WebSocket support — server-push only, no external deps
// (keeps the gateway stdlib-only and offline-buildable; accepted cost in
// ADR-001). Server-to-client frames are unmasked text frames; incoming
// frames are read only to detect close.

const wsGUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

type wsConn struct {
	conn net.Conn
	bw   *bufio.ReadWriter
}

// wsUpgrade performs the opening handshake and hijacks the connection.
func wsUpgrade(w http.ResponseWriter, r *http.Request) (*wsConn, error) {
	if !strings.EqualFold(r.Header.Get("Upgrade"), "websocket") {
		return nil, fmt.Errorf("not a websocket upgrade")
	}
	key := r.Header.Get("Sec-WebSocket-Key")
	if key == "" {
		return nil, fmt.Errorf("missing Sec-WebSocket-Key")
	}
	hj, ok := w.(http.Hijacker)
	if !ok {
		return nil, fmt.Errorf("response writer does not support hijacking")
	}
	conn, bw, err := hj.Hijack()
	if err != nil {
		return nil, err
	}

	sum := sha1.Sum([]byte(key + wsGUID))
	accept := base64.StdEncoding.EncodeToString(sum[:])
	response := "HTTP/1.1 101 Switching Protocols\r\n" +
		"Upgrade: websocket\r\n" +
		"Connection: Upgrade\r\n" +
		"Sec-WebSocket-Accept: " + accept + "\r\n\r\n"
	if _, err := bw.WriteString(response); err != nil {
		conn.Close()
		return nil, err
	}
	if err := bw.Flush(); err != nil {
		conn.Close()
		return nil, err
	}
	return &wsConn{conn: conn, bw: bw}, nil
}

// WriteText sends one unmasked text frame (server -> client).
func (c *wsConn) WriteText(payload []byte) error {
	var header []byte
	n := len(payload)
	switch {
	case n < 126:
		header = []byte{0x81, byte(n)}
	case n <= 0xFFFF:
		header = []byte{0x81, 126, 0, 0}
		binary.BigEndian.PutUint16(header[2:], uint16(n))
	default:
		header = append([]byte{0x81, 127}, make([]byte, 8)...)
		binary.BigEndian.PutUint64(header[2:], uint64(n))
	}
	if _, err := c.bw.Write(header); err != nil {
		return err
	}
	if _, err := c.bw.Write(payload); err != nil {
		return err
	}
	return c.bw.Flush()
}

// ReadUntilClose consumes client frames, returning when the peer closes.
// Client frames are masked per RFC 6455; payloads are discarded.
func (c *wsConn) ReadUntilClose() {
	for {
		head := make([]byte, 2)
		if _, err := readFull(c.bw.Reader, head); err != nil {
			return
		}
		opcode := head[0] & 0x0F
		masked := head[1]&0x80 != 0
		length := uint64(head[1] & 0x7F)
		switch length {
		case 126:
			ext := make([]byte, 2)
			if _, err := readFull(c.bw.Reader, ext); err != nil {
				return
			}
			length = uint64(binary.BigEndian.Uint16(ext))
		case 127:
			ext := make([]byte, 8)
			if _, err := readFull(c.bw.Reader, ext); err != nil {
				return
			}
			length = binary.BigEndian.Uint64(ext)
		}
		if masked {
			if _, err := readFull(c.bw.Reader, make([]byte, 4)); err != nil {
				return
			}
		}
		if length > 1<<20 {
			return // refuse absurd frames
		}
		if _, err := readFull(c.bw.Reader, make([]byte, length)); err != nil {
			return
		}
		if opcode == 0x8 { // close
			return
		}
	}
}

func (c *wsConn) Close() error {
	// Best-effort close frame, then TCP close.
	_, _ = c.bw.Write([]byte{0x88, 0x00})
	_ = c.bw.Flush()
	return c.conn.Close()
}

func readFull(r *bufio.Reader, buf []byte) (int, error) {
	total := 0
	for total < len(buf) {
		n, err := r.Read(buf[total:])
		if err != nil {
			return total, err
		}
		total += n
	}
	return total, nil
}
