// Package peer manages a single BGP session: TCP connect, OPEN exchange,
// keepalive loop, and message dispatch. This is where the goroutine and
// channel learning happens.
package peer

import (
	"context"
	"fmt"
	"log"
	"net"
	"sync"
	"time"

	"github.com/luke0628/minibgp/pkg/bgp"
)

// Config holds the parameters for a BGP session.
type Config struct {
	LocalAS  uint16
	RouterID string // e.g. "10.0.0.1"
	HoldTime uint16 // seconds, 0 = default 90
}

// Peer represents a single BGP session to a remote speaker.
type Peer struct {
	cfg    Config
	addr   string          // "1.2.3.4:179"
	conn   net.Conn        // the TCP socket
	state  string          // "IDLE", "CONNECT", "OPEN_SENT", "OPEN_CONFIRM", "ESTABLISHED"
	mu     sync.RWMutex    // protects state and conn
	events chan Event      // channel for reporting state changes
	cancel context.CancelFunc // cancels the session goroutines
}

// Event is sent on Peer.events when the session state changes or receives a message.
type Event struct {
	Type    string // "STATE", "OPEN", "KEEPALIVE", "ERROR", "CLOSED"
	Message string
	Peer    string
	Open    *bgp.OpenMsg // populated on "OPEN" events
}

// New creates a Peer in IDLE state.
func New(cfg Config, peerIP string) (*Peer, error) {
	if _, err := bgp.IPToRouterID(cfg.RouterID); err != nil {
		return nil, fmt.Errorf("bad router-id: %w", err)
	}
	if cfg.HoldTime == 0 {
		cfg.HoldTime = 90
	}
	return &Peer{
		cfg:    cfg,
		addr:   net.JoinHostPort(peerIP, fmt.Sprintf("%d", bgp.Port)),
		state:  "IDLE",
		events: make(chan Event, 16), // buffered so sender never blocks
	}, nil
}

// Events returns the read-only event channel.
// The caller should range over it in a goroutine.
func (p *Peer) Events() <-chan Event {
	return p.events
}

// State returns the current FSM state.
func (p *Peer) State() string {
	p.mu.RLock()
	defer p.mu.RUnlock()
	return p.state
}

func (p *Peer) setState(s string) {
	p.mu.Lock()
	defer p.mu.Unlock()
	old := p.state
	p.state = s
	if old != s {
		p.events <- Event{Type: "STATE", Message: fmt.Sprintf("%s → %s", old, s), Peer: p.addr}
	}
}

// Connect dials the peer, sends OPEN, starts keepalives.
// Blocks until the session ends or ctx is cancelled.
func (p *Peer) Connect(ctx context.Context) error {
	ctx, p.cancel = context.WithCancel(ctx)
	defer p.cancel()

	p.setState("CONNECT")

	conn, err := net.DialTimeout("tcp", p.addr, 10*time.Second)
	if err != nil {
		p.sendError(fmt.Errorf("dial: %w", err))
		p.setState("IDLE")
		return fmt.Errorf("connect: %w", err)
	}
	p.mu.Lock()
	p.conn = conn
	p.mu.Unlock()

	p.setState("OPEN_SENT")

	// Send OPEN
	open := &bgp.OpenMsg{
		Version:  4,
		MyAS:     p.cfg.LocalAS,
		HoldTime: p.cfg.HoldTime,
		BGPID:    net.ParseIP(p.cfg.RouterID).To4(),
		// No optional parameters for now (add capabilities later).
	}
	if err := open.Write(conn); err != nil {
		p.sendError(fmt.Errorf("write OPEN: %w", err))
		p.setState("IDLE")
		return fmt.Errorf("write open: %w", err)
	}
	log.Printf("[%s] OPEN sent: %s", p.addr, open)

	// Read peer's OPEN
	peerOpen, err := p.readOpen(conn)
	if err != nil {
		p.sendError(fmt.Errorf("read OPEN: %w", err))
		p.setState("IDLE")
		return fmt.Errorf("read open: %w", err)
	}
	p.events <- Event{Type: "OPEN", Message: peerOpen.String(), Peer: p.addr, Open: peerOpen}
	p.setState("OPEN_CONFIRM")

	// Send KEEPALIVE to confirm
	ka := &bgp.KeepaliveMsg{}
	if err := ka.Write(conn); err != nil {
		p.sendError(fmt.Errorf("write KEEPALIVE: %w", err))
		p.setState("IDLE")
		return fmt.Errorf("write keepalive: %w", err)
	}
	p.setState("ESTABLISHED")

	// Start keepalive goroutine and message reader goroutine.
	var wg sync.WaitGroup
	wg.Add(2)

	// Goroutine 1: send keepalives periodically.
	go p.keepaliveLoop(ctx, conn, &wg)

	// Goroutine 2: read incoming messages.
	go p.readLoop(ctx, conn, &wg)

	// Wait for either goroutine to exit (means session is down).
	wg.Wait()
	p.setState("IDLE")
	p.events <- Event{Type: "CLOSED", Peer: p.addr}
	return nil
}

// Close tears down the session.
func (p *Peer) Close() {
	p.mu.Lock()
	defer p.mu.Unlock()
	if p.cancel != nil {
		p.cancel()
	}
	if p.conn != nil {
		p.conn.Close()
	}
}

// keepaliveLoop sends KEEPALIVE every HoldTime/3 seconds.
// Exits when ctx is done or write fails.
func (p *Peer) keepaliveLoop(ctx context.Context, conn net.Conn, wg *sync.WaitGroup) {
	defer wg.Done()
	ticker := time.NewTicker(time.Duration(p.cfg.HoldTime/3) * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ctx.Done():
			return
		case <-ticker.C:
			ka := &bgp.KeepaliveMsg{}
			if err := ka.Write(conn); err != nil {
				p.sendError(fmt.Errorf("keepalive write: %w", err))
				return
			}
		}
	}
}

// readLoop reads BGP messages from the peer and dispatches them.
// Exits when ctx is done or read fails.
func (p *Peer) readLoop(ctx context.Context, conn net.Conn, wg *sync.WaitGroup) {
	defer wg.Done()

	for {
		select {
		case <-ctx.Done():
			return
		default:
		}

		hdr, err := bgp.ReadHeader(conn)
		if err != nil {
			p.sendError(fmt.Errorf("read header: %w", err))
			return
		}

		bodyLen := int(hdr.Length) - 19
		body := make([]byte, bodyLen)
		if bodyLen > 0 {
			if _, err := ioReadFull(conn, body); err != nil {
				p.sendError(fmt.Errorf("read body: %w", err))
				return
			}
		}

		switch hdr.Type {
		case bgp.MsgOpen:
			// unexpected OPEN in established state
			p.events <- Event{Type: "ERROR", Message: "unexpected OPEN received", Peer: p.addr}
			return
		case bgp.MsgKeepalive:
			p.events <- Event{Type: "KEEPALIVE", Peer: p.addr}
		case bgp.MsgNotification:
			p.events <- Event{Type: "ERROR", Message: "NOTIFICATION received, closing", Peer: p.addr}
			return
		case bgp.MsgUpdate:
			p.events <- Event{Type: "ERROR", Message: "UPDATE not implemented", Peer: p.addr}
			// Don't tear down, just log.
		default:
			p.events <- Event{Type: "ERROR", Message: fmt.Sprintf("unknown type %d", hdr.Type), Peer: p.addr}
		}
	}
}

// readOpen reads and parses a peer's OPEN message (header + body).
func (p *Peer) readOpen(conn net.Conn) (*bgp.OpenMsg, error) {
	hdr, err := bgp.ReadHeader(conn)
	if err != nil {
		return nil, err
	}
	if hdr.Type != bgp.MsgOpen {
		return nil, fmt.Errorf("expected OPEN (type 1), got type %d", hdr.Type)
	}

	bodyLen := int(hdr.Length) - 19
	body := make([]byte, bodyLen)
	if _, err := ioReadFull(conn, body); err != nil {
		return nil, fmt.Errorf("reading OPEN body: %w", err)
	}
	return bgp.ParseOpen(body)
}

// sendError sends an ERROR event without tearing down the session.
func (p *Peer) sendError(err error) {
	p.events <- Event{Type: "ERROR", Message: err.Error(), Peer: p.addr}
}

// ioReadFull is a local helper to avoid importing io for the one call.
func ioReadFull(r net.Conn, buf []byte) (int, error) {
	total := 0
	for total < len(buf) {
		n, err := r.Read(buf[total:])
		total += n
		if err != nil {
			if total == len(buf) {
				return total, nil
			}
			return total, err
		}
	}
	return total, nil
}
