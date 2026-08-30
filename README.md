# Dagg — website

Brand-native site for Dagg, the AI-Native Transformation Platform.
WorkGraph · Dagg Factory · DIS/KRAG. Single self-contained `index.html`.

Source of truth: private `founder-os` repo (`sites/dagg/`).

## Golden-standard preview

Run the revision-safe preview command below. It serves every HTML, CSS, JavaScript and image response with no-store headers, exposes the exact Git revision and dirty state at `/__revision`, and injects the same revision into each served HTML document as `<meta name="dagg-revision">`. Do not review the site through another static server.

```
python3 tools/serve_preview.py --port 8912
```

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
response, response headers and `evidence/P0/result.json` into `evidence/P0/`.
