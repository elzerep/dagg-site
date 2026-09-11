#!/usr/bin/env python3
"""Validate an existing FS5 package without starting a server or browser."""

from __future__ import annotations

import hashlib
import json
import os
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOLS))
import capture_fs5_evidence as fs5  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_root() -> Path:
    configured = os.environ.get("DAGG_FS5_EVIDENCE_DIR")
    return (Path(configured) if configured else fs5.DEFAULT_OUTPUT).resolve()


def applicable_fixture(rendered: bool):
    manifest = {"units": [
        {"route": "home", "sectionAnchorValue": "hero",
         "dataCopyRef": "home.common", "dataCopyKind": "body",
         "dataCopyScope": "default", "multiplicity": 1,
         "accessibleAttribute": False, "exactText": "Common"},
        {"route": "home", "sectionAnchorValue": "hero",
         "dataCopyRef": "home.nojs", "dataCopyKind": "body",
         "dataCopyScope": "default", "multiplicity": 1,
         "accessibleAttribute": False, "applicableState": "no-js",
         "exactText": "No JS"}]}
    actual = {"nestedRefs": [], "unscoped": [], "uncoveredShell": [],
              "uncoveredAccessible": [], "textOwners": [],
              "accessibleOwners": [], "units": [
                  {"route": "home", "ref": "home.common", "kind": "body",
                   "scope": "default", "section": "hero", "state": None,
                   "attributes": {}, "text": "Common", "rendered": True},
                  {"route": "home", "ref": "home.nojs", "kind": "body",
                   "scope": "default", "section": "hero", "state": None,
                   "attributes": {}, "text": "No JS", "rendered": rendered}]}
    return manifest, actual


class ContractUnitTests(unittest.TestCase):
    """Pure contract checks used for a browser-free implementation smoke."""

    def test_contract_cardinality(self):
        self.assertEqual(8, len(fs5.ROUTES))
        self.assertEqual(9, len(fs5.VIEWPORTS))
        self.assertEqual(72, fs5.EXPECTED_MATRIX_ROWS)
        self.assertEqual(72, len({(r[0], v) for r in fs5.ROUTES for v in fs5.VIEWPORTS}))

    def test_required_outputs_are_unique(self):
        self.assertEqual(len(fs5.REQUIRED_OUTPUTS), len(set(fs5.REQUIRED_OUTPUTS)))
        self.assertIn("failures.json", fs5.REQUIRED_OUTPUTS)
        self.assertIn("screenshots-manifest.json", fs5.REQUIRED_OUTPUTS)

    def test_route_paths_are_unique_and_absolute(self):
        paths = [p for _, p, _ in fs5.ROUTES]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(all(p.startswith("/") and p.endswith("/") for p in paths))

    def test_first_view_contracts_cover_every_authoritative_route_viewport(self):
        expected = {(route, viewport) for route, _, _ in fs5.ROUTES
                    for viewport in fs5.FIRST_VIEWPORTS}
        self.assertEqual(expected, set(fs5.FIRST_VIEW_CONTRACTS))

    def test_first_view_selectors_are_unique_and_have_no_commas(self):
        for key, contract in fs5.FIRST_VIEW_CONTRACTS.items():
            ids = [item["id"] for item in contract]
            selectors = [selector for item in contract
                         for selector in item.get("selectors", [item.get("selector")])]
            self.assertEqual(len(ids), len(set(ids)), key)
            self.assertEqual(len(selectors), len(set(selectors)), key)
            self.assertTrue(all(selector and "," not in selector
                                for selector in selectors),
                            (key, selectors))
            for item in contract:
                self.assertIn(item["mode"],
                              {"full", "start44", "all-full", "any-full"})
                if item["mode"] == "all-full":
                    self.assertIsInstance(item.get("count"), int, (key, item))
                    self.assertGreater(item["count"], 0, (key, item))

    def test_home_mobile_image_uses_top_edge_semantics(self):
        contract = fs5.FIRST_VIEW_CONTRACTS[("home", (390, 844))]
        image = next(item for item in contract
                     if item["id"] == "home-hero-image")
        self.assertEqual("start44", image["mode"])
        for viewport in ((1440, 900), (1024, 768)):
            contract = fs5.FIRST_VIEW_CONTRACTS[("home", viewport)]
            image = next(item for item in contract
                         if item["id"] == "home-hero-image")
            self.assertEqual("full", image["mode"])

    def test_build_first_view_uses_opening_stage_not_factory_progress(self):
        for viewport in fs5.FIRST_VIEWPORTS:
            selectors = [selector
                         for item in fs5.FIRST_VIEW_CONTRACTS[("build", viewport)]
                         for selector in item.get("selectors", [item.get("selector")])]
            self.assertIn("[data-build-opening-stage]", selectors)
            self.assertNotIn("[data-build-factory-progress]", selectors)

    def test_build_mobile_requires_approved_and_one_downstream_row(self):
        contract = fs5.FIRST_VIEW_CONTRACTS[("build", (390, 844))]
        row_ids = [item["id"] for item in contract
                   if item["id"].startswith("build-opening-") and
                   item["id"] != "build-opening-stage"]
        self.assertEqual(["build-opening-approved",
                          "build-opening-evaluation-or-review"], row_ids)

    def test_h1_line_limits_are_route_specific_and_integer(self):
        expected = {
            "home": (2, 2, 4),
            "transformation": (3, 4, 4),
            "workgraph": (2, 2, 5),
            "build": (4, 4, 4),
            "trust": (2, 2, 3),
            "company": (3, 3, 5),
            "assessment": (3, 3, 3),
            "impact": (2, 2, 3),
        }
        for route, limits in expected.items():
            actual = tuple(fs5.h1_line_limit(route, width)
                           for width in (1440, 1024, 390))
            self.assertEqual(limits, actual, route)
            self.assertTrue(all(isinstance(value, int) for value in actual))

    def test_home_disclosure_gate_fails_closed(self):
        valid = {"count": 1, "rendered": True,
                 "firstSyntheticRef": "home.record.identity",
                 "precedes": True}
        self.assertTrue(fs5.home_disclosure_gate(valid))
        for key, wrong in (("count", 0), ("count", 2),
                           ("rendered", False),
                           ("firstSyntheticRef", "home.execution.identity"),
                           ("precedes", False)):
            candidate = dict(valid)
            candidate[key] = wrong
            self.assertFalse(fs5.home_disclosure_gate(candidate),
                             (key, wrong))

    def test_finalizer_seals_every_non_revision_artifact(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name in fs5.REQUIRED_OUTPUTS:
                if name != "revision.json":
                    (root / name).write_text(name, encoding="utf-8")
            fs5.finalize_package(root, {
                "snapshotId": "a" * 64,
                "snapshotConsistencyPasses": 2,
            })
            revision = json.loads((root / "revision.json").read_text())
            self.assertEqual(set(fs5.REQUIRED_OUTPUTS) - {"revision.json"},
                             set(revision["artifactSha256"]))
            for name, expected in revision["artifactSha256"].items():
                self.assertEqual(expected, digest(root / name))

    def test_vendored_axe_default_has_provenance(self):
        source, metadata = fs5.resolve_axe(None)
        self.assertTrue(source)
        self.assertEqual("assets/vendor/axe-core/axe.min.js", metadata["path"])
        self.assertRegex(metadata["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual("4.13.0", metadata["version"])

    def test_lossless_png_decoder(self):
        def chunk(kind, body):
            return (struct.pack(">I", len(body)) + kind + body
                    + struct.pack(">I", zlib.crc32(kind + body) & 0xffffffff))
        png = (b"\x89PNG\r\n\x1a\n"
               + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 6, 0, 0, 0))
               + chunk(b"IDAT", zlib.compress(b"\x00\x01\x02\x03\xff"))
               + chunk(b"IEND", b""))
        with tempfile.TemporaryDirectory() as directory:
            reference = Path(directory) / "one.png"
            reference.write_bytes(png)
            width, height, channels, rows = fs5.decode_png_rgb(reference)
        self.assertEqual((1, 1, 4), (width, height, channels))
        self.assertEqual([b"\x01\x02\x03\xff"], rows)

    def test_copy_normalization_is_exact_nfc_and_whitespace_only(self):
        self.assertEqual("Café\nkeeps punctuation!",
                         fs5.normalize_copy("  Cafe\u0301\n keeps\tpunctuation!  "))
        self.assertNotEqual(fs5.normalize_copy("Case"), fs5.normalize_copy("case"))

    def test_keyed_copy_reconciliation_fails_closed(self):
        manifest = {"units": [{"route": "home",
            "dataCopyRef": "home.hero.h1", "dataCopyKind": "heading",
            "dataCopyScope": "default", "sectionAnchorValue": "hero",
            "multiplicity": 1, "accessibleAttribute": False,
            "exactText": "Exact words."}]}
        actual = {"nestedRefs": [], "unscoped": [], "uncoveredShell": [],
                  "uncoveredAccessible": [], "units": [{"route": "home",
                      "ref": "home.hero.h1", "kind": "heading",
                      "scope": "default", "section": "hero", "state": None,
                      "attributes": {},
                      "text": "Exact\twords."}]}
        self.assertTrue(fs5.reconcile_copy("home", actual, manifest)["passed"])
        actual["units"][0]["text"] = "Almost exact words."
        result = fs5.reconcile_copy("home", actual, manifest)
        self.assertFalse(result["passed"])
        self.assertEqual("home.hero.h1", result["mismatches"][0]["ref"])
        actual["units"][0]["text"] = "Exact words."
        actual["uncoveredAccessible"] = [{"tag": "BUTTON", "value": "Unowned"}]
        self.assertFalse(fs5.reconcile_copy("home", actual, manifest)["passed"])

    def test_dynamic_copy_reconciliation_accepts_declared_state(self):
        manifest = {"units": [{"route": "shared",
            "dataCopyRef": "shared.header.menu-state",
            "dataCopyKind": "functional", "dataCopyScope": "shell",
            "sectionAnchorValue": "global-header", "multiplicity": 1,
            "accessibleAttribute": False, "exactStates": [
                {"id": "closed", "text": "Menu"},
                {"id": "open", "text": "Close"}]}]}
        actual = {"nestedRefs": [], "unscoped": [], "uncoveredShell": [],
                  "uncoveredAccessible": [], "textOwners": [],
                  "accessibleOwners": [], "units": [{"route": "shared",
                      "ref": "shared.header.menu-state", "kind": "functional",
                      "scope": "shell", "section": "global-header",
                      "state": "closed", "attributes": {}, "text": "Menu",
                      "rendered": True}]}
        self.assertTrue(fs5.reconcile_copy("home", actual, manifest)["passed"])

    def test_dynamic_copy_reconciliation_rejects_unknown_state(self):
        manifest = {"units": [{"route": "shared",
            "dataCopyRef": "shared.header.menu-state",
            "dataCopyKind": "functional", "dataCopyScope": "shell",
            "sectionAnchorValue": "global-header", "multiplicity": 1,
            "accessibleAttribute": False, "exactStates": [
                {"id": "closed", "text": "Menu"},
                {"id": "open", "text": "Close"}]}]}
        actual = {"nestedRefs": [], "unscoped": [], "uncoveredShell": [],
                  "uncoveredAccessible": [], "textOwners": [],
                  "accessibleOwners": [], "units": [{"route": "shared",
                      "ref": "shared.header.menu-state", "kind": "functional",
                      "scope": "shell", "section": "global-header",
                      "state": "opening", "attributes": {}, "text": "Menu",
                      "rendered": True}]}
        result = fs5.reconcile_copy("home", actual, manifest)
        self.assertFalse(result["passed"])
        self.assertEqual(
            {"expected": True, "actual": False},
            result["mismatches"][0]["fields"]["state"],
        )

    def test_script_disabled_dom_snapshot_reconstructs_keyed_copy(self):
        strings = ["#document", "HTML", "BODY", "MAIN", "data-home", "",
                   "SECTION", "data-home-act", "hero", "P", "data-copy-ref",
                   "home.hero.no-js", "data-copy-kind", "body",
                   "data-copy-scope", "default", "#text", "Exact no JS."]
        snapshot = {"strings": strings, "documents": [{
            "nodes": {"nodeName": [0, 1, 2, 3, 6, 9, 16],
                      "nodeValue": [5, 5, 5, 5, 5, 5, 17],
                      "parentIndex": [-1, 0, 1, 2, 3, 4, 5],
                      "attributes": [[], [], [], [4, 5], [7, 8],
                                     [10, 11, 12, 13, 14, 15], []]},
            "layout": {"nodeIndex": [1, 2, 3, 4, 5, 6]}}]}
        copy = fs5.copy_from_dom_snapshot(snapshot)
        manifest = {"units": [{"route": "home",
            "sectionAnchorValue": "hero", "dataCopyRef": "home.hero.no-js",
            "dataCopyKind": "body", "dataCopyScope": "default",
            "multiplicity": 1, "accessibleAttribute": False,
            "applicableState": "no-js", "exactText": "Exact no JS."}]}
        result = fs5.reconcile_copy("home", copy, manifest,
                                    applicable_states={"no-js"})
        self.assertTrue(result["passed"], result)

    def test_dom_snapshot_classifies_skip_link_as_shared_shell(self):
        strings = ["#document", "HTML", "BODY", "A", "class", "skip-link",
                   "data-copy-section", "global-header", "data-copy-ref",
                   "shared.header.skip-link", "data-copy-kind", "functional",
                   "data-copy-scope", "shell", "#text", "Skip to content", ""]
        snapshot = {"strings": strings, "documents": [{
            "nodes": {"nodeName": [0, 1, 2, 3, 14],
                      "nodeValue": [16, 16, 16, 16, 15],
                      "parentIndex": [-1, 0, 1, 2, 3],
                      "attributes": [[], [], [],
                                     [4, 5, 6, 7, 8, 9, 10, 11, 12, 13], []]},
            "layout": {"nodeIndex": [1, 2, 3, 4]}}]}
        copy = fs5.copy_from_dom_snapshot(snapshot)
        self.assertEqual("shared", copy["units"][0]["route"])
        self.assertEqual("global-header", copy["units"][0]["section"])
        self.assertEqual([], copy["uncoveredShell"])

    def test_dom_snapshot_does_not_promote_hidden_child_attributes(self):
        strings = ["#document", "HTML", "BODY", "MAIN", "BUTTON",
                   "aria-label", "Hidden control", ""]
        snapshot = {"strings": strings, "documents": [{
            "nodes": {"nodeName": [0, 1, 2, 3, 4],
                      "nodeValue": [7, 7, 7, 7, 7],
                      "parentIndex": [-1, 0, 1, 2, 3],
                      "attributes": [[], [], [], [], [5, 6]]},
            # The MAIN has layout, but its BUTTON child does not.
            "layout": {"nodeIndex": [1, 2, 3]}}]}
        copy = fs5.copy_from_dom_snapshot(snapshot)
        self.assertEqual([], copy["accessibleOwners"])
        self.assertEqual([], copy["uncoveredAccessible"])

    def test_dom_snapshot_accessible_attributes_require_local_markers(self):
        strings = ["#document", "HTML", "BODY", "MAIN", "DIV", "BUTTON",
                   "data-copy-ref", "home.panel", "data-copy-kind", "body",
                   "data-copy-scope", "default", "data-home", "",
                   "data-home-act", "hero", "aria-label", "Child action"]
        snapshot = {"strings": strings, "documents": [{
            "nodes": {"nodeName": [0, 1, 2, 3, 4, 5],
                      "nodeValue": [13, 13, 13, 13, 13, 13],
                      "parentIndex": [-1, 0, 1, 2, 3, 4],
                      "attributes": [[], [], [], [12, 13], [14, 15, 6, 7,
                                                           8, 9, 10, 11],
                                     [16, 17]]},
            "layout": {"nodeIndex": [1, 2, 3, 4, 5]}}]}
        copy = fs5.copy_from_dom_snapshot(snapshot)
        self.assertEqual(1, len(copy["accessibleOwners"]))
        self.assertIsNone(copy["accessibleOwners"][0]["ownerRef"])
        self.assertEqual(copy["accessibleOwners"], copy["uncoveredAccessible"])

    def test_applicable_copy_states_are_exact_and_unknown_refs_still_fail(self):
        def wanted(ref, text, state=None):
            unit = {"route": "home", "sectionAnchorValue": "hero",
                    "dataCopyRef": ref, "dataCopyKind": "body",
                    "dataCopyScope": "default", "multiplicity": 1,
                    "accessibleAttribute": False, "exactText": text}
            if state:
                unit["applicableState"] = state
            return unit
        units = [wanted("home.common", "Common"),
                 wanted("home.nojs", "No JS", "no-js"),
                 wanted("home.success", "Success", "local-preview-success"),
                 wanted("home.menu", "Menu", "separate-responsive-menu-layer")]
        actual = {"nestedRefs": [], "unscoped": [], "uncoveredShell": [],
                  "uncoveredAccessible": [], "textOwners": [],
                  "accessibleOwners": [], "units": [
                      {"route": "home", "ref": u["dataCopyRef"],
                       "kind": "body", "scope": "default", "section": "hero",
                       "state": None, "attributes": {}, "text": u["exactText"]}
                      for u in units]}
        by_ref = {u["ref"]: u for u in actual["units"]}
        by_ref["home.common"]["rendered"] = True
        for ref in ("home.nojs", "home.success", "home.menu"):
            by_ref[ref]["rendered"] = False
        manifest = {"units": units}
        self.assertTrue(fs5.reconcile_copy("home", actual, manifest)["passed"])
        by_ref["home.nojs"]["rendered"] = True
        self.assertTrue(fs5.reconcile_copy(
            "home", actual, manifest, {"no-js"})["passed"])
        by_ref["home.nojs"]["rendered"] = False
        by_ref["home.success"]["rendered"] = True
        self.assertTrue(fs5.reconcile_copy(
            "home", actual, manifest, {"local-preview-success"})["passed"])
        by_ref["home.success"]["rendered"] = False
        actual["units"].append({"route": "home", "ref": "home.unknown",
            "kind": "body", "scope": "default", "section": "hero",
            "state": None, "attributes": {}, "text": "Unknown",
            "rendered": True})
        self.assertFalse(fs5.reconcile_copy("home", actual, manifest)["passed"])

    def test_unknown_requested_applicable_state_fails_closed(self):
        manifest, _ = applicable_fixture(False)
        with self.assertRaises(fs5.FS5Failure):
            fs5.declared_applicable_states(manifest, "home", {"no-jz"})

    def test_visible_inactive_applicable_unit_is_rejected(self):
        manifest, actual = applicable_fixture(True)
        actual["units"][1]["text"] = "Leaked and wrong"
        result = fs5.reconcile_copy("home", actual, manifest)
        self.assertFalse(result["passed"])
        self.assertEqual("home.nojs", result["visibleInactiveRefs"][0]["ref"])

    def test_hidden_inactive_applicable_unit_is_allowed(self):
        manifest, actual = applicable_fixture(False)
        result = fs5.reconcile_copy("home", actual, manifest)
        self.assertTrue(result["passed"], result)
        self.assertEqual([], result["visibleInactiveRefs"])

    def test_hidden_active_no_js_unit_is_rejected(self):
        manifest, actual = applicable_fixture(False)
        result = fs5.reconcile_copy("home", actual, manifest, {"no-js"})
        self.assertFalse(result["passed"])
        mismatch = next(x for x in result["mismatches"]
                        if x.get("ref") == "home.nojs")
        self.assertEqual({"expected": True, "actual": False},
                         mismatch["fields"]["rendered"])

    def test_accessible_ancestor_nesting_is_narrowly_allowed(self):
        manifest = {"units": [
            {"route": "shared", "sectionAnchorValue": "global-header",
             "dataCopyRef": "shared.nav.name", "dataCopyKind": "functional",
             "dataCopyScope": "shell", "multiplicity": 1,
             "accessibleAttribute": True, "accessibleAttributeName": "aria-label",
             "exactText": "Primary"},
            {"route": "shared", "sectionAnchorValue": "global-header",
             "dataCopyRef": "shared.nav.link", "dataCopyKind": "functional",
             "dataCopyScope": "shell", "multiplicity": 1,
             "accessibleAttribute": False, "exactText": "Transformation"}]}
        actual = {"unscoped": [], "uncoveredShell": [],
                  "uncoveredAccessible": [],
                  "nestedRefs": [{"ancestorRef": "shared.nav.name",
                                  "childRef": "shared.nav.link"}],
                  "textOwners": [{"text": "Transformation",
                                  "ownerRef": "shared.nav.link",
                                  "region": "shell"}],
                  "accessibleOwners": [{"tag": "NAV", "attribute": "aria-label",
                                        "value": "Primary",
                                        "ownerRef": "shared.nav.name"}],
                  "units": [
                      {"route": "shared", "ref": "shared.nav.name",
                       "kind": "functional", "scope": "shell",
                       "section": "global-header", "state": None,
                       "attributes": {"aria-label": ["Primary"]}, "text": ""},
                      {"route": "shared", "ref": "shared.nav.link",
                       "kind": "functional", "scope": "shell",
                       "section": "global-header", "state": None,
                       "attributes": {}, "text": "Transformation"}]}
        self.assertTrue(fs5.reconcile_copy("home", actual, manifest)["passed"])
        actual["textOwners"] = [{"text": "Unowned beneath accessible marker",
                                 "ownerRef": "shared.nav.name",
                                 "region": "shell"}]
        result = fs5.reconcile_copy("home", actual, manifest)
        self.assertFalse(result["passed"])
        self.assertTrue(result["textOwnerFailures"])
        actual["textOwners"] = [{"text": "Transformation",
                                  "ownerRef": "shared.nav.link",
                                  "region": "shell"}]
        actual["accessibleOwners"].append({
            "tag": "A", "attribute": "aria-label", "value": "Wrong owner",
            "ownerRef": "shared.nav.link"})
        result = fs5.reconcile_copy("home", actual, manifest)
        self.assertFalse(result["passed"])
        self.assertTrue(result["accessibleOwnerFailures"])

    def test_computed_accessible_name_failure_cannot_use_dom_heuristic(self):
        class BrokenCDP:
            def call(self, *args, **kwargs):
                raise RuntimeError("AX unavailable")
        class Page:
            cdp = BrokenCDP()
            session = "test"
        manifest = {"units": [{"route": "shared",
            "sectionAnchorValue": "global-header", "dataCopyRef": "shared.panel",
            "dataCopyKind": "functional", "dataCopyScope": "shell",
            "multiplicity": 1, "accessibleAttribute": True,
            "accessibleAttributeName": "computed-accessible-name",
            "exactText": "Build"}]}
        actual = {"nestedRefs": [], "unscoped": [], "uncoveredShell": [],
                  "uncoveredAccessible": [], "textOwners": [],
                  "accessibleOwners": [], "units": [{"route": "shared",
                      "ref": "shared.panel", "kind": "functional",
                      "scope": "shell", "section": "global-header",
                      "state": None,
                      "attributes": {"computed-accessible-name": ["Build"]},
                      "text": "Build"}]}
        evidence = fs5.enrich_computed_accessible_names(Page(), actual, manifest)
        self.assertFalse(evidence["passed"])
        self.assertFalse(fs5.reconcile_copy("home", actual, manifest)["passed"])

    def test_copy_manifest_binds_authority_hashes_and_state_enums(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            authority = root / "contract.md"
            authority.write_text("binding copy", encoding="utf-8")
            authority_hash = digest(authority)
            routes = {name for name, _, _ in fs5.ROUTES}
            units = []
            for name in sorted(routes | {"shared"}):
                units.append({"authorityFile": "contract.md",
                              "authorityHash": authority_hash, "route": name,
                              "sectionAnchorValue": "hero",
                              "dataCopyRef": "%s.hero.h1" % name,
                              "dataCopyKind": "heading",
                              "dataCopyScope": "shell" if name == "shared" else "default",
                              "multiplicity": 1, "accessibleAttribute": False,
                              "exactText": "Exact copy."})
            doc = {"schemaVersion": 1, "authorityHashes": {"contract.md": authority_hash},
                   "routeRoots": dict(fs5.COPY_ROUTE_ROOTS),
                   "sectionAnchorAttributes": dict(fs5.COPY_SECTION_ATTRIBUTES),
                   "units": units, "blockers": []}
            manifest = root / "COPY-UNIT-MANIFEST.json"
            manifest.write_text(json.dumps(doc), encoding="utf-8")
            original = fs5.REPO_ROOT
            try:
                fs5.REPO_ROOT = root.resolve()
                loaded, metadata = fs5.load_copy_manifest(manifest)
                self.assertEqual(9, metadata["unitCount"])
                self.assertEqual(doc, loaded)
                doc["units"][0]["multiplicity"] = True
                manifest.write_text(json.dumps(doc), encoding="utf-8")
                with self.assertRaises(fs5.FS5Failure):
                    fs5.load_copy_manifest(manifest)
                doc["units"][0]["multiplicity"] = 1
                doc["units"][0]["multiplicity"] = 0
                doc["units"][0]["exclusionReason"] = "test exclusion"
                manifest.write_text(json.dumps(doc), encoding="utf-8")
                with self.assertRaises(fs5.FS5Failure):
                    fs5.load_copy_manifest(manifest)
                doc["units"][0]["multiplicity"] = 1
                doc["units"][0].pop("exclusionReason")
                doc["blockers"] = [{"id": "unresolved-copy"}]
                manifest.write_text(json.dumps(doc), encoding="utf-8")
                with self.assertRaises(fs5.FS5Failure):
                    fs5.load_copy_manifest(manifest)
            finally:
                fs5.REPO_ROOT = original

    def test_current_copy_manifest_is_final_and_self_verified(self):
        manifest, metadata = fs5.load_copy_manifest(fs5.DEFAULT_COPY_MANIFEST)
        self.assertEqual(len(manifest["units"]), metadata["unitCount"])
        self.assertEqual(sum(bool(u["accessibleAttribute"])
                             for u in manifest["units"]),
                         metadata["accessibleUnitCount"])
        self.assertEqual(sum(u["multiplicity"] == 0
                             for u in manifest["units"]),
                         metadata["exclusionCount"])
        self.assertEqual(0, metadata["blockerCount"])
        self.assertEqual([], manifest.get("blockers"))

    def test_assessment_state_contract_is_complete(self):
        manifest = json.loads(fs5.DEFAULT_COPY_MANIFEST.read_text())
        units = {unit["dataCopyRef"]: unit for unit in manifest["units"]}
        button = units["assessment.inquiry.submit"]
        status = units["assessment.inquiry.submit-state"]
        self.assertEqual(["idle", "submitting", "duplicate"],
                         [state["id"] for state in button["exactStates"]])
        self.assertEqual([
            "idle", "validation-name", "validation-email",
            "validation-company", "validation-path", "validation-why",
            "submitting", "duplicate", "error",
        ], [state["id"] for state in status["exactStates"]])

    def test_interval_gate_requires_every_exact_interval(self):
        timeline = [{"index": 0, "at": 0}, {"index": 1, "at": 1600},
                    {"index": 2, "at": 3800}, {"index": 3, "at": 6000}]
        self.assertTrue(fs5.interval_evidence(timeline, fs5.HOME_INTERVALS_MS)["passed"])
        self.assertFalse(fs5.interval_evidence(timeline[:-1], fs5.HOME_INTERVALS_MS)["passed"])
        timeline[-1]["at"] = 7000
        self.assertFalse(fs5.interval_evidence(timeline, fs5.HOME_INTERVALS_MS)["passed"])
        factory_intervals = (1300, 1200, 1200, 1200, 1300)
        factory = [{"index": index, "at": sum(factory_intervals[:index])}
                   for index in range(len(factory_intervals) + 1)]
        self.assertTrue(fs5.factory_interval_evidence(factory)["passed"])
        too_fast = [{"index": index, "at": index * 900}
                    for index in range(6)]
        self.assertFalse(fs5.factory_interval_evidence(too_fast)["passed"])

    def test_dynamic_copy_state_coverage_requires_whole_enum(self):
        manifest = {"units": [{"route": "home", "dataCopyRef": "home.status",
                               "exactStates": [{"id": "ready", "text": "Ready"},
                                               {"id": "done", "text": "Done"}],
                               "multiplicity": 1}]}
        ready = {"route": "home", "ref": "home.status", "state": "ready",
                 "text": "Ready", "passed": True}
        self.assertFalse(fs5.copy_state_coverage(manifest, [ready])["passed"])
        done = dict(ready, state="done", text="Done")
        result = fs5.copy_state_coverage(manifest, [ready, done])
        self.assertTrue(result["passed"])
        self.assertEqual(result["required"], result["observed"])

    def test_dynamic_copy_state_coverage_honors_explicit_required_subset(self):
        manifest = {"units": [{"route": "shared", "dataCopyRef": "footer.explore",
                               "exactStates": [{"id": "gated", "text": "Gated"},
                                               {"id": "enabled", "text": "Enabled"}],
                               "fs5RequiredState": "gated", "multiplicity": 1}]}
        gated = {"route": "shared", "ref": "footer.explore", "state": "gated",
                 "text": "Gated", "passed": True}
        result = fs5.copy_state_coverage(manifest, [gated])
        self.assertTrue(result["passed"])
        self.assertEqual([["shared", "footer.explore", "gated"]], result["required"])
        enabled = dict(gated, state="enabled", text="Enabled")
        result = fs5.copy_state_coverage(manifest, [gated, enabled])
        self.assertTrue(result["passed"])
        self.assertEqual([["shared", "footer.explore", "enabled"]],
                         result["optionalObserved"])

    def test_visual_pair_metadata_has_binding_cardinality(self):
        shots = []
        for route in fs5.VISUAL_ROUTES:
            for viewport in fs5.VISUAL_VIEWPORTS:
                for kind in ("viewport", "full-page-documentation"):
                    shots.append({"route": route, "viewport": list(viewport),
                                  "lane": "base-matrix", "kind": kind,
                                  "path": "%s-%s-%s.png" % (route, viewport[0], kind),
                                  "sha256": "a" * 64})
        metadata = fs5.visual_pair_metadata(shots, "b" * 64)
        self.assertTrue(metadata["complete"])
        self.assertEqual(36, metadata["canonicalScreenshotCount"])
        self.assertEqual(12, len(metadata["breakpointContinuity"]))
        self.assertEqual(18, len(metadata["routeSilhouette"]))
        self.assertEqual(18, len(metadata["whitespaceRhythm"]))
        self.assertFalse(fs5.external_visual_review(None, metadata)["passed"])
        review = {"schemaVersion": 1, "snapshotId": metadata["snapshotId"],
                  "protocolSha256": metadata["protocolSha256"],
                  "canonicalScreenshotSha256": metadata["canonicalScreenshotSha256"],
                  "reviewer": {"kind": "human", "name": "FS5 reviewer"}}
        for category in ("breakpointContinuity", "routeSilhouette",
                         "whitespaceRhythm"):
            review[category] = [{"id": x["id"], "passed": True}
                                for x in metadata[category]]
        review["twoSecondRouteChecks"] = [
            {"route": route, "passed": True} for route in fs5.VISUAL_ROUTES]
        review["assetRenderFidelity"] = [
            {"route": route, "passed": True} for route in fs5.VISUAL_ROUTES]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "visual-review.json"
            path.write_text(json.dumps(review), encoding="utf-8")
            self.assertTrue(fs5.external_visual_review(path, metadata)["passed"])

    def test_no_unconditional_known_unimplemented_gate(self):
        self.assertFalse(hasattr(fs5, "KNOWN_UNIMPLEMENTED_GATES"))
        self.assertEqual("COPY-UNIT-MANIFEST.json", fs5.DEFAULT_COPY_MANIFEST.name)

    def test_protected_invariant_manifest_binds_assets_and_baselines(self):
        doc = json.loads(fs5.PROTECTED_INVARIANT.read_text(encoding="utf-8"))
        copy = doc["homeHero"]["copy"]
        assets = doc["homeHero"]["assets"]
        rows = []
        for viewport in fs5.VIEWPORTS:
            token = "mobile-v4.webp" if viewport[0] < 640 else "desktop-v4.webp"
            asset = next(x for x in assets if x["path"].endswith(token))
            protected = dict(copy)
            protected["image"] = {"alt": protected.pop("alt"),
                                  "currentSrc": "http://example.test/" + asset["path"],
                                  "naturalWidth": asset["width"],
                                  "naturalHeight": asset["height"]}
            rows.append({"route": "home", "viewport": list(viewport),
                         "measurement": {"protectedHome": protected}})
        result = fs5.protected_invariant_gate(rows)
        self.assertTrue(result["passed"], result)


@unittest.skipUnless(
    os.environ.get("DAGG_FS5_EVIDENCE_DIR"),
    "package validation requires DAGG_FS5_EVIDENCE_DIR; pure contract tests still ran",
)
class ExistingEvidencePackage(unittest.TestCase):
    """Every test reads only the already-promoted package named by the env."""

    @classmethod
    def setUpClass(cls):
        cls.root = evidence_root()
        if not cls.root.is_dir():
            raise AssertionError("FS5 evidence directory does not exist: %s" % cls.root)
        missing = [name for name in fs5.REQUIRED_OUTPUTS if not (cls.root / name).is_file()]
        if missing:
            raise AssertionError("FS5 package is incomplete: %s" % ", ".join(missing))
        cls.docs = {}
        for name in fs5.REQUIRED_OUTPUTS:
            if name.endswith(".json"):
                cls.docs[name] = json.loads((cls.root / name).read_text(encoding="utf-8"))
        cls.revision = cls.docs["revision.json"]
        cls.snapshot = cls.revision.get("snapshotId")

    def test_revision_and_artifact_hashes(self):
        self.assertRegex(self.snapshot or "", r"^[0-9a-f]{64}$")
        self.assertEqual(2, self.revision.get("snapshotConsistencyPasses"))
        identity = self.revision.get("servedDiskIdentity", {})
        self.assertTrue(identity.get("passed"), identity)
        self.assertEqual([], identity.get("differingFiles"))
        self.assertEqual([], identity.get("headerFailures"))
        self.assertEqual(set(fs5.REQUIRED_OUTPUTS), set(self.revision.get("requiredOutputs", [])))
        expected = self.revision.get("artifactSha256", {})
        self.assertEqual(set(fs5.REQUIRED_OUTPUTS) - {"revision.json"}, set(expected))
        for name, wanted in expected.items():
            self.assertEqual(wanted, digest(self.root / name), name)

    def test_environment_records_tool_and_reference_provenance(self):
        environment = self.docs["environment.json"]
        self.assertTrue(environment.get("passed"), environment)
        axe = environment.get("axeCore", {})
        self.assertRegex(axe.get("sha256") or "", r"^[0-9a-f]{64}$")
        self.assertTrue(axe.get("version"), axe)
        copy = environment.get("copyAuthority", {})
        self.assertEqual("design/golden-standard/narrative/COPY-UNIT-MANIFEST.json",
                         copy.get("path"))
        self.assertRegex(copy.get("sha256") or "", r"^[0-9a-f]{64}$")
        _, current_copy = fs5.load_copy_manifest(fs5.DEFAULT_COPY_MANIFEST)
        self.assertEqual(current_copy["sha256"], copy.get("sha256"))
        self.assertEqual(current_copy["unitCount"], copy.get("unitCount"))
        self.assertEqual(current_copy["accessibleUnitCount"],
                         copy.get("accessibleUnitCount"))
        self.assertEqual(current_copy["exclusionCount"],
                         copy.get("exclusionCount"))
        self.assertEqual(0, copy.get("blockerCount"))
        reference = environment.get("homeReferenceGate", {})
        self.assertTrue(reference.get("passed"), reference)
        self.assertRegex(reference.get("baselineSnapshotId") or "",
                         r"^[0-9a-f]{64}$")
        protected = environment.get("protectedInvariantGate", {})
        self.assertTrue(protected.get("passed"), protected)
        self.assertEqual(4, len(protected.get("assetRecords", [])))
        self.assertEqual(9, len(protected.get("copyRecords", [])))
        self.assertEqual(9, len(protected.get("sourceRecords", [])))
        visual = environment.get("externalVisualReview", {})
        self.assertTrue(visual.get("passed"), visual)

    def test_one_snapshot_everywhere(self):
        for name, doc in self.docs.items():
            self.assertEqual(self.snapshot, doc.get("snapshotId"), name)
        manifest = self.docs["screenshots-manifest.json"]
        for shot in manifest.get("screenshots", []):
            self.assertEqual(self.snapshot, shot.get("snapshotId"), shot)

    def test_base_matrix_is_exact_and_passing(self):
        matrix = self.docs["route-matrix.json"]
        self.assertTrue(matrix.get("passed"), matrix)
        self.assertEqual(72, matrix.get("expectedRows"))
        rows = matrix.get("rows", [])
        self.assertEqual(72, len(rows))
        actual = {(r.get("route"), tuple(r.get("viewport", []))) for r in rows}
        expected = {(r[0], v) for r in fs5.ROUTES for v in fs5.VIEWPORTS}
        self.assertEqual(expected, actual)
        self.assertTrue(all(r.get("passed") is True for r in rows))
        self.assertTrue(all(r.get("lane") == "base-matrix" for r in rows))
        self.assertTrue(all(len(r.get("screenshots", {})) == 2 for r in rows))
        for row in rows:
            keyed = [a for a in row.get("assertions", [])
                     if a.get("name") == "exact keyed copy authority"]
            self.assertEqual(1, len(keyed), row.get("id"))
            self.assertTrue(keyed[0].get("passed"), keyed[0])
            detail = keyed[0].get("detail", {})
            for field in ("textOwnerFailures", "accessibleOwnerFailures",
                          "visibleInactiveRefs", "activeApplicableStates"):
                self.assertIn(field, detail, row.get("id"))
            self.assertEqual([], detail["textOwnerFailures"])
            self.assertEqual([], detail["accessibleOwnerFailures"])
            self.assertEqual([], detail["visibleInactiveRefs"])

    def test_interaction_lanes_are_complete(self):
        doc = self.docs["interactions.json"]
        self.assertTrue(doc.get("passed"), doc)
        lanes = doc.get("lanes", [])
        names = {x.get("lane") for x in lanes}
        self.assertEqual(set(doc.get("requiredLanes", [])), names)
        self.assertTrue(all(x.get("passed") is True for x in lanes))
        self.assertIn("touch-390x844", names)
        self.assertIn("touch-768x1024", names)
        for name in ("touch-390x844", "touch-768x1024"):
            lane = next(x for x in lanes if x.get("lane") == name)
            applicable = lane.get("detail", {}).get("applicableCopy", {})
            self.assertTrue(applicable.get("passed"), applicable)
            self.assertEqual([], applicable.get("visibleInactiveRefs"))
            manifest, _ = fs5.load_copy_manifest(fs5.DEFAULT_COPY_MANIFEST)
            expected_states = sorted(fs5.declared_applicable_states(
                manifest, "home", {"separate-responsive-menu-layer"}))
            self.assertEqual(expected_states,
                             applicable.get("activeApplicableStates"))
        for route, _, _ in fs5.ROUTES:
            lane = next((x for x in lanes
                         if x.get("lane") == "route-touch-controls-%s" % route), None)
            self.assertIsNotNone(lane, route)
            self.assertEqual(lane.get("detail", {}).get("candidateCount"),
                             lane.get("detail", {}).get("seenCount"), route)
            attempts = lane.get("detail", {}).get("attempts", [])
            self.assertTrue(attempts, route)
            for attempt in attempts:
                self.assertTrue(attempt.get("passed"), attempt)
                for event in attempt.get("probe", {}).get("events", []):
                    self.assertTrue(event.get("trusted"), event)
        for name in ("home-interval-timing", "build-interval-timing",
                     "build-flyout-timing"):
            self.assertIn(name, names)
        state_coverage = doc.get("copyStateCoverage", {})
        self.assertTrue(state_coverage.get("passed"), state_coverage)
        self.assertTrue(state_coverage.get("required"), state_coverage)
        required = {tuple(x) for x in state_coverage.get("required", [])}
        observed = {tuple(x) for x in state_coverage.get("observed", [])}
        self.assertTrue(required.issubset(observed), state_coverage)
        self.assertEqual([], state_coverage.get("missing"))
        self.assertEqual([], state_coverage.get("extra"))
        self.assertEqual([], state_coverage.get("unexpected"))

    def test_resilience_lanes_are_complete(self):
        doc = self.docs["resilience.json"]
        self.assertTrue(doc.get("passed"), doc)
        lanes = doc.get("lanes", [])
        for lane, count in doc.get("expectedPerLane", {}).items():
            matching = [x for x in lanes if x.get("lane") == lane]
            self.assertEqual(count, len(matching), lane)
            self.assertTrue(all(x.get("passed") is True for x in matching), lane)
        nojs = [x for x in lanes if x.get("lane") == "true-no-js"]
        self.assertEqual(8, len(nojs))
        for row in nojs:
            measurement = row.get("measurement", {})
            self.assertGreater(measurement.get("dom", {}).get("nodeCount", 0), 0)
            self.assertGreater(measurement.get("accessibility", {}).get("nodeCount", 0), 0)
            self.assertIsInstance(row.get("screenshot"), dict)
            copy_checks = [x for x in row.get("assertions", [])
                           if x.get("name") == "exact keyed no-JS copy authority"]
            self.assertEqual(1, len(copy_checks), row)
            self.assertTrue(copy_checks[0].get("passed"), copy_checks[0])
            detail = copy_checks[0].get("detail", {})
            self.assertEqual(["no-js"], detail.get("activeApplicableStates"))
            self.assertEqual([], detail.get("textOwnerFailures"))
            self.assertEqual([], detail.get("accessibleOwnerFailures"))
            self.assertEqual([], detail.get("visibleInactiveRefs"))
        axe = doc.get("axeStateCoverage", {})
        self.assertTrue(axe.get("passed"), axe)
        records = axe.get("records", [])
        self.assertGreaterEqual(len(records), 16)
        defaults = [x for x in records if str(x.get("state", "")).startswith("default-")]
        self.assertEqual(16, len(defaults))
        self.assertTrue(all(x.get("passed") is True and
                            x.get("result", {}).get("passed") is True
                            for x in records), records)

    def test_links_and_assessment(self):
        anchors = self.docs["anchors.json"]
        self.assertTrue(anchors.get("passed"), anchors.get("failures"))
        self.assertTrue(anchors.get("records"))
        self.assertTrue(all(x.get("passed") is True for x in anchors["records"]))
        assessment = self.docs["assessment.json"]
        self.assertTrue(assessment.get("passed"), assessment)
        names = {x.get("name") for x in assessment.get("assertions", []) if x.get("passed")}
        self.assertIn("truthful local checking status", names)
        self.assertIn("zero transmitting requests", names)
        self.assertTrue(assessment.get("axeConfirmation", {}).get("passed"),
                        assessment.get("axeConfirmation"))
        applicable = assessment.get("applicableCopy", {})
        self.assertTrue(applicable.get("passed"), applicable)
        self.assertEqual([], applicable.get("visibleInactiveRefs"))
        manifest, _ = fs5.load_copy_manifest(fs5.DEFAULT_COPY_MANIFEST)
        expected_states = sorted(fs5.declared_applicable_states(
            manifest, "assessment", {"local-preview-success"}))
        self.assertEqual(expected_states,
                         applicable.get("activeApplicableStates"))

    def test_performance_evidence(self):
        perf = self.docs["performance.json"]
        self.assertTrue(perf.get("passed"), perf)
        rows = perf.get("rows", [])
        self.assertEqual(16, len(rows))
        expected = {(r[0], w) for r in fs5.ROUTES for w in fs5.PERFORMANCE_WIDTHS}
        self.assertEqual(expected, {(r.get("route"), r.get("viewport", [None])[0]) for r in rows})
        for row in rows:
            self.assertIsInstance(row.get("lcpMs"), (int, float), row)
            self.assertIsInstance(row.get("cls"), (int, float), row)
            self.assertTrue(row.get("heroWithinBudget"), row)
            self.assertTrue(row.get("passed"), row)

    def test_screenshot_manifest_and_hashes(self):
        manifest = self.docs["screenshots-manifest.json"]
        self.assertTrue(manifest.get("passed"), manifest)
        shots = manifest.get("screenshots", [])
        self.assertEqual(manifest.get("count"), len(shots))
        self.assertGreaterEqual(len(shots), 72 * 2)
        visual = manifest.get("visualPairReview", {})
        self.assertTrue(visual.get("complete"), visual)
        self.assertEqual(36, visual.get("canonicalScreenshotCount"))
        self.assertEqual(12, len(visual.get("breakpointContinuity", [])))
        self.assertEqual(18, len(visual.get("routeSilhouette", [])))
        self.assertEqual(18, len(visual.get("whitespaceRhythm", [])))
        for shot in shots:
            path = self.root / shot["path"]
            self.assertTrue(path.is_file(), path)
            self.assertEqual(shot["sha256"], digest(path), path)
            self.assertGreater(shot.get("bytes", 0), 8)
            self.assertGreater(shot.get("pixelDimensions", {}).get("width", 0), 0)

    def test_failure_ledger_is_empty(self):
        failures = self.docs["failures.json"]
        self.assertTrue(failures.get("passed"), failures)
        self.assertEqual([], failures.get("hardFailures"))
        self.assertEqual([], failures.get("matrixFailures"))
        self.assertFalse(any(failures.get("componentFailures", {}).values()))
        self.assertTrue(all(x.get("passed") for x in failures.get("networkRows", [])))
        report = (self.root / "report.md").read_text(encoding="utf-8")
        self.assertIn("**PASS**", report)
        self.assertIn(self.snapshot, report)


if __name__ == "__main__":
    unittest.main()
