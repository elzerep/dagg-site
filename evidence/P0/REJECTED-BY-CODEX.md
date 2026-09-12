# P0 operating acceptance

Status: rejected by Codex.

Reason: the server froze commit and dirty metadata at startup but continued reading live source files on every request. A running review session could therefore serve HTML from one workspace moment and CSS, JavaScript or images from another. No-store headers prevent browser cache reuse; they do not make the served workspace immutable.

The acceptance test named `freshBytesAfterChange` proved the defect by treating changed response bytes without server restart as a pass. P0R1 replaces that behavior with one deterministic, immutable path-and-byte snapshot per server process.
