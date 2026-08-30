# Dagg — website

Brand-native site for Dagg, the AI-Native Transformation Platform.
WorkGraph · Dagg Factory · DIS/KRAG. Single self-contained `index.html`.

Source of truth: private `founder-os` repo (`sites/dagg/`).

## Golden-standard preview

Run the immutable preview command below. At startup it freezes every served HTML, CSS, JavaScript, font and image into one in-memory snapshot, computes a deterministic snapshot ID and exposes the commit, dirty state and snapshot ID at `/__revision`, in response headers and in invisible HTML metadata. A running preview never reads changed source bytes from disk. Restart it after every source change and do not review the site through another static server.

```
python3 tools/serve_preview.py --port 8912
```

The terminal prints the snapshot ID. Record it with the full commit hash and dirty state in every review. If two screenshots do not carry the same snapshot ID, they are not comparable.

Then open `http://127.0.0.1:8912/preview/directions/a-plus.html`. Use `--port` to
choose another port and `--host` to change the interface; the default binds
loopback only. Always record both the full hash and the dirty state from
`http://127.0.0.1:8912/__revision` when reporting a preview review.

Tests and evidence:

```
python3 -B -m unittest discover -s tests -v
python3 -B tools/capture_preview_evidence.py
```

The capture harness starts the same server, drives the installed Google Chrome
over the Chrome DevTools Protocol and writes screenshots, the revision
response, response headers and `evidence/P0R1/result.json` into `evidence/P0R1/`.
