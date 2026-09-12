# P0R2 · Make snapshot acquisition consistency-safe

Status: ready  
Authority: `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md`  
Base commit: `9e0a670a9689a16ce4641c86b5e92a320da0e9f6`  
Gate type: operating acceptance by Codex

## 1. Objective

Close the final P0R1 race. P0R1 keeps served bytes immutable after startup, but it reads Git status once and then reads files sequentially. An external writer can therefore change the workspace during acquisition and produce a snapshot whose bytes do not match the recorded dirty state or do not represent one stable acquisition.

P0R2 is accepted only when the server binds after two consecutive complete acquisition passes agree exactly. A changing workspace is retried a bounded number of times and then refused; it is never silently snapshotted.

## 2. Final visible copy

Add one sentence after the immutable-preview paragraph in README:

> Before opening the port, the server reads the complete snapshot twice and starts only when both passes agree; if files are changing continuously, startup fails instead of producing mixed evidence.

No other visible copy changes.

## 3. Authoritative inputs

- Corrected masterplan supplied by Codex.
- This package file.
- P0R1 implementation at `9e0a670a9689a16ce4641c86b5e92a320da0e9f6`.
- P0 and P0R1 rejection records.

Record SHA-256 and byte sizes for the masterplan, P0R1 package, this package and the three implementation files before the first implementation write. Preserve the three authority files during Claude execution.

## 4. Files owned

Only these paths may be created or changed:

- `README.md` — the one sentence in section 2 only.
- `design/golden-standard/DAGG-GOLDEN-STANDARD-MASTERPLAN.md` — supplied bytes unchanged.
- `design/golden-standard/packages/P0R1-IMMUTABLE-PREVIEW-SNAPSHOT.md` — supplied rejected status unchanged.
- `design/golden-standard/packages/P0R2-CONSISTENT-SNAPSHOT-ACQUISITION.md` — unchanged.
- `tools/serve_preview.py`
- `tools/capture_preview_evidence.py`
- `tests/test_preview_revision.py`
- `evidence/P0R1/REJECTED-BY-CODEX.md`
- `evidence/P0R2/**`

Do not change any public site, preview or asset file. Do not push, deploy, publish, amend earlier commits or start P1.

## 5. Consistent-acquisition contract

One **complete acquisition pass** returns an immutable value containing:

- full commit, abbreviated commit and branch;
- raw `git status --porcelain` bytes and derived dirty count;
- the sorted candidate-path list after exclusions;
- frozen path → bytes map;
- skipped paths;
- snapshot ID, file count and byte count.

The server performs consecutive passes before binding:

1. Run pass A.
2. Run pass B immediately.
3. Accept only if commit, branch, raw status, candidate path set, skipped path set, file count, byte count, snapshot ID and every frozen byte agree. Equality of snapshot ID is necessary but compare the declared metadata too.
4. If A and B differ, discard both and retry the pair from scratch.
5. Permit at most three pair attempts. If no pair agrees, raise `SnapshotError` with a concise changing-workspace message and exit non-zero before binding or printing `LISTENING`.

The accepted revision metadata comes from the accepted pass, not an earlier read. `/__revision` adds:

- `snapshotConsistencyPasses: 2`;
- `snapshotAcquisitionAttempts: N`;
- `snapshotAcquisitionStable: true`.

The stderr startup summary includes `stable after N attempt(s)`.

## 6. Executable acceptance tests

Retain every P0R1 test and add direct tests for the acquisition gap:

1. A stable throwaway repository succeeds on the first pair and reports two consistency passes, one acquisition attempt and stable true.
2. Deterministically mutate a tracked file after pass A but before pass B. The pair must be rejected. Once the writer stops, the next pair is accepted and contains only the final bytes/status.
3. Deterministically change Git dirty state between A and B while restoring identical served bytes. The mismatch must still be rejected because raw status changed.
4. Simulate continuous change for all three attempts. Acquisition raises `SnapshotError`; no server socket is created and no `LISTENING` line can be emitted.
5. Independently recompute the accepted snapshot ID and compare the accepted path bytes.
6. Re-run post-start mutation/restart tests to prove P0R1 behavior remains intact.
7. `/__revision`, all content-type response headers and all HTML meta remain on one accepted snapshot ID.
8. Startup remains under two seconds for the current 20–25 MB repository despite the second pass.
9. Only owned files differ from base; public sources remain byte-identical.

The race tests must be deterministic. Do not rely on timing sleeps. Use a controlled function seam or a mock around one complete acquisition pass so the test changes the throwaway repository exactly between passes while the production path remains unchanged.

## 7. Evidence

Write `evidence/P0R2/` with:

- test output and machine-readable results;
- immutable snapshot ID, consistency pass count and acquisition attempts;
- `/__revision`, response headers and DOM meta;
- 1440 and 390 full-page screenshots from one accepted server process;
- start/before-commit control hashes;
- deviations and unmeasured fields stated honestly.

The pre-commit evidence snapshot must reproduce on the clean post-commit server exactly as P0R1 specifies. Evidence remains excluded from the snapshot set.

## 8. Stop conditions

Stop before commit if:

- a single acquisition pass can be accepted without a matching second pass;
- status and bytes are captured from different accepted passes;
- a retry can combine part of a rejected pass with a later pass;
- continuous change can produce `LISTENING`;
- any race test depends on luck or elapsed timing;
- startup exceeds two seconds;
- a public site file changes.

## 9. Completion report

Return deviations first, then:

1. correction commit and owned files;
2. direct evidence that a one-time race retries and continuous change refuses;
3. pre-commit snapshot ID and evidence paths;
4. post-commit clean commit, dirty state and reproduced snapshot ID;
5. independent test command and results;
6. what is ready for Codex acceptance.

Do not call P0R2 complete from passing steady-state tests alone.
