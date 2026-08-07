package main

import (
	"context"
	"strings"
	"sync"
	"time"
)

// SessionHub fans session events out to WebSocket subscribers and tracks
// in-flight streaming replies so barge-in can cancel them.

type SessionHub struct {
	mu          sync.Mutex
	subscribers map[string]map[chan SessionEvent]struct{} // sessionID -> subs
	streams     map[string]context.CancelFunc             // turnID -> cancel
	// chunkDelay paces reply.chunk events; tests shrink it, barge-in tests
	// grow it to hold the stream open.
	chunkDelay time.Duration
}

func NewSessionHub(chunkDelay time.Duration) *SessionHub {
	return &SessionHub{
		subscribers: map[string]map[chan SessionEvent]struct{}{},
		streams:     map[string]context.CancelFunc{},
		chunkDelay:  chunkDelay,
	}
}

func (h *SessionHub) Subscribe(sessionID string) (chan SessionEvent, func()) {
	ch := make(chan SessionEvent, 64)
	h.mu.Lock()
	if h.subscribers[sessionID] == nil {
		h.subscribers[sessionID] = map[chan SessionEvent]struct{}{}
	}
	h.subscribers[sessionID][ch] = struct{}{}
	h.mu.Unlock()
	return ch, func() {
		h.mu.Lock()
		delete(h.subscribers[sessionID], ch)
		h.mu.Unlock()
	}
}

func (h *SessionHub) Publish(sessionID string, event SessionEvent) {
	h.mu.Lock()
	defer h.mu.Unlock()
	for ch := range h.subscribers[sessionID] {
		select {
		case ch <- event:
		default: // slow subscriber: drop rather than block the gateway
		}
	}
}

// StreamReply emits the reply as word-chunks on the event stream. Returns
// immediately; the goroutine stops early if CancelTurn is called (barge-in),
// emitting turn.cancelled instead of reply.done.
func (h *SessionHub) StreamReply(sessionID, turnID, reply string) {
	ctx, cancel := context.WithCancel(context.Background())
	h.mu.Lock()
	h.streams[turnID] = cancel
	h.mu.Unlock()

	words := strings.Split(reply, " ")
	go func() {
		defer func() {
			h.mu.Lock()
			delete(h.streams, turnID)
			h.mu.Unlock()
		}()
		for i, w := range words {
			select {
			case <-ctx.Done():
				h.Publish(sessionID, SessionEvent{Type: "turn.cancelled", TurnID: turnID, Reason: "barge-in"})
				return
			case <-time.After(h.chunkDelay):
			}
			text := w
			if i < len(words)-1 {
				text += " "
			}
			h.Publish(sessionID, SessionEvent{Type: "reply.chunk", TurnID: turnID, Seq: i, Text: text})
		}
		h.Publish(sessionID, SessionEvent{Type: "reply.done", TurnID: turnID})
	}()
}

// CancelTurn stops an in-flight stream. Returns true if one was active.
func (h *SessionHub) CancelTurn(turnID string) bool {
	h.mu.Lock()
	cancel, ok := h.streams[turnID]
	h.mu.Unlock()
	if ok {
		cancel()
	}
	return ok
}
