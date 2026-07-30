// testpeer is a minimal BGP speaker that listens on :179 and responds
// with a hardcoded OPEN + periodic KEEPALIVEs. Use it to test minibgp
// without a real BGP router.
//
// Usage (terminal 1):
//
//	sudo go run ./cmd/testpeer  (needs root for port 179)
//
// Usage (terminal 2):
//
//	go run . --local-as=65001 --router-id=10.0.0.1 127.0.0.1
package main

import (
	"fmt"
	"io"
	"log"
	"net"
	"os"
	"time"

	"github.com/luke0628/minibgp/pkg/bgp"
)

func main() {
	port := 179
	if len(os.Args) > 1 {
		fmt.Sscanf(os.Args[1], "%d", &port)
	}

	ln, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		log.Fatalf("listen: %v", err)
	}
	log.Printf("Listening on :%d — connect your minibgp with: go run . --local-as=65001 --router-id=10.0.0.1 127.0.0.1", port)

	for {
		conn, err := ln.Accept()
		if err != nil {
			log.Printf("accept: %v", err)
			continue
		}
		go handle(conn)
	}
}

func handle(conn net.Conn) {
	defer conn.Close()
	peerAddr := conn.RemoteAddr().String()
	log.Printf("[%s] connected", peerAddr)

	// Read peer's OPEN
	hdr, err := bgp.ReadHeader(conn)
	if err != nil {
		log.Printf("[%s] read header: %v", peerAddr, err)
		return
	}
	if hdr.Type != bgp.MsgOpen {
		log.Printf("[%s] expected OPEN, got type %d", peerAddr, hdr.Type)
		return
	}

	bodyLen := int(hdr.Length) - 19
	body := make([]byte, bodyLen)
	if _, err := io.ReadFull(conn, body); err != nil {
		log.Printf("[%s] read OPEN body: %v", peerAddr, err)
		return
	}
	open, err := bgp.ParseOpen(body)
	if err != nil {
		log.Printf("[%s] parse OPEN: %v", peerAddr, err)
		return
	}
	log.Printf("[%s] %s", peerAddr, open)

	// Send our OPEN
	resp := &bgp.OpenMsg{
		Version:  4,
		MyAS:     65002,
		HoldTime: 90,
		BGPID:    net.ParseIP("10.0.0.254").To4(),
	}
	log.Printf("[%s] → %s", peerAddr, resp)
	if err := resp.Write(conn); err != nil {
		log.Printf("[%s] write OPEN: %v", peerAddr, err)
		return
	}

	// Read KEEPALIVE (OPEN_CONFIRM → ESTABLISHED)
	if _, err := bgp.ReadHeader(conn); err != nil {
		log.Printf("[%s] read keepalive confirm: %v", peerAddr, err)
		return
	}
	log.Printf("[%s] session ESTABLISHED", peerAddr)

	// Send KEEPALIVEs periodically
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	errCh := make(chan error, 1)
	go func() {
		for {
			hdr, err := bgp.ReadHeader(conn)
			if err != nil {
				errCh <- err
				return
			}
			// discard body
			if hdr.Length > 19 {
				discard := make([]byte, int(hdr.Length)-19)
				io.ReadFull(conn, discard)
			}
			switch hdr.Type {
			case bgp.MsgKeepalive:
				log.Printf("[%s] KEEPALIVE recv", peerAddr)
			case bgp.MsgNotification:
				log.Printf("[%s] NOTIFICATION recv", peerAddr)
				errCh <- fmt.Errorf("peer sent notification")
				return
			default:
				log.Printf("[%s] msg type %d", peerAddr, hdr.Type)
			}
		}
	}()

	for {
		select {
		case err := <-errCh:
			log.Printf("[%s] closed: %v", peerAddr, err)
			return
		case <-ticker.C:
			ka := &bgp.KeepaliveMsg{}
			if err := ka.Write(conn); err != nil {
				log.Printf("[%s] keepalive write: %v", peerAddr, err)
				return
			}
		}
	}
}
