# minibgp — Minimal BGP Speaker

A minimal BGP speaker built to learn Go through a familiar domain (Juniper TAC → SWE).

**RFC 4271** wire protocol: OPEN, KEEPALIVE handshake + periodic keepalives. UPDATE and NOTIFICATION are stubs for later.

## Project Structure

```
minibgp/
├── main.go              # CLI entrypoint: dial peer, auto-reconnect, event loop
├── Dockerfile           # Alpine-based image with minibgp + testpeer
├── go.mod               # module github.com/luke0628/minibgp (Go 1.23)
├── cmd/testpeer/
│   └── main.go          # Fake BGP peer for local testing (listens :179)
└── pkg/
    ├── bgp/
    │   ├── types.go     # Header, marker, consts (MsgOpen=1, MsgKeepalive=4)
    │   ├── open.go      # OPEN message encode/decode + capability parsing
    │   └── keepalive.go # KEEPALIVE message (19-byte header only)
    └── peer/
        └── peer.go      # Session FSM: IDLE→CONNECT→OPEN_SENT→OPEN_CONFIRM→ESTABLISHED
```

## Key Design

| Component | What it does |
|-----------|-------------|
| `bgp.Header` | 19-byte wire header: 16B marker (all 0xff), 2B length, 1B type |
| `bgp.OpenMsg` | Version=4, MyAS, HoldTime, BGP ID, optional capabilities (TLV) |
| `bgp.KeepaliveMsg` | Empty body — 19B header only, sent every HoldTime/3 |
| `peer.Peer` | Goroutine-based session: keepalive loop + read loop, event channel |
| `testpeer` | Listens :179, hardcoded AS 65002 / Router-ID 10.0.0.254 |

**Concurrency model:** Each peer spawns two goroutines after establishing the session:
1. `keepaliveLoop` — sends KEEPALIVE every HoldTime/3 seconds
2. `readLoop` — reads and dispatches incoming BGP messages

Events (STATE, OPEN, KEEPALIVE, ERROR, CLOSED) are pushed to a buffered channel. Caller ranges over `Peer.Events()` in its own goroutine.

**Auto-reconnect:** `main.go` runs a reconnect loop — on session close, waits 5s and re-dials.

## Usage

### Quick Start (localhost loop)

```bash
# Terminal 1: start test peer (needs sudo for port 179)
sudo go run ./cmd/testpeer

# Terminal 2: connect
go run . --local-as=65001 --router-id=10.0.0.1 127.0.0.1
```

Output:
```
Connecting to 127.0.0.1:179 (AS=65001, ID=10.0.0.1)...
STATE: IDLE → CONNECT
STATE: CONNECT → OPEN_SENT
PEER OPEN: OPEN ver=4 AS=65002 hold=90s ID=10.0.0.254 caps=0
STATE: OPEN_SENT → OPEN_CONFIRM
STATE: OPEN_CONFIRM → ESTABLISHED
KEEPALIVE received   (every ~30s)
```

### With a real BGP peer

```bash
go run . --local-as=65001 --router-id=10.0.0.1 192.168.1.1
```

### Docker

```bash
# Build binaries (static, CGO_ENABLED=0)
GOOS=linux CGO_ENABLED=0 go build -o minibgp .
GOOS=linux CGO_ENABLED=0 go build -o testpeer ./cmd/testpeer

# Build image
docker build -t minibgp .

# Run testpeer in container
docker run --rm --network host minibgp testpeer
```

## Future

- [ ] UPDATE message: NLRI encoding, path attributes
- [ ] NOTIFICATION: proper error codes
- [ ] 4-byte ASN support (Cap4OctetAS)
- [ ] kind cluster: multi-node BGP mesh
- [ ] GoBGP interop testing
- [ ] Route reflection / policy
