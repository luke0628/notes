// Package bgp implements core BGP message types and wire-format encoding.
//
// This is a minimal implementation for learning Go through a familiar domain.
// It covers BGP OPEN and KEEPALIVE messages per RFC 4271.
// UPDATE and NOTIFICATION are left as stubs for later.
package bgp

import (
	"encoding/binary"
	"fmt"
	"io"
	"net"
)

// BGP message types (RFC 4271 §4.1).
const (
	MsgOpen         = 1
	MsgUpdate       = 2
	MsgNotification = 3
	MsgKeepalive    = 4
)

// Standard BGP port.
const Port = 179

// Marker is the 16-byte sync field that precedes every BGP message.
var Marker = [16]byte{
	0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
	0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
}

// Header is the 19-byte prefix of every BGP message.
//
//	 0                   1                   2                   3
//	 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//	|                                                               |
//	|                           Marker (16)                          |
//	|                                                               |
//	|                                                               |
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//	|          Length               |      Type     |
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
type Header struct {
	Marker [16]byte
	Length uint16 // total message length including header
	Type   uint8
}

// String returns a human-readable description of the message type.
func (h Header) String() string {
	names := map[uint8]string{1: "OPEN", 2: "UPDATE", 3: "NOTIFICATION", 4: "KEEPALIVE"}
	name, ok := names[h.Type]
	if !ok {
		name = fmt.Sprintf("UNKNOWN(%d)", h.Type)
	}
	return fmt.Sprintf("%s len=%d", name, h.Length)
}

// ReadHeader reads a BGP message header from the wire.
// Returns the parsed header. The caller is responsible for reading
// the remaining (Length - 19) bytes of the message body.
func ReadHeader(r io.Reader) (Header, error) {
	var h Header
	if err := binary.Read(r, binary.BigEndian, &h); err != nil {
		return h, fmt.Errorf("reading header: %w", err)
	}
	if h.Marker != Marker {
		return h, fmt.Errorf("bad marker: expected all 0xff")
	}
	if h.Length < 19 || h.Length > 4096 {
		return h, fmt.Errorf("invalid length: %d (must be 19-4096)", h.Length)
	}
	return h, nil
}

// WriteHeader writes a BGP message header to the wire.
func (h *Header) Write(w io.Writer) error {
	h.Marker = Marker
	return binary.Write(w, binary.BigEndian, h)
}

// IPToRouterID converts a string like "10.0.0.1" into a 4-byte router ID.
func IPToRouterID(s string) (net.IP, error) {
	ip := net.ParseIP(s)
	if ip == nil {
		return nil, fmt.Errorf("invalid IP: %s", s)
	}
	return ip.To4(), nil
}
