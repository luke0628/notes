package bgp

import (
	"encoding/binary"
	"fmt"
	"io"
	"net"
)

// OpenMsg is a BGP OPEN message (RFC 4271 §4.2).
//
//	 0                   1
//	 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//	|    Version    |
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//	|     My Autonomous System      |
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//	|           Hold Time           |
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//	|                         BGP Identifier                        |
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//	| Opt Parm Len  |
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
//	|                                                               |
//	|             Optional Parameters (variable)                    |
//	|                                                               |
//	+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
type OpenMsg struct {
	Version  uint8  // always 4
	MyAS     uint16 // local AS number (2-byte for now)
	HoldTime uint16 // seconds, 0 means use default; suggested: 90
	BGPID    net.IP // 4-byte router ID
	OptParms []OptParm
}

// OptParm is a single optional parameter in a BGP OPEN message.
// Each parameter is a TLV: Type (1), Length (1), Value (variable).
type OptParm struct {
	Type   uint8
	Length uint8
	Value  []byte // up to 255 bytes
}

// Capability codes we care about.
const (
	CapMultiprotocol = 1
	CapRouteRefresh  = 2
	Cap4OctetAS      = 65
)

// Capability is a BGP capability TLV advertised inside OptParm type=2.
type Capability struct {
	Code   uint8
	Length uint8
	Value  []byte
}

// ParseOpen parses a BGP OPEN message from raw bytes (body only, no header).
func ParseOpen(data []byte) (*OpenMsg, error) {
	if len(data) < 10 {
		return nil, fmt.Errorf("OPEN too short: %d bytes (min 10)", len(data))
	}
	o := &OpenMsg{
		Version:  data[0],
		MyAS:     binary.BigEndian.Uint16(data[1:3]),
		HoldTime: binary.BigEndian.Uint16(data[3:5]),
		BGPID:    net.IP(data[5:9]),
	}
	if o.Version != 4 {
		return nil, fmt.Errorf("unsupported BGP version: %d (want 4)", o.Version)
	}
	optLen := int(data[9])
	if 10+optLen > len(data) {
		return nil, fmt.Errorf("optional params overflow: declared %d, have %d",
			optLen, len(data)-10)
	}
	if optLen > 0 {
		if err := o.parseOptParms(data[10 : 10+optLen]); err != nil {
			return nil, err
		}
	}
	return o, nil
}

func (o *OpenMsg) parseOptParms(data []byte) error {
	for i := 0; i < len(data); {
		if i+2 > len(data) {
			return fmt.Errorf("truncated opt parm at offset %d", i)
		}
		p := OptParm{
			Type:   data[i],
			Length: data[i+1],
		}
		if i+2+int(p.Length) > len(data) {
			return fmt.Errorf("opt parm type %d overflow", p.Type)
		}
		p.Value = make([]byte, p.Length)
		copy(p.Value, data[i+2:i+2+int(p.Length)])
		o.OptParms = append(o.OptParms, p)
		i += 2 + int(p.Length)
	}
	return nil
}

// Params returns all capabilities extracted from OptParm type=2 (Capabilities).
func (o *OpenMsg) Capabilities() []Capability {
	var caps []Capability
	for _, p := range o.OptParms {
		if p.Type != 2 {
			continue
		}
		// Type 2 is the Capabilities optional parameter.
		// Inside: sequence of Capability TLVs.
		for i := 0; i < len(p.Value); {
			if i+2 > len(p.Value) {
				break
			}
			c := Capability{
				Code:   p.Value[i],
				Length: p.Value[i+1],
			}
			if i+2+int(c.Length) > len(p.Value) {
				break
			}
			c.Value = make([]byte, c.Length)
			copy(c.Value, p.Value[i+2:i+2+int(c.Length)])
			caps = append(caps, c)
			i += 2 + int(c.Length)
		}
	}
	return caps
}

// String returns a compact summary of the OPEN message.
func (o *OpenMsg) String() string {
	return fmt.Sprintf("OPEN ver=%d AS=%d hold=%ds ID=%s caps=%d",
		o.Version, o.MyAS, o.HoldTime, o.BGPID.String(), len(o.Capabilities()))
}

// Encode serializes the OPEN message body (without header) to the wire.
func (o *OpenMsg) Encode() ([]byte, error) {
	// Estimate size: 10 (fixed) + opt params.
	optRaw, err := o.encodeOptParms()
	if err != nil {
		return nil, err
	}
	total := 10 + len(optRaw)
	buf := make([]byte, total)
	buf[0] = o.Version
	binary.BigEndian.PutUint16(buf[1:3], o.MyAS)
	binary.BigEndian.PutUint16(buf[3:5], o.HoldTime)
	copy(buf[5:9], o.BGPID.To4())
	buf[9] = uint8(len(optRaw))
	copy(buf[10:], optRaw)
	return buf, nil
}

func (o *OpenMsg) encodeOptParms() ([]byte, error) {
	if len(o.OptParms) == 0 {
		return nil, nil
	}
	var raw []byte
	for _, p := range o.OptParms {
		if p.Length > 255 {
			return nil, fmt.Errorf("opt parm type %d too long: %d", p.Type, p.Length)
		}
		raw = append(raw, p.Type, p.Length)
		raw = append(raw, p.Value...)
	}
	if len(raw) > 255 {
		return nil, fmt.Errorf("total opt parms too long: %d (max 255)", len(raw))
	}
	return raw, nil
}

// Write sends a BGP OPEN message over the wire with proper header.
func (o *OpenMsg) Write(w io.Writer) error {
	body, err := o.Encode()
	if err != nil {
		return err
	}
	h := Header{
		Length: uint16(19 + len(body)),
		Type:   MsgOpen,
	}
	if err := h.Write(w); err != nil {
		return err
	}
	_, err = w.Write(body)
	return err
}
