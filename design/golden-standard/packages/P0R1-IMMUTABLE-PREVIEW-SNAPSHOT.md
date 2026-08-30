# P0R1 · Make the preview an immutable workspace snapshot

Status: ready  
Authority: `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Base commit: `972700bf95641bb6615a72d859fdd037329cbc86`  
Gate type: operating acceptance by Codex

## 1. Objective

Correct the rejected P0 preview model. One running preview process must serve one immutable path-and-byte snapshot. HTML, CSS, JavaScript, fonts and images can never come from different workspace moments, including when the working tree is dirty.

P0R1 is accepted only when:

- every served file is frozen in memory before the server announces `LISTENING`;
- a deterministic SHA-256 snapshot ID identifies the complete served file set;
- `/__revision`, every response header and every served HTML document expose the same snapshot ID;
- changing, deleting or creating source files after server start cannot affect that running server;
- restarting the server produces a new snapshot when the served set changed;
- the final clean post-commit run reproduces the evidence snapshot ID because `evidence/` is excluded from the served set;
- no public design, copy, IA, interaction or asset changes.

## 2. Final visible copy — use verbatim

Replace the current README explanation under **Golden-standard preview** with:

> Run the immutable preview command below. At startup it freezes every served HTML, CSS, JavaScript, font and image into one in-memory snapshot, computes a deterministic snapshot ID and exposes the commit, dirty state and snapshot ID at `/__revision`, in response headers and in invisible HTML metadata. A running preview never reads changed source bytes from disk. Restart it after every source change and do not review the site through another static server.

Add immediately after the command:

> The terminal prints the snapshot ID. Record it with the full commit hash and dirty state in every review. If two screenshots do not carry the same snapshot ID, they are not comparable.

No other visible copy changes.

## 3. Authoritative inputs

- `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`, including the corrected exact-snapshot contract.
- This package file.
- P0 rejection evidence and implementation at base commit `972700bf95641bb6615a72d859fdd037329cbc86`.
- The public preview and asset bytes at the base commit.

Before the first implementation write, record SHA-256 and byte size for the masterplan, this package, the rejected P0 package and the three P0 Python files. Recompute before commit. The masterplan and package files must remain unchanged during Claude execution.

## 4. Files owned by this package

Only these paths may be created or changed:

- `README.md` — immutable-preview instructions only.
- `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md` — include the supplied corrected bytes unchanged.
- `design/golden-standard/packages/P0-RECONCILE-AND-PREVIEW.md` — include the supplied rejected/superseded status unchanged.
- `design/golden-standard/packages/P0R1-IMMUTABLE-PREVIEW-SNAPSHOT.md` — include unchanged.
- `tools/serve_preview.py`
- `tools/capture_preview_evidence.py`
- `tests/test_preview_revision.py`
- `evidence/P0/REJECTED-BY-CODEX.md`
- `evidence/P0R1/**`

If another file is required, stop and report. Do not widen scope silently.

## 5. Immutable files and decisions

Do not change:

- anything under `preview/`, `assets/`, `marketing/` or `v1/`;
- root public HTML/CSS/JavaScript or images;
- the navigation, copy, palette, type, grid, motion or image grammar;
- the authority notes accepted in P0;
- `CLAUDE.md`, the package template, reference audits or Decision Field image;
- Git history before the correction commit;
- the branch name.

Do not push, deploy, publish, amend P0 or start P1.

## 6. Snapshot definition

The served file set is resolved once, before binding or announcing the server:

1. Start from `git ls-files --cached --others --exclude-standard -z` at the selected repository root.
2. Normalize each path to a repository-relative POSIX path and sort by its UTF-8 byte sequence.
3. Exclude `.git/**`, `evidence/**`, `**/__pycache__/**`, `**/*.pyc` and `.DS_Store` from the served set. Evidence is excluded to avoid self-reference and because it is not website content.
4. Reject paths that escape the repository. A symlink may be snapshotted only if its resolved target is a regular file inside the repository; otherwise startup fails clearly.
5. Read every file byte before `LISTENING`; keep the path → bytes map in memory for the server lifetime. Do not reopen a served source path after startup.
6. Compute `snapshotId` as lowercase hex SHA-256 over every sorted entry using this unambiguous framing:
   - eight-byte big-endian path-byte length;
   - UTF-8 path bytes;
   - eight-byte big-endian content-byte length;
   - content bytes.

Record `snapshotFileCount` and `snapshotByteCount` alongside the ID.

## 7. Behavior and technical contract

- `/__revision` returns full commit, abbreviated commit, branch, dirty Boolean at snapshot start, server start timestamp, repository root, `snapshotId`, `snapshotFileCount` and `snapshotByteCount`.
- Every response, including errors and directory indexes, carries `X-Dagg-Revision`, `X-Dagg-Dirty` and `X-Dagg-Snapshot` plus the P0 no-store headers.
- Served HTML contains exactly one each of `meta[name="dagg-revision"]`, `meta[name="dagg-dirty"]` and `meta[name="dagg-snapshot"]`, injected in memory.
- `assetRevision` in evidence equals `snapshotId`, never merely the commit hash for a dirty capture.
- Directory indexes are derived from the frozen path map, not the live filesystem.
- A file created after startup returns 404 until restart. A snapshotted file changed or deleted after startup continues returning its frozen bytes until restart.
- Add `--repo-root` so the immutable behavior can be tested in a throwaway Git repository without mutating the Dagg worktree. Default remains the real repository discovered from the script path.
- Keep loopback binding, traversal refusal, query-string/space handling, standard-library-only implementation and startup under two seconds.
- The server startup line and stderr summary include the abbreviated commit, dirty state and abbreviated snapshot ID.
- The evidence capture harness uses one server process for `/__revision`, all response headers, DOM and both screenshots.

## 8. Executable acceptance tests

The test suite must independently prove:

1. `/__revision` includes every required commit and snapshot field.
2. HTML, linked CSS, JavaScript, raster image and JSON carry the same `X-Dagg-Snapshot` value as `/__revision.snapshotId`.
3. HTML contains exactly one revision, dirty and snapshot meta tag, all inside `<head>`.
4. Removing only the three injected meta tags restores the snapshotted source HTML byte-for-byte.
5. The snapshot ID recomputed in the test from the declared framed algorithm equals the server ID.
6. In a throwaway repository, changing a served CSS file after startup does not change its response bytes or snapshot ID.
7. In that same running server, deleting a snapshotted image does not make it disappear and creating a new file does not make it available.
8. Restarting after those changes serves the new CSS bytes, returns 404 for the deleted image, serves the new file and produces a different snapshot ID.
9. Evidence files created after startup do not affect the snapshot ID after restart because `evidence/**` is excluded.
10. Dirty state is truthful at snapshot start for clean and dirty throwaway repositories.
11. Required no-store headers remain on HTML, CSS, JavaScript, image and JSON.
12. Traversal is refused; spaces, query strings and directory indexes work from the snapshot.
13. Server exceptions are zero.
14. Startup is under two seconds on the current repository.
15. `git diff --name-only 972700bf95641bb6615a72d859fdd037329cbc86...HEAD` contains only owned files and no public source path differs.

Delete all `__pycache__` and `.pyc` artifacts before staging. Do not add a broad `.gitignore` in this package.

## 9. Required visual and machine evidence

Write to `evidence/P0R1/`:

- `result.json` with commit-at-capture, dirty state, snapshot ID, asset revision, file/byte counts and every test result;
- full-page screenshots at 1440 and 390 px from the same server process;
- saved `/__revision` response;
- saved relevant `<head>` DOM snapshot;
- response headers for HTML, CSS, JavaScript, raster image and JSON;
- DOM metadata for both viewports;
- control hashes at start and before commit;
- deviations first, including the existing favicon 404 and placeholder links without false passes.

The capture harness must verify every screenshot record uses the same snapshot ID and must reject capture if a response header disagrees.

After the single local correction commit, run the full suite on the clean tree and start the server once more. The clean server must report the new commit, `dirty: false` and the same `snapshotId` stored in the pre-commit evidence. This post-commit output is reported to Codex; do not create a self-referential evidence rewrite or a second commit.

## 10. Stop conditions

Stop before commit if:

- any response can still change because a source file changed after startup;
- snapshot computation is lazy or request-time;
- evidence, Git internals or cache files enter the snapshot set;
- a public source file changes;
- the clean post-commit snapshot cannot be predicted from the pre-commit snapshot because implementation files changed after capture;
- a new third-party dependency is required;
- any test requires destructive Git history manipulation.

## 11. Required completion report

Return in this order:

1. Deviations or failures first.
2. Exact correction commit and files changed.
3. Pre-commit evidence snapshot ID and exact paths.
4. Post-commit clean revision, dirty state and reproduced snapshot ID.
5. Tests run and what each covers.
6. What is ready for Codex operating acceptance.

Do not call P0R1 complete until the immutable-after-start behavior, restart behavior and post-commit snapshot reproduction all have direct evidence.
