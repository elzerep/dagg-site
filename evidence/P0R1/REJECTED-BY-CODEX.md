# P0R1 operating acceptance

Status: rejected by Codex.

Reason: P0R1 made the running server immutable, but snapshot acquisition remained sequential and unchecked. Git commit/dirty metadata was read before the file map, and the file map was read only once. A concurrent writer during startup could therefore produce bytes inconsistent with the recorded status or combine different acquisition moments before the socket bound.

P0R2 requires two identical complete passes, bounded retry and refusal under continuous change.
