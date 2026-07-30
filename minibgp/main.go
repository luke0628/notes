// minibgp — a minimal BGP speaker for learning Go.
//
// Usage:
//
//	go run . [--local-as=65001] [--router-id=10.0.0.1] <peer-ip>
//
// Example:
//
//	go run . --local-as=65001 --router-id=10.0.0.1 10.0.0.2
//
// To test locally without a real BGP peer, use the test server:
//
//	go run ./cmd/testpeer  (in another terminal)
//	go run . --local-as=65001 --router-id=10.0.0.1 127.0.0.1
package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/luke0628/minibgp/pkg/peer"
)

func main() {
	localAS := flag.Int("local-as", 65001, "local AS number")
	routerID := flag.String("router-id", "10.0.0.1", "BGP router ID")
	flag.Parse()

	if flag.NArg() < 1 {
		fmt.Fprintf(os.Stderr, "usage: %s [--local-as=N] [--router-id=X.X.X.X] <peer-ip>\n", os.Args[0])
		os.Exit(1)
	}
	peerIP := flag.Arg(0)

	cfg := peer.Config{
		LocalAS:  uint16(*localAS),
		RouterID: *routerID,
		HoldTime: 90,
	}

	p, err := peer.New(cfg, peerIP)
	if err != nil {
		log.Fatalf("creating peer: %v", err)
	}
	defer p.Close()

	// Context cancelled on Ctrl+C or SIGTERM.
	ctx, cancel := context.WithCancel(context.Background())
	defer cancel()

	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
	go func() {
		sig := <-sigCh
		log.Printf("received %v, shutting down...", sig)
		cancel()
	}()

	// Watch events in a goroutine.
	go func() {
		for evt := range p.Events() {
			switch evt.Type {
			case "STATE":
				log.Printf("STATE: %s", evt.Message)
			case "OPEN":
				log.Printf("PEER OPEN: %s", evt.Message)
			case "KEEPALIVE":
				log.Printf("KEEPALIVE received")
			case "ERROR":
				log.Printf("ERROR: %s", evt.Message)
			case "CLOSED":
				log.Printf("Session closed — reconnecting in 5s...")
			}
		}
	}()

	// Auto-reconnect loop.
	for {
		if p.State() == "ESTABLISHED" {
			time.Sleep(1 * time.Second)
			continue
		}
		log.Printf("Connecting to %s:%d (AS=%d, ID=%s)...",
			peerIP, 179, cfg.LocalAS, cfg.RouterID)

		err := p.Connect(ctx)
		if err != nil {
			log.Printf("Session failed: %v", err)
		}

		select {
		case <-ctx.Done():
			log.Println("Shutting down.")
			return
		case <-time.After(5 * time.Second):
			// reconnect
		}
	}
}
