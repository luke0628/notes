package bgp

import "io"

// KeepaliveMsg is a BGP KEEPALIVE message (RFC 4271 §4.4).
// It consists only of the 19-byte header — no body.
type KeepaliveMsg struct{}

// Write sends a BGP KEEPALIVE message over the wire.
func (k *KeepaliveMsg) Write(w io.Writer) error {
	h := Header{
		Length: 19, // header only, no body
		Type:   MsgKeepalive,
	}
	return h.Write(w)
}

// String returns a human-readable summary.
func (k *KeepaliveMsg) String() string {
	return "KEEPALIVE"
}
