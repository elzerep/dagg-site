#!/usr/bin/env python3
"""Capture the FS5 immutable, fail-closed Chrome/CDP evidence package.

This runner intentionally reuses the raw CDP, installed-Chrome and immutable
``serve_preview.py`` plumbing from ``capture_p2_evidence``.  It never assembles
or edits site source.  Every browser lane uses a fresh target, and output is
built in a temporary sibling and promoted only after all gates pass.

The suite is deliberately failure-first.  Missing axe-core, an unusable Home
reference, unsupported touch/CDP commands, a lost network event, or incomplete
route evidence makes the run fail and preserves the partial package under a
``.failed-*`` name.  No synthetic PASS records are emitted.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import hashlib
import html.parser
import json
import os
import re
import shutil
import socket
import struct
import subprocess
import sys
import tempfile
import time
import urllib.parse
import urllib.error
import urllib.request
import unicodedata
import zlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
TOOLS = REPO_ROOT / "tools"
sys.dont_write_bytecode = True
sys.path.insert(0, str(TOOLS))

import capture_p2_evidence as p2  # noqa: E402
import serve_preview  # noqa: E402

SCHEMA_VERSION = 1
DEFAULT_OUTPUT = REPO_ROOT / "evidence" / "FULL-SITE-STAGING" / "FS5"
ROUTES = (
    ("home", "/preview/golden-standard/home/", True),
    ("transformation", "/preview/golden-standard/routes/transformation/", True),
    ("workgraph", "/preview/golden-standard/routes/workgraph/", True),
    ("build", "/preview/golden-standard/routes/build/", True),
    ("impact", "/preview/golden-standard/routes/impact/", False),
    ("trust", "/preview/golden-standard/routes/trust/", True),
    ("company", "/preview/golden-standard/routes/company/", True),
    ("assessment", "/preview/golden-standard/routes/assessment/", True),
)
VIEWPORTS = (
    (320, 720), (360, 800), (390, 844), (768, 1024), (1024, 768),
    (1280, 720), (1366, 768), (1440, 900), (1536, 1024),
)
PERFORMANCE_WIDTHS = (390, 1440)
EXPECTED_MATRIX_ROWS = len(ROUTES) * len(VIEWPORTS)
DEFAULT_COPY_MANIFEST = (REPO_ROOT / "design" / "golden-standard" /
                         "narrative" / "COPY-UNIT-MANIFEST.json")
VISUAL_PROTOCOL = (REPO_ROOT / "design" / "golden-standard" / "authority" /
                   "FS5-VISUAL-PAIR-REVIEW-PROTOCOL.md")
PROTECTED_INVARIANT = (REPO_ROOT / "evidence" / "FULL-SITE-STAGING" /
                       "FS5-PROTECTED-INVARIANT-BASELINE.json")
VISUAL_ROUTES = ("home", "transformation", "workgraph", "build", "trust", "company")
VISUAL_VIEWPORTS = ((1440, 900), (1024, 768), (390, 844))
COPY_ROUTE_ROOTS = {name: "[data-%s]" % name for name, _, _ in ROUTES}
COPY_SECTION_ATTRIBUTES = {
    "shared": "data-copy-section", "home": "data-home-act",
    "transformation": "data-transformation-section",
    "workgraph": "data-workgraph-section", "build": "data-build-beat",
    "impact": "data-impact-section", "trust": "data-trust-section",
    "company": "data-company-section", "assessment": "data-assessment-section",
}
COPY_APPLICABLE_STATES = frozenset((
    "no-js", "local-preview-success", "separate-responsive-menu-layer",
))
# Exact interval contracts.  Each observed transition is checked separately;
# the runner never substitutes a total-duration proxy.
HOME_INTERVALS_MS = (1600, 2200, 2200)
INTERVAL_TOLERANCE_MS = 175
FACTORY_INTERVAL_COUNT = 5
FACTORY_TOTAL_RANGE_MS = (6000, 8000)
FACTORY_HOLD_MIN_DELTA_MS = 50
FLYOUT_OPEN_RANGE_MS = (70, 130)
FLYOUT_CLOSE_RANGE_MS = (170, 290)
REQUIRED_OUTPUTS = (
    "revision.json", "environment.json", "route-matrix.json",
    "interactions.json", "resilience.json", "anchors.json",
    "assessment.json", "performance.json", "failures.json",
    "screenshots-manifest.json", "tests-output.txt", "report.md",
)
SNAPSHOT_HEADER = "x-dagg-snapshot"
ASSESSMENT_PATH = "/preview/golden-standard/routes/assessment/"
COMPONENT_SCRIPT = "/preview/golden-standard/component-library/script.js"
ROUTE_SCRIPT = {
    name: ("/preview/golden-standard/home/src/direction.js" if name == "home"
           else "/preview/golden-standard/routes/%s/src/direction.js" % name)
    for name, _, _ in ROUTES
}

FIRST_VIEWPORTS = ((1440, 900), (1024, 768), (390, 844))


def first_view_item(item_id: str, selector: str | tuple[str, ...],
                    mode: str = "full", count: int | None = None):
    item = {"id": item_id, "mode": mode}
    if isinstance(selector, tuple):
        item["selectors"] = list(selector)
    else:
        item["selector"] = selector
    if count is not None:
        item["count"] = count
    return item


def first_view_contracts():
    contracts = {}
    for viewport in FIRST_VIEWPORTS:
        mobile = viewport == (390, 844)
        contracts[("home", viewport)] = (
            first_view_item("home-eyebrow", ".home-hero .home-eyebrow"),
            first_view_item("home-h1", ".home-h1"),
            first_view_item("home-lead", ".home-lead"),
            first_view_item("home-primary-action", ".home-hero [data-home-primary-action]"),
            first_view_item("home-secondary-action", ".home-hero .cl-button--secondary"),
            first_view_item("home-hero-image", "[data-home-hero-image]",
                            "start44" if mobile else "full"),
        )
        contracts[("transformation", viewport)] = (
            first_view_item("transformation-eyebrow", ".transformation-hero .transformation-eyebrow"),
            first_view_item("transformation-h1", ".transformation-h1"),
            first_view_item("transformation-lead", ".transformation-lead"),
            first_view_item("transformation-primary-action", ".transformation-hero [data-transformation-primary-action]"),
            first_view_item("transformation-secondary-action", ".transformation-hero .cl-button--secondary"),
            first_view_item("transformation-outcome-labels",
                            "[data-transformation-index-label]", "all-full", 5),
            first_view_item("transformation-hero-image",
                            "[data-transformation-hero-image]",
                            "start44" if mobile else "full"),
        )
        workgraph = [
            first_view_item("workgraph-eyebrow", ".workgraph-hero .workgraph-eyebrow"),
            first_view_item("workgraph-h1", ".workgraph-h1"),
            first_view_item("workgraph-lead", ".workgraph-lead"),
            first_view_item("workgraph-disclosure",
                            '[data-copy-ref="workgraph.position.disclosure"]'),
            first_view_item("workgraph-record", "[data-workgraph-record]",
                            "start44"),
            first_view_item("workgraph-record-identity",
                            '[data-copy-ref="workgraph.position.identity"]'),
            first_view_item("workgraph-record-owner",
                            '[data-workgraph-record-field="owner"]' if not mobile else
                            ('[data-workgraph-record-field="owner"]',
                             '[data-workgraph-record-field="permission"]'),
                            "full" if not mobile else "any-full"),
        ]
        if not mobile:
            workgraph.insert(4, first_view_item(
                "workgraph-actions", ".workgraph-hero__actions .cl-button",
                "all-full", 2))
        contracts[("workgraph", viewport)] = tuple(workgraph)
        build = [
            first_view_item("build-eyebrow", ".build-hero .build-eyebrow"),
            first_view_item("build-h1", ".build-h1"),
            first_view_item("build-lead", ".build-lead"),
            first_view_item("build-action", "[data-build-mode-action]"),
            first_view_item("build-disclosure",
                            '[data-copy-ref="build.position.disclosure"]'),
            first_view_item("build-opening-stage", "[data-build-opening-stage]",
                            "start44"),
            first_view_item("build-opening-approved",
                            '[data-build-opening-stage-row="approved-intervention"]'),
        ]
        if mobile:
            build.append(first_view_item(
                "build-opening-evaluation-or-review",
                ('[data-build-opening-stage-row="evaluation"]',
                 '[data-build-opening-stage-row="review-state"]'),
                "any-full"))
        else:
            build.append(first_view_item(
                "build-opening-permission",
                '[data-build-opening-stage-row="specification-permission"]'))
            build.append(first_view_item(
                "build-opening-review",
                '[data-build-opening-stage-row="review-state"]'))
        contracts[("build", viewport)] = tuple(build)
        contracts[("impact", viewport)] = (
            first_view_item("impact-eyebrow", ".impact-hero .impact-eyebrow"),
            first_view_item("impact-h1", ".impact-h1"),
            first_view_item("impact-lead", ".impact-lead"),
            first_view_item("impact-primary-action",
                            ".impact-hero .cl-button--primary"),
        )
        contracts[("trust", viewport)] = (
            first_view_item("trust-h1", ".trust-h1"),
            first_view_item("trust-lead", ".trust-lead"),
            first_view_item("trust-primary-action",
                            ".trust-actions .cl-button--primary"),
            first_view_item("trust-secondary-action",
                            ".trust-actions .cl-button--secondary"),
            first_view_item("trust-control", "[data-trust-control]",
                            "start44"),
        )
        company = [
            first_view_item("company-h1", ".company-h1"),
            first_view_item("company-lead", ".company-lead"),
            first_view_item("company-seam", "[data-company-seam]"),
            first_view_item("company-accountability",
                            "[data-company-accountability]",
                            "start44"),
        ]
        if mobile:
            company.append(first_view_item(
                "company-accountability-decision",
                '[data-company-accountability-row="decision"]',
                "start44"))
        else:
            company.append(first_view_item(
                "company-accountability-decision",
                '[data-company-accountability-row="decision"]'))
            company.append(first_view_item(
                "company-accountability-build",
                '[data-company-accountability-row="build"]'))
        contracts[("company", viewport)] = tuple(company)
        contracts[("assessment", viewport)] = (
            first_view_item("assessment-eyebrow", ".assessment-hero .assessment-eyebrow"),
            first_view_item("assessment-h1", ".assessment-h1"),
            first_view_item("assessment-lead", ".assessment-lead"),
            first_view_item("assessment-primary-action",
                            "[data-assessment-primary-action]"),
            first_view_item("assessment-scope", ".assessment-hero__scope"),
        )
    return contracts


FIRST_VIEW_CONTRACTS = first_view_contracts()

COPY_BANDS = {
    "home": (0, 520), "transformation": (450, 600), "workgraph": (320, 430),
    "build": (360, 535), "trust": (300, 420), "company": (260, 360),
    "assessment": (300, 390), "impact": (0, 10000),
}
PROGRESSIVE_MAX = {
    "home": 100, "transformation": 220, "workgraph": 320,
    "build": 360, "trust": 320, "company": 160,
    "assessment": 180, "impact": 240,
}

PERF_BOOTSTRAP = r"""
(() => {
  window.__fs5Perf = {lcp: null, cls: 0, events: [], touches: []};
  try { new PerformanceObserver(list => { for (const e of list.getEntries()) {
    window.__fs5Perf.lcp = e.startTime;
  }}).observe({type:'largest-contentful-paint', buffered:true}); } catch (e) {}
  try { new PerformanceObserver(list => { for (const e of list.getEntries()) {
    if (!e.hadRecentInput) window.__fs5Perf.cls += e.value;
  }}).observe({type:'layout-shift', buffered:true}); } catch (e) {}
  addEventListener('pointerdown', e => window.__fs5Perf.events.push({type:'pointerdown', at:performance.now()}), true);
  addEventListener('keydown', e => window.__fs5Perf.events.push({type:'keydown', key:e.key, at:performance.now()}), true);
  for (const type of ['touchstart','touchend','touchcancel']) {
    addEventListener(type, e => {
      const target=e.target && e.target.closest && e.target.closest('[data-fs5-touch-index]');
      window.__fs5Perf.touches.push({type, at:performance.now(), trusted:e.isTrusted,
        index:target && target.getAttribute('data-fs5-touch-index')});
    }, true);
  }
})();
"""

BASE_MEASURE = r"""
(async () => {
  const rendered = el => { if (!el || !el.getClientRects().length) return false;
    const c=getComputedStyle(el); return c.display!=='none' && c.visibility!=='hidden' && +c.opacity!==0; };
  const rect = el => { const r=el.getBoundingClientRect(); return {x:r.x,y:r.y,width:r.width,height:r.height,bottom:r.bottom,right:r.right}; };
  const inViewport = el => { const r=el.getBoundingClientRect(); return rendered(el) && r.top>=-0.5 && r.left>=-0.5 && r.right<=innerWidth+0.5 && r.bottom<=innerHeight+0.5; };
  const start44 = el => { if(!rendered(el)) return false; const r=el.getBoundingClientRect();
    const visibleHeight=Math.min(r.bottom,innerHeight)-Math.max(r.top,0);
    return r.top>=-0.5 && r.top<=innerHeight+0.5 && r.left>=-0.5 && r.right<=innerWidth+0.5 && visibleHeight>=43.5; };
  const textLineCount = el => { if(!el)return null;const range=document.createRange();range.selectNodeContents(el);
    const tops=[...range.getClientRects()].filter(r=>r.width>0&&r.height>0).map(r=>r.top).sort((a,b)=>a-b);
    const rows=[];for(const top of tops){if(!rows.length||Math.abs(top-rows[rows.length-1])>1)rows.push(top);}return rows.length;};
  const text = el => el ? el.textContent.replace(/\s+/g,' ').trim() : null;
  const wordCount = value => (value.match(/[\p{L}\p{N}]+(?:[-'][\p{L}\p{N}]+)*/gu)||[]).length;
  const inClosedDetails = el => { const d=el&&el.closest('details:not([open])');
    if (!d || el.closest('summary')) return false; const summary=d.querySelector(':scope > summary');
    return !(summary && getComputedStyle(summary).display==='none'); };
  const excluded = el => !el || !rendered(el) || inClosedDetails(el) ||
    el.closest('header,footer,[hidden],[aria-hidden="true"],script,style,.visually-hidden,.cl-visually-hidden,.workgraph-visually-hidden');
  const main=document.querySelector('main')||document.body;
  const copy = {default:0, progressive:0, firstSection:0, unscoped:[],
    units:[], nestedRefs:[], uncoveredAccessible:[], uncoveredShell:[],
    textOwners:[], accessibleOwners:[]};
  const rootSelectors={home:'[data-home]',transformation:'[data-transformation]',
    workgraph:'[data-workgraph]',build:'[data-build]',impact:'[data-impact]',
    trust:'[data-trust]',company:'[data-company]',assessment:'[data-assessment]'};
  const sectionAttributes={shared:'data-copy-section',home:'data-home-act',
    transformation:'data-transformation-section',workgraph:'data-workgraph-section',
    build:'data-build-beat',impact:'data-impact-section',trust:'data-trust-section',
    company:'data-company-section',assessment:'data-assessment-section'};
  const exactText=el=>{const values=[];const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);
    let n;while((n=w.nextNode())){const v=n.nodeValue.replace(/\u00a0/g,' ').replace(/\s+/g,' ').trim();if(v)values.push(v);}return values.join('\n')};
  const shellSelector='header,footer,[data-chrome-header],.chrome-footer,.skip-link,[data-copy-section]';
  const routeOf=el=>{if(el.closest(shellSelector))return 'shared';
    for(const [route,selector] of Object.entries(rootSelectors)){if(el.closest(selector))return route;}return null};
  const computedAccessibleName=el=>{const labelled=el.getAttribute('aria-labelledby');
    if(labelled){return labelled.split(/\s+/).map(id=>document.getElementById(id)).filter(Boolean).map(exactText).join(' ')}
    const label=el.getAttribute('aria-label');if(label)return label;
    if(el.tagName==='IMG'&&el.hasAttribute('alt'))return el.getAttribute('alt');
    if(el.id){const explicit=document.querySelector('label[for="'+CSS.escape(el.id)+'"]');if(explicit)return exactText(explicit)}
    const wrapping=el.closest('label');if(wrapping)return exactText(wrapping);
    return exactText(el)};
  const attrsOf=el=>{const values={};for(const attr of el.attributes){
    if(attr.value.trim())values[attr.name]=[attr.value.replace(/\u00a0/g,' ').replace(/[\t\r\f ]+/g,' ').trim()];}return values};
  const copyNodes=[...document.querySelectorAll('[data-copy-ref]')];
  copy.units=copyNodes.map(el=>{const attributes=attrsOf(el);const accessibleName=computedAccessibleName(el);
    if(accessibleName)attributes['computed-accessible-name']=[accessibleName];return ({
    ref:el.getAttribute('data-copy-ref'), kind:el.getAttribute('data-copy-kind'),
    scope:el.getAttribute('data-copy-scope'), state:el.getAttribute('data-copy-state'),
    route:routeOf(el),
    section:(()=>{const route=routeOf(el),attr=sectionAttributes[route];const owner=attr&&el.closest('['+attr+']');return owner&&owner.getAttribute(attr)})(),
    text:exactText(el), attributes, rendered:rendered(el)
  })});
  copy.nestedRefs=copyNodes.flatMap(el=>{const pairs=[];let parent=el.parentElement&&el.parentElement.closest('[data-copy-ref]');
    while(parent){pairs.push({childRef:el.getAttribute('data-copy-ref'),ancestorRef:parent.getAttribute('data-copy-ref')});
      parent=parent.parentElement&&parent.parentElement.closest('[data-copy-ref]');}return pairs;});
  const accessibleAttributes=['aria-label','title','alt','placeholder','aria-description','aria-valuetext','aria-roledescription'];
  const publicElements=[...document.querySelectorAll('main,main *,header,header *,footer,footer *,[data-chrome-header],[data-chrome-header] *,.chrome-footer,.chrome-footer *,.skip-link,[data-copy-section],[data-copy-section] *')];
  for(const el of publicElements){for(const attr of accessibleAttributes){const value=el.getAttribute(attr);
    if(value&&value.trim())copy.accessibleOwners.push({tag:el.tagName,attribute:attr,value,ownerRef:el.getAttribute('data-copy-ref')});}}
  copy.uncoveredAccessible=copy.accessibleOwners.filter(x=>!x.ownerRef);
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;
  while((node=walker.nextNode())){const value=node.nodeValue.replace(/\s+/g,' ').trim();if(!value)continue;
    const parent=node.parentElement;if(parent.closest('script,style,template'))continue;
    const inMain=!!parent.closest('main'),inShell=!!parent.closest(shellSelector);if(!inMain&&!inShell)continue;
    const owner=parent.closest('[data-copy-ref]');const row={text:value,ownerRef:owner&&owner.getAttribute('data-copy-ref'),region:inMain?'main':'shell'};
    copy.textOwners.push(row);if(!row.ownerRef)(inMain?copy.unscoped:copy.uncoveredShell).push(value);
    if(!inMain||excluded(parent))continue;const scope=parent.closest('[data-copy-scope]');
    if(!scope)continue;const kind=scope.getAttribute('data-copy-scope');
    if(kind==='default'||kind==='progressive')copy[kind]+=wordCount(value);
    if(kind==='default'&&parent.closest('main section')===(document.querySelector('main section')))copy.firstSection+=wordCount(value);
  }
  const headings=[...document.querySelectorAll('h1,h2,h3,h4,h5,h6')].filter(rendered).map(el=>({level:+el.tagName[1],text:text(el)}));
  const skips=[]; for(let i=1;i<headings.length;i++) if(headings[i].level>headings[i-1].level+1) skips.push([headings[i-1],headings[i]]);
  const ids=[...document.querySelectorAll('[id]')].map(el=>el.id); const dup=ids.filter((id,i)=>ids.indexOf(id)!==i);
  const links=[...document.querySelectorAll('a[href]')].filter(rendered).map(a=>({text:text(a),href:a.getAttribute('href'),absolute:a.href,rect:rect(a)}));
  const images=[...document.images].map(img=>({src:img.getAttribute('src'),currentSrc:img.currentSrc,complete:img.complete,naturalWidth:img.naturalWidth,naturalHeight:img.naturalHeight,rendered:rect(img)}));
  const firstSelectors=%s; const firstView=firstSelectors.map(spec=>{const selectors=spec.selectors||[spec.selector];
    const elements=selectors.flatMap(selector=>[...document.querySelectorAll(selector)]).filter((el,index,all)=>all.indexOf(el)===index);
    const rows=elements.map(el=>({rendered:rendered(el),full:inViewport(el),start44:start44(el),rect:rect(el)}));
    let passed=false;if(spec.mode==='full')passed=elements.length===1&&rows[0].full;
    else if(spec.mode==='start44')passed=elements.length===1&&rows[0].start44;
    else if(spec.mode==='all-full')passed=elements.length===spec.count&&rows.every(row=>row.full);
    else if(spec.mode==='any-full')passed=elements.length>0&&rows.some(row=>row.full);
    return {id:spec.id,selector:spec.selector||null,selectors,mode:spec.mode,expectedCount:spec.count||null,
      matchCount:elements.length,present:elements.length>0,rendered:rows.length>0&&rows.every(row=>row.rendered),inside:passed,passed,measurements:rows};});
  const h1=document.querySelector('main h1'); const hero=document.querySelector('main section:first-of-type');
  const build=document.querySelector('[data-flyout]'); const buildSummary=build&&build.querySelector(':scope > summary');
  const buildFirst=build&&build.querySelector('a[href]');
  const timerStart=performance.now(); await new Promise(r=>setTimeout(r,200)); const timerElapsed=performance.now()-timerStart;
  const focusables=[...document.querySelectorAll('a[href],button,input,textarea,select,summary,[tabindex]')].filter(rendered).map(el=>({tag:el.tagName,text:text(el),tabindex:el.getAttribute('tabindex'),inNav:!!el.closest('header,nav'),inAssessment:!!el.closest('[data-assessment]'),rect:rect(el)}));
  const styles=[...document.querySelectorAll('main section')].map(el=>({height:rect(el).height,background:getComputedStyle(el).backgroundColor}));
  return {
    url:location.href, snapshot:(document.querySelector('meta[name="dagg-snapshot"]')||{}).content||null,
    visibility:document.visibilityState, viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio,visualWidth:visualViewport&&visualViewport.width,visualHeight:visualViewport&&visualViewport.height},
    timerElapsed, scroll:{clientWidth:document.documentElement.clientWidth,scrollWidth:document.documentElement.scrollWidth,clientHeight:document.documentElement.clientHeight,scrollHeight:document.documentElement.scrollHeight},
    structure:{header:document.querySelectorAll('body > header,[data-chrome-header]').length,main:document.querySelectorAll('main').length,footer:document.querySelectorAll('body > footer,.chrome-footer').length,h1:document.querySelectorAll('main h1').length,headings,skips,duplicateIds:[...new Set(dup)]},
    h1:{text:text(h1),rect:h1?rect(h1):null,fontSize:h1?parseFloat(getComputedStyle(h1).fontSize):null,lineHeight:h1?parseFloat(getComputedStyle(h1).lineHeight):null,lineCount:textLineCount(h1)},
    hero:hero?rect(hero):null, firstView, links, images, copy, focusables, sections:styles,
    protectedHome:{eyebrow:text(document.querySelector('.home-eyebrow')),
      h1:text(document.querySelector('.home-h1')),lead:text(document.querySelector('.home-lead')),
      primaryAction:text(document.querySelector('[data-home-primary-action]')),
      secondaryAction:text(document.querySelector('.home-actions .cl-button--secondary')),
      image:(()=>{const i=document.querySelector('[data-home-hero-image]');return i?{alt:i.alt,currentSrc:i.currentSrc,naturalWidth:i.naturalWidth,naturalHeight:i.naturalHeight}:null})()},
    buildContract:{summaryTag:buildSummary&&buildSummary.tagName,summaryText:text(buildSummary),firstText:text(buildFirst),firstHref:buildFirst&&buildFirst.getAttribute('href'),nestedLink:!!(buildSummary&&buildSummary.querySelector('a'))},
    routeFacts:{
      home:{sequence:(document.querySelector('[data-home-execution]')||{}).dataset?.homeSequence||null,index:(document.querySelector('[data-home-execution]')||{}).dataset?.homeStateIndex||null,status:text(document.querySelector('[data-home-execution-status]')),states:[...document.querySelectorAll('[data-home-execution-state]')].map(el=>text(el)),stateTabStops:document.querySelectorAll('[data-home-execution-states] a,[data-home-execution-states] button,[data-home-execution-states] [tabindex]').length,bodyText:text(document.querySelector('[data-home-execution]')),rootText:text(document.querySelector('[data-home]')),disclosure:(()=>{const root=document.querySelector('[data-home]');const nodes=root?[...root.querySelectorAll('[data-copy-ref="home.record.disclosure"]')]:[];const disclosure=nodes[0]||null;const synthetic=root?[...root.querySelectorAll('[data-copy-ref]')].find(el=>/WG-[0-9]{3}/.test(text(el)||'')):null;return {count:nodes.length,rendered:rendered(disclosure),firstSyntheticRef:synthetic&&synthetic.getAttribute('data-copy-ref'),precedes:!!(disclosure&&synthetic&&(disclosure.compareDocumentPosition(synthetic)&Node.DOCUMENT_POSITION_FOLLOWING))};})()},
      transformation:{provenance:text(document.querySelector('[data-transformation-provenance]')),provenanceVisible:rendered(document.querySelector('[data-transformation-provenance]')),provenanceInsideDetails:!!document.querySelector('[data-transformation-map] [data-transformation-provenance]'),outcomes:[...document.querySelectorAll('[data-transformation-outcome]')].map(el=>({text:text(el),visible:rendered(el)})),selected:(document.querySelector('input[name="outcome"]:checked')||{}).value||null,resolved:document.querySelector('[data-transformation]')?.hasAttribute('data-transformation-resolved')||false},
      workgraph:{mode:document.querySelector('[data-workgraph-record-state]')?.getAttribute('data-workgraph-carrier-mode')||null,active:document.querySelector('[data-workgraph-record-state]')?.getAttribute('data-workgraph-active-state')||null,steps:[...document.querySelectorAll('[data-workgraph-step]')].map(el=>text(el))},
      build:{pass:document.querySelector('[data-build-factory-progress]')?.getAttribute('data-build-pass')||null,active:document.querySelector('[data-build-stage].build-stage--active')?.getAttribute('data-build-stage')||null,status:text(document.querySelector('[data-build-status]')),stages:[...document.querySelectorAll('[data-build-stage]')].map(el=>el.getAttribute('data-build-stage')),pauseVisible:rendered(document.querySelector('[data-build-pause]')),replayVisible:rendered(document.querySelector('[data-build-replay]')),inspectVisible:rendered(document.querySelector('[data-build-inspect]'))},
      assessment:{submit:text(document.querySelector('[data-assessment-submit]')),status:text(document.querySelector('[data-assessment-status]')),formVisible:rendered(document.querySelector('[data-assessment-form]')),successVisible:rendered(document.querySelector('[data-assessment-success]'))}
    },
    performance:Object.assign({},window.__fs5Perf||{}, {navigation:performance.getEntriesByType('navigation').map(e=>({domContentLoaded:e.domContentLoadedEventEnd,load:e.loadEventEnd,duration:e.duration}))})
  };
})()
"""


class FS5Failure(RuntimeError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def utc_stamp() -> str:
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def json_write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def assertion(bucket: list, name: str, passed: bool, detail=None) -> bool:
    bucket.append({"name": name, "passed": bool(passed), "detail": detail})
    return bool(passed)


def all_passed(assertions: list) -> bool:
    return bool(assertions) and all(item.get("passed") is True for item in assertions)


def start_fs5_chrome(profile_dir: Path, failure_output: Path | None = None):
    """Start installed Chrome with an explicit debug port and diagnostics.

    P2's original launcher relies solely on ``DevToolsActivePort`` and drops
    stderr.  That makes a locked-Mac/keychain failure indistinguishable from a
    missing port file.  FS5 uses a reserved loopback port, polls the documented
    ``/json/version`` endpoint, avoids macOS keychain UI with a disposable mock
    keychain, and persists actionable diagnostics on failure.  It never falls
    back to another browser or to simulated evidence.
    """
    chrome_path = p2.find_chrome()
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        debug_port = probe.getsockname()[1]
    stderr_path = profile_dir / "chrome-stderr.log"
    args = [
        chrome_path, "--headless=new",
        "--remote-debugging-address=127.0.0.1",
        "--remote-debugging-port=%d" % debug_port,
        "--user-data-dir=%s" % profile_dir,
        "--no-first-run", "--no-default-browser-check",
        "--password-store=basic", "--use-mock-keychain",
        "--disable-extensions", "--disable-gpu",
        "--disable-background-timer-throttling",
        "--disable-backgrounding-occluded-windows",
        "--disable-renderer-backgrounding", "--hide-scrollbars",
        "--force-device-scale-factor=1", "--remote-allow-origins=*",
        "about:blank",
    ]
    started = time.monotonic()
    with stderr_path.open("wb") as stderr_file:
        process = subprocess.Popen(args, stdout=subprocess.DEVNULL,
                                   stderr=stderr_file)
    version_url = "http://127.0.0.1:%d/json/version" % debug_port
    last_error = None
    deadline = time.monotonic() + 45
    while time.monotonic() < deadline:
        exit_code = process.poll()
        if exit_code is not None:
            last_error = "Chrome exited with code %s" % exit_code
            break
        try:
            with urllib.request.urlopen(version_url, timeout=.5) as response:
                version = json.loads(response.read())
            websocket = version.get("webSocketDebuggerUrl")
            if websocket:
                diagnostic = {
                    "chromePath": chrome_path, "debugPort": debug_port,
                    "startupSeconds": round(time.monotonic() - started, 3),
                    "processExitCode": None,
                    "devToolsActivePortExists":
                        (profile_dir / "DevToolsActivePort").exists(),
                    "versionEndpoint": version,
                    "stderrTail": stderr_path.read_text(
                        encoding="utf-8", errors="replace")[-4000:],
                }
                return process, websocket, chrome_path, diagnostic
        except (OSError, ValueError, urllib.error.URLError) as err:
            last_error = "%s: %s" % (type(err).__name__, err)
        time.sleep(.05)
    if process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    diagnostic = {
        "chromePath": chrome_path, "debugPort": debug_port,
        "startupSeconds": round(time.monotonic() - started, 3),
        "processExitCode": process.returncode,
        "devToolsActivePortExists": (profile_dir / "DevToolsActivePort").exists(),
        "profileEntries": sorted(p.name for p in profile_dir.iterdir())[:100],
        "lastEndpointError": last_error,
        "stderrTail": stderr_path.read_text(
            encoding="utf-8", errors="replace")[-12000:],
        "arguments": args[1:],
    }
    if failure_output:
        json_write(failure_output, diagnostic)
    raise FS5Failure("Chrome CDP startup failed; diagnostics: %s"
                     % (failure_output or json.dumps(diagnostic)[:2000]))


class FS5Page(p2.Page):
    """A disposable target with stricter event accounting than the P2 page."""

    def __init__(self, cdp: p2.CDP, base_url: str, snapshot_id: str):
        self.cdp = cdp
        self.base_url = base_url
        self.expected_snapshot = snapshot_id
        self.origin = urllib.parse.urlsplit(base_url)
        self.touch_serial = 0
        target = cdp.call("Target.createTarget", {"url": "about:blank"})
        self.target_id = target["targetId"]
        self.session = cdp.call("Target.attachToTarget", {
            "targetId": self.target_id, "flatten": True})["sessionId"]
        for domain in ("Page", "Runtime", "Log", "Network", "DOM", "Accessibility", "Performance"):
            cdp.call("%s.enable" % domain, session_id=self.session)
        cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": PERF_BOOTSTRAP}, session_id=self.session)
        self.last_events = []

    def close(self):
        try:
            self.cdp.call("Target.closeTarget", {"targetId": self.target_id})
        except Exception:
            pass

    def configure(self, width: int, height: int, *, reduced=False, touch=False,
                  script_disabled=False, preload=None, block=None, scale=1.0):
        mobile = bool(touch or width < 600)
        self.cdp.call("Emulation.setDeviceMetricsOverride", {
            "width": width, "height": height, "deviceScaleFactor": scale,
            "mobile": mobile, "screenWidth": width, "screenHeight": height,
        }, session_id=self.session)
        self.cdp.call("Emulation.setTouchEmulationEnabled", {
            "enabled": bool(touch), "maxTouchPoints": 5 if touch else 1,
        }, session_id=self.session)
        self.cdp.call("Emulation.setEmulatedMedia", {"features": [{
            "name": "prefers-reduced-motion", "value": "reduce" if reduced else "no-preference"}]}, session_id=self.session)
        if preload:
            self.cdp.call("Page.addScriptToEvaluateOnNewDocument", {"source": preload}, session_id=self.session)
        self.cdp.call("Network.setBlockedURLs", {"urls": list(block or [])}, session_id=self.session)
        self.cdp.call("Emulation.setScriptExecutionDisabled", {"value": bool(script_disabled)}, session_id=self.session)

    def navigate(self, url: str, width: int, height: int, **mode):
        self.cdp.events.clear()
        self.configure(width, height, **mode)
        self.cdp.call("Page.bringToFront", session_id=self.session)
        self.cdp.call("Page.navigate", {"url": url}, session_id=self.session)
        event = self.cdp.wait_for_event("Page.loadEventFired")
        if event.get("sessionId") not in (None, self.session):
            raise FS5Failure("load event belonged to another target")
        if mode.get("script_disabled"):
            return self.nojs_measure()
        readiness = self.evaluate(p2.WAIT_FOR_PAINT, await_promise=True)
        route = url_to_route(url)
        selectors = FIRST_VIEW_CONTRACTS.get((route, (width, height)), ())
        measured = self.evaluate(BASE_MEASURE % json.dumps(list(selectors)), await_promise=True)
        measured["readiness"] = readiness
        measured["inputCapabilities"] = self.evaluate("({touch:navigator.maxTouchPoints,coarse:matchMedia('(pointer: coarse)').matches,hover:matchMedia('(hover: hover)').matches})")
        return measured

    def nojs_measure(self):
        snap = self.cdp.call("DOMSnapshot.captureSnapshot", {
            "computedStyles": ["display", "visibility"], "includeDOMRects": True,
            "includePaintOrder": True}, session_id=self.session)
        ax = self.cdp.call("Accessibility.getFullAXTree", session_id=self.session)
        strings = snap.get("strings", [])
        nodes = (snap.get("documents") or [{}])[0].get("nodes", {})
        names = [strings[i] for i in nodes.get("nodeName", [])]
        values = [strings[i] for i in nodes.get("nodeValue", []) if isinstance(i, int) and i >= 0]
        ax_nodes = []
        for node in ax.get("nodes", []):
            role = (node.get("role") or {}).get("value")
            name = (node.get("name") or {}).get("value")
            if not node.get("ignored"):
                ax_nodes.append({"role": role, "name": name})
        return {
            "dom": {"nodeCount": len(names), "noscriptCount": sum(n.upper() == "NOSCRIPT" for n in names), "text": " ".join(values)},
            "accessibility": {"nodeCount": len(ax_nodes), "nodes": ax_nodes},
            "copy": copy_from_dom_snapshot(snap),
            "viewport": self.cdp.call("Page.getLayoutMetrics", session_id=self.session),
        }

    def events(self, intentional_blocks=()):
        self.cdp.drain(0.7)
        events = [e for e in self.cdp.events if e.get("sessionId") in (None, self.session)]
        self.cdp.events.clear()
        ledger = {}
        console = []
        for event in events:
            method, params = event.get("method"), event.get("params", {})
            rid = params.get("requestId")
            if method == "Network.requestWillBeSent":
                req = params.get("request", {})
                ledger.setdefault(rid, {}).update({"requestId": rid, "url": req.get("url"), "method": req.get("method"), "type": params.get("type"), "sent": True})
            elif method == "Network.responseReceived":
                response = params.get("response", {})
                ledger.setdefault(rid, {}).update({"response": True, "status": response.get("status"), "responseUrl": response.get("url"), "headers": response.get("headers", {})})
            elif method == "Network.loadingFinished":
                ledger.setdefault(rid, {}).update({"finished": True, "encodedDataLength": params.get("encodedDataLength", 0)})
            elif method == "Network.loadingFailed":
                ledger.setdefault(rid, {}).update({"failed": True, "finished": True, "errorText": params.get("errorText"), "blockedReason": params.get("blockedReason"), "canceled": params.get("canceled", False)})
            elif method == "Runtime.exceptionThrown":
                console.append({"kind": method, "detail": params.get("exceptionDetails", {})})
            elif method == "Runtime.consoleAPICalled" and params.get("type") == "error":
                console.append({"kind": method, "detail": params})
            elif method == "Log.entryAdded" and (params.get("entry") or {}).get("level") == "error":
                console.append({"kind": method, "detail": params.get("entry")})
        rows = list(ledger.values())
        blocks = tuple(intentional_blocks)
        for row in rows:
            row["intentionalBlock"] = bool(row.get("failed") and any(token in (row.get("url") or "") for token in blocks))
        unresolved = [r for r in rows if r.get("sent") and not r.get("finished")]
        orphans = [r for r in rows if not r.get("sent")]
        failed = [r for r in rows if r.get("failed") and not r.get("intentionalBlock") and not r.get("canceled")]
        http_errors = [r for r in rows if (r.get("status") or 0) >= 400]
        remote = []
        header_errors = []
        for row in rows:
            url = row.get("responseUrl") or row.get("url") or ""
            parsed = urllib.parse.urlsplit(url)
            same = parsed.scheme in ("http", "https") and parsed.netloc == self.origin.netloc
            if parsed.scheme in ("http", "https") and not same:
                remote.append(row)
            if same and row.get("response") and (row.get("status") or 0) < 400:
                headers = {str(k).lower(): str(v) for k, v in (row.get("headers") or {}).items()}
                if headers.get(SNAPSHOT_HEADER) != self.expected_snapshot:
                    header_errors.append({"url": url,
                                          "actual": headers.get(SNAPSHOT_HEADER),
                                          "expected": self.expected_snapshot})
        return {"requests": rows, "unresolved": unresolved, "orphanEvents": orphans,
                "failed": failed, "httpErrors": http_errors, "remote": remote,
                "console": console, "missingSnapshotHeaders": header_errors}

    def screenshot(self, beyond_viewport=False):
        result = self.cdp.call("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": bool(beyond_viewport), "fromSurface": True}, session_id=self.session)
        return base64.b64decode(result["data"])

    def point(self, selector):
        value = self.evaluate("(() => {const e=document.querySelector(%s);if(!e)return null;const r=e.getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()" % json.dumps(selector))
        if not value:
            raise FS5Failure("missing interaction selector %s" % selector)
        return value

    def mouse(self, selector, click=False):
        p = self.point(selector)
        self.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": p["x"], "y": p["y"]}, session_id=self.session)
        if click:
            for kind in ("mousePressed", "mouseReleased"):
                self.cdp.call("Input.dispatchMouseEvent", {"type": kind, "x": p["x"], "y": p["y"], "button": "left", "clickCount": 1}, session_id=self.session)

    def touch(self, selector, *, cancel=False):
        self.evaluate("document.querySelector(%s).scrollIntoView({block:'center',inline:'center'})" % json.dumps(selector))
        self.wait(20)
        p = self.point(selector)
        point = {"x": p["x"], "y": p["y"], "radiusX": 1, "radiusY": 1, "force": 1, "id": 1}
        self.touch_serial += 1
        token = self.evaluate("""(()=>{const e=document.querySelector(%s);
          if(!e)return null;if(!e.hasAttribute('data-fs5-touch-index'))
            e.setAttribute('data-fs5-touch-index',%s);
          return e.getAttribute('data-fs5-touch-index')})()""" %
                              (json.dumps(selector),
                               json.dumps("direct-%d" % self.touch_serial)))
        if token is None:
            raise FS5Failure("missing touch target %s" % selector)
        before = self.evaluate("(window.__fs5Perf&&window.__fs5Perf.touches||[]).length")
        self.cdp.call("Input.dispatchTouchEvent", {"type": "touchStart", "touchPoints": [point]}, session_id=self.session)
        self.cdp.call("Input.dispatchTouchEvent", {"type": "touchCancel" if cancel else "touchEnd", "touchPoints": []}, session_id=self.session)
        self.wait(20)
        events = self.evaluate("(window.__fs5Perf&&window.__fs5Perf.touches||[]).slice(%d)" % before)
        relevant = [event for event in events if event.get("index") == token]
        return {"selector": selector, "index": token, "cancelled": bool(cancel),
                "point": p, "events": events,
                "passed": bool(relevant) and all(e.get("trusted") is True for e in relevant)
                and any(e.get("type") == "touchstart" for e in relevant)
                and any(e.get("type") == ("touchcancel" if cancel else "touchend") for e in relevant)}

    def key(self, key, code=None, vk=0, text=None):
        for kind in (["rawKeyDown", "char", "keyUp"] if text is not None else ["rawKeyDown", "keyUp"]):
            params = {"type": kind, "key": key, "code": code or key, "windowsVirtualKeyCode": vk, "nativeVirtualKeyCode": vk}
            if kind == "char":
                params.update(text=text, unmodifiedText=text)
            self.cdp.call("Input.dispatchKeyEvent", params, session_id=self.session)

    def wait(self, ms):
        return self.evaluate("new Promise(r=>setTimeout(r,%d))" % ms, await_promise=True)


def url_to_route(url: str) -> str:
    path = urllib.parse.urlsplit(url).path
    for name, route_path, _ in ROUTES:
        if path == route_path or path.rstrip("/") == route_path.rstrip("/"):
            return name
    raise FS5Failure("URL is outside the FS5 route table: %s" % url)


def normalize_copy(value: str) -> str:
    """NFC, NBSP conversion and horizontal folding, preserving unit lines."""
    normalized = unicodedata.normalize("NFC", value or "").replace("\u00a0", " ")
    lines = [re.sub(r"[\t\r\f ]+", " ", line).strip()
             for line in normalized.split("\n")]
    return "\n".join(line for line in lines if line)


def copy_from_dom_snapshot(snapshot: dict) -> dict:
    """Reconstruct keyed copy from a script-disabled CDP DOMSnapshot."""
    strings = snapshot.get("strings") or []
    documents = snapshot.get("documents") or []
    if not documents:
        return {"units": [], "nestedRefs": [], "unscoped": [],
                "uncoveredShell": [], "uncoveredAccessible": [],
                "textOwners": [], "accessibleOwners": []}
    document = documents[0]
    nodes = document.get("nodes") or {}
    node_names = nodes.get("nodeName") or []
    node_values = nodes.get("nodeValue") or []
    parents = nodes.get("parentIndex") or []
    raw_attrs = nodes.get("attributes") or []

    def string_at(index):
        return strings[index] if isinstance(index, int) and 0 <= index < len(strings) else ""

    count = len(node_names)
    names = [string_at(index).upper() for index in node_names]
    values = [string_at(node_values[i]) if i < len(node_values) else ""
              for i in range(count)]
    attributes = []
    for i in range(count):
        raw = raw_attrs[i] if i < len(raw_attrs) and isinstance(raw_attrs[i], list) else []
        attributes.append({string_at(raw[j]): string_at(raw[j + 1])
                           for j in range(0, len(raw) - 1, 2)})
    children = [[] for _ in range(count)]
    for child, parent in enumerate(parents):
        if isinstance(parent, int) and 0 <= parent < count:
            children[parent].append(child)
    layout_nodes = set((document.get("layout") or {}).get("nodeIndex") or [])

    def ancestry(index):
        result = []
        while isinstance(index, int) and 0 <= index < count:
            result.append(index)
            index = parents[index] if index < len(parents) else -1
        return result

    def descendants(index):
        result, pending = [], list(children[index])
        while pending:
            item = pending.pop(0)
            result.append(item)
            pending[0:0] = children[item]
        return result

    def exact_text(index):
        return "\n".join(normalize_copy(values[item]) for item in descendants(index)
                          if names[item] == "#TEXT" and normalize_copy(values[item]))

    def is_shell(index):
        for item in ancestry(index):
            classes = set(attributes[item].get("class", "").split())
            if (names[item] in ("HEADER", "FOOTER") or
                    "data-chrome-header" in attributes[item] or
                    classes.intersection(("chrome-footer", "skip-link")) or
                    "data-copy-section" in attributes[item]):
                return True
        return False

    def route_of(index):
        chain = ancestry(index)
        if is_shell(index):
            return "shared"
        for route in COPY_ROUTE_ROOTS:
            if any("data-%s" % route in attributes[item] for item in chain):
                return route
        return None

    def section_of(index, route):
        key = COPY_SECTION_ATTRIBUTES.get(route)
        return next((attributes[item][key] for item in ancestry(index)
                     if key and key in attributes[item]), None)

    ref_nodes = [i for i, attrs in enumerate(attributes) if attrs.get("data-copy-ref")]
    id_nodes = {attrs["id"]: i for i, attrs in enumerate(attributes)
                if attrs.get("id")}
    units = []
    for index in ref_nodes:
        gathered = {key: [normalize_copy(value)]
                    for key, value in attributes[index].items() if value}
        labelled = attributes[index].get("aria-labelledby", "").split()
        accessible = (" ".join(exact_text(id_nodes[item]) for item in labelled
                               if item in id_nodes) or
                      attributes[index].get("aria-label") or
                      attributes[index].get("alt") or exact_text(index))
        if accessible:
            gathered["computed-accessible-name"] = [normalize_copy(accessible)]
        route = route_of(index)
        units.append({"ref": attributes[index].get("data-copy-ref"),
                      "kind": attributes[index].get("data-copy-kind"),
                      "scope": attributes[index].get("data-copy-scope"),
                      "state": attributes[index].get("data-copy-state"),
                      "route": route, "section": section_of(index, route),
                      "text": exact_text(index), "attributes": gathered,
                      "rendered": index in layout_nodes})

    unscoped, uncovered_shell, uncovered_accessible = [], [], []
    text_owners, accessible_owners = [], []
    accessible_names = ("aria-label", "title", "alt", "placeholder",
                        "aria-description", "aria-valuetext",
                        "aria-roledescription")
    for index in range(count):
        chain = ancestry(index)
        owner = next((attributes[item].get("data-copy-ref") for item in chain
                      if attributes[item].get("data-copy-ref")), None)
        in_shell = is_shell(index)
        in_main = any(names[item] == "MAIN" for item in chain)
        excluded = any(names[item] in ("SCRIPT", "STYLE", "TEMPLATE") for item in chain)
        parent = parents[index] if index < len(parents) else -1
        visible = (parent in layout_nodes if names[index] == "#TEXT"
                   else index in layout_nodes)
        if (names[index] == "#TEXT" and normalize_copy(values[index]) and
                not excluded and visible and (in_main or in_shell)):
            row = {"text": normalize_copy(values[index]), "ownerRef": owner,
                   "region": "main" if in_main else "shell"}
            text_owners.append(row)
            if not owner:
                (unscoped if in_main else uncovered_shell).append(row["text"])
        if visible and (in_main or in_shell):
            for attr in accessible_names:
                if attributes[index].get(attr):
                    row = {"tag": names[index], "attribute": attr,
                           "value": attributes[index][attr],
                           "ownerRef": attributes[index].get("data-copy-ref")}
                    accessible_owners.append(row)
                    if not row["ownerRef"]:
                        uncovered_accessible.append(row)
    nested = [{"childRef": attributes[index]["data-copy-ref"],
               "ancestorRef": attributes[item]["data-copy-ref"]}
              for index in ref_nodes for item in ancestry(index)[1:]
              if attributes[item].get("data-copy-ref")]
    return {"units": units, "nestedRefs": nested, "unscoped": unscoped,
            "uncoveredShell": uncovered_shell,
            "uncoveredAccessible": uncovered_accessible,
            "textOwners": text_owners,
            "accessibleOwners": accessible_owners}


def enrich_computed_accessible_names(page: FS5Page, actual: dict,
                                     manifest: dict) -> dict:
    """Bind computed-name units to Chrome's accessibility tree or fail closed."""
    manifested_refs = {u["dataCopyRef"] for u in manifest["units"]
                       if u.get("accessibleAttributeName") ==
                       "computed-accessible-name"
                       and u.get("multiplicity", 0) > 0}
    actual_refs = {u.get("ref") for u in actual.get("units", [])}
    refs = manifested_refs & actual_refs
    units_by_ref = {}
    for unit in actual.get("units", []):
        if unit.get("ref") in refs:
            units_by_ref.setdefault(unit["ref"], []).append(unit)
    evidence = []
    try:
        root = page.cdp.call("DOM.getDocument", {"depth": 0, "pierce": True},
                             session_id=page.session)["root"]["nodeId"]
        for ref in sorted(refs):
            units = units_by_ref.get(ref, [])
            selector = '[data-copy-ref="%s"]' % ref
            node_ids = page.cdp.call("DOM.querySelectorAll", {
                "nodeId": root, "selector": selector},
                session_id=page.session).get("nodeIds", [])
            if len(node_ids) != len(units):
                for unit in units:
                    unit["computedAccessibleNameEvidence"] = {
                        "passed": False, "reason": "DOM occurrence mismatch",
                        "unitCount": len(units), "nodeCount": len(node_ids)}
                    unit.setdefault("attributes", {})["computed-accessible-name"] = []
                evidence.append({"ref": ref, "passed": False,
                                 "unitCount": len(units),
                                 "nodeCount": len(node_ids)})
                continue
            for occurrence, (unit, node_id) in enumerate(zip(units, node_ids)):
                result = page.cdp.call("Accessibility.getPartialAXTree", {
                    "nodeId": node_id, "fetchRelatives": False},
                    session_id=page.session)
                nodes = result.get("nodes") or []
                target = nodes[0] if nodes else {}
                name = (target.get("name") or {}).get("value")
                passed = bool(nodes and not target.get("ignored") and
                              isinstance(name, str) and normalize_copy(name))
                record = {"ref": ref, "occurrence": occurrence,
                          "passed": passed, "ignored": target.get("ignored"),
                          "name": normalize_copy(name) if isinstance(name, str) else None,
                          "axNodeId": target.get("nodeId")}
                unit["computedAccessibleNameEvidence"] = record
                unit.setdefault("attributes", {})["computed-accessible-name"] = (
                    [record["name"]] if passed else [])
                evidence.append(record)
    except Exception as exc:
        for units in units_by_ref.values():
            for unit in units:
                unit["computedAccessibleNameEvidence"] = {
                    "passed": False, "reason": "%s: %s" %
                    (type(exc).__name__, exc)}
                unit.setdefault("attributes", {})["computed-accessible-name"] = []
        evidence.append({"passed": False, "reason": "%s: %s" %
                         (type(exc).__name__, exc)})
    return {"records": evidence, "requiredRefs": sorted(refs),
            "passed": not refs or (bool(evidence) and
                                     all(x.get("passed") for x in evidence))}


def load_copy_manifest(value) -> tuple[dict, dict]:
    """Load the exact keyed copy authority; absence or ambiguity is fatal.

    This consumes COPY-UNIT-MANIFEST.json's flat ``units`` schema.  Dynamic
    ``exactStates`` are an explicit enum, not an invitation to fuzzy-match.
    """
    path = Path(value or DEFAULT_COPY_MANIFEST).resolve()
    try:
        relative = path.relative_to(REPO_ROOT).as_posix()
    except ValueError as exc:
        raise FS5Failure("copy manifest must be inside the immutable candidate: %s" % path) from exc
    if not path.is_file():
        raise FS5Failure(
            "exact copy authority is missing: %s; provide the keyed COPY-UNIT-MANIFEST.json"
            % relative)
    raw = path.read_bytes()
    try:
        doc = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise FS5Failure("copy manifest is not valid UTF-8 JSON: %s" % relative) from exc
    if doc.get("schemaVersion") != 1:
        raise FS5Failure("copy manifest schemaVersion must equal 1")
    route_names = {name for name, _, _ in ROUTES}
    roots = doc.get("routeRoots")
    if roots != COPY_ROUTE_ROOTS:
        raise FS5Failure("copy manifest routeRoots do not match runner selectors")
    sections = doc.get("sectionAnchorAttributes")
    if sections != COPY_SECTION_ATTRIBUTES:
        raise FS5Failure("copy manifest sectionAnchorAttributes do not match runner selectors")
    blockers = doc.get("blockers") or []
    if blockers:
        ids = [str(x.get("id", x)) if isinstance(x, dict) else str(x)
               for x in blockers]
        raise FS5Failure("copy manifest has unresolved blockers: %s" % ", ".join(ids))
    authorities = doc.get("authorityHashes")
    if not isinstance(authorities, dict) or not authorities:
        raise FS5Failure("copy manifest must bind authorityHashes")
    authority_records = []
    for authority_path, wanted_hash in sorted(authorities.items()):
        authority = (REPO_ROOT / authority_path).resolve()
        try:
            authority.relative_to(REPO_ROOT)
        except ValueError as exc:
            raise FS5Failure("authority file escapes candidate: %s" % authority_path) from exc
        if not authority.is_file():
            raise FS5Failure("copy authority file missing: %s" % authority_path)
        actual_hash = sha256(authority.read_bytes())
        if actual_hash != wanted_hash:
            raise FS5Failure("copy authority hash mismatch: %s" % authority_path)
        authority_records.append({"path": authority_path, "sha256": actual_hash})
    units = doc.get("units")
    if not isinstance(units, list) or not units:
        raise FS5Failure("copy manifest has no units")
    refs = []
    states_count = 0
    for unit in units:
        required = ("authorityFile", "authorityHash", "route",
                    "sectionAnchorValue", "dataCopyRef", "dataCopyKind",
                    "dataCopyScope", "multiplicity", "accessibleAttribute")
        if not isinstance(unit, dict) or any(k not in unit for k in required):
            raise FS5Failure("copy unit lacks required flat-schema fields: %r" % unit)
        route = unit["route"]
        ref = unit["dataCopyRef"]
        if route not in route_names | {"shared"}:
            raise FS5Failure("copy unit has unknown route: %s" % route)
        if not re.fullmatch(r"[a-z0-9][a-z0-9._-]*", str(ref)):
            raise FS5Failure("invalid dataCopyRef: %r" % ref)
        allowed_scopes = ("shell",) if route == "shared" else ("default", "progressive")
        if unit["dataCopyScope"] not in allowed_scopes:
            raise FS5Failure("invalid dataCopyScope for %s" % ref)
        if (type(unit["multiplicity"]) is not int or
                unit["multiplicity"] < 0):
            raise FS5Failure("invalid multiplicity for %s" % ref)
        if unit["multiplicity"] == 0 and not normalize_copy(unit.get("exclusionReason", "")):
            raise FS5Failure("zero-multiplicity exclusion lacks reason for %s" % ref)
        if unit.get("applicableState", "all") not in ({"all"} |
                                                       COPY_APPLICABLE_STATES):
            raise FS5Failure("invalid applicableState for %s" % ref)
        if (unit["authorityFile"] not in authorities or
                unit["authorityHash"] != authorities[unit["authorityFile"]]):
            raise FS5Failure("unit authority is not bound for %s" % ref)
        if not all(normalize_copy(str(unit[k])) for k in
                   ("sectionAnchorValue", "dataCopyKind")):
            raise FS5Failure("blank unit metadata for %s" % ref)
        has_text = "exactText" in unit
        has_states = "exactStates" in unit
        if has_text == has_states:
            raise FS5Failure("%s must define exactly one of exactText/exactStates" % ref)
        if has_text:
            if unit["exactText"] != normalize_copy(unit["exactText"]):
                raise FS5Failure("exactText is not normalized for %s" % ref)
        else:
            states = unit["exactStates"]
            if not isinstance(states, list) or not states:
                raise FS5Failure("empty exactStates for %s" % ref)
            ids = [x.get("id") for x in states if isinstance(x, dict)]
            if len(ids) != len(states) or len(ids) != len(set(ids)):
                raise FS5Failure("invalid or duplicate exactStates ids for %s" % ref)
            for state in states:
                if (not state.get("id") or state.get("text") !=
                        normalize_copy(state.get("text"))):
                    raise FS5Failure("invalid exactStates value for %s" % ref)
            required_states = unit.get("fs5RequiredState")
            if required_states is not None:
                required_states = ([required_states] if isinstance(required_states, str)
                                   else required_states)
                if (not isinstance(required_states, list) or not required_states or
                        any(not isinstance(x, str) for x in required_states) or
                        len(required_states) != len(set(required_states)) or
                        not set(required_states).issubset(set(ids))):
                    raise FS5Failure("invalid fs5RequiredState for %s" % ref)
            states_count += len(states)
        if type(unit["accessibleAttribute"]) is not bool:
            raise FS5Failure("accessibleAttribute must be Boolean for %s" % ref)
        if unit["accessibleAttribute"]:
            if unit.get("accessibleAttributeName") not in (
                    "aria-label", "alt", "title", "placeholder",
                    "computed-accessible-name"):
                raise FS5Failure("accessible attribute name missing for %s" % ref)
        refs.append(ref)
    if len(refs) != len(set(refs)):
        raise FS5Failure("duplicate dataCopyRef entries in manifest")
    represented = {u["route"] for u in units}
    if represented != route_names | {"shared"}:
        raise FS5Failure("copy units must represent shared and every route")
    positive_routes = {u["route"] for u in units if u["multiplicity"] > 0}
    if positive_routes != route_names | {"shared"}:
        raise FS5Failure("every route and shared shell requires a positive unit")
    metadata = {"path": relative, "sha256": sha256(raw),
                "authorityFiles": authority_records, "unitCount": len(units),
                "accessibleUnitCount": sum(bool(u["accessibleAttribute"])
                                           for u in units),
                "dynamicStateCount": states_count,
                "exclusionCount": sum(u["multiplicity"] == 0 for u in units),
                "blockerCount": 0}
    return doc, metadata


def reconcile_copy(route: str, actual: dict, manifest: dict,
                   applicable_states=()) -> dict:
    """Compare keyed DOM copy to authority with no fuzzy/sub-string fallback."""
    active_states = frozenset(applicable_states)
    unknown_states = active_states - COPY_APPLICABLE_STATES
    if unknown_states:
        raise FS5Failure("unknown copy applicable state(s): %s" %
                         ", ".join(sorted(unknown_states)))
    relevant_units = [u for u in manifest["units"]
                      if u["route"] in ("shared", route)]
    relevant = {u["dataCopyRef"]: u for u in relevant_units}
    def active(unit):
        state = unit.get("applicableState", "all")
        return state == "all" or state in active_states
    expected_units = [u for u in manifest["units"]
                      if u["route"] in ("shared", route) and u["multiplicity"] > 0
                      and active(u)]
    expected = {u["dataCopyRef"]: u for u in expected_units}
    actual_units = actual.get("units") if isinstance(actual, dict) else None
    if not isinstance(actual_units, list):
        actual_units = []
    actual_by_ref = {}
    malformed = []
    visible_inactive_refs = []
    for unit in actual_units:
        ref = unit.get("ref")
        if not ref:
            malformed.append(ref)
            continue
        wanted = relevant.get(ref)
        if (wanted is not None and wanted["multiplicity"] > 0 and
                not active(wanted)):
            if unit.get("rendered") is not False:
                visible_inactive_refs.append({
                    "ref": ref,
                    "rendered": unit.get("rendered"),
                    "reason": "inactive applicable unit must be explicitly hidden",
                })
            continue
        actual_by_ref.setdefault(ref, []).append(unit)
        if not all(unit.get(k) for k in ("kind", "scope", "section", "route")):
            malformed.append(ref)
    missing = sorted(set(expected) - set(actual_by_ref))
    extra = sorted(set(actual_by_ref) - set(expected))
    mismatches = []
    for ref in sorted(set(expected) & set(actual_by_ref)):
        wanted, occurrences = expected[ref], actual_by_ref[ref]
        if len(occurrences) != wanted["multiplicity"]:
            mismatches.append({"ref": ref, "field": "multiplicity",
                               "expected": wanted["multiplicity"],
                               "actual": len(occurrences)})
        for occurrence, got in enumerate(occurrences):
            fields = {"kind": (wanted["dataCopyKind"], got.get("kind")),
                      "scope": (wanted["dataCopyScope"], got.get("scope")),
                      "section": (wanted["sectionAnchorValue"], got.get("section")),
                      "route": (wanted["route"], got.get("route"))}
            if wanted.get("applicableState", "all") != "all":
                fields["rendered"] = (True, got.get("rendered") is True)
            if wanted["accessibleAttribute"]:
                attr = wanted["accessibleAttributeName"]
                observed = "\n".join(got.get("attributes", {}).get(attr, []))
                if attr == "computed-accessible-name":
                    fields["computedAccessibleNameEvidence"] = (
                        True,
                        (got.get("computedAccessibleNameEvidence") or {}).get(
                            "passed") is True)
            else:
                observed = got.get("text")
            observed = normalize_copy(observed)
            if "exactText" in wanted:
                fields["text"] = (wanted["exactText"], observed)
            else:
                states = {x["id"]: x["text"] for x in wanted["exactStates"]}
                state = got.get("state")
                fields["state"] = (True, state in states)
                fields["text"] = (states.get(state), observed)
            bad = {k: {"expected": pair[0], "actual": pair[1]}
                   for k, pair in fields.items() if pair[0] != pair[1]}
            if bad:
                mismatches.append({"ref": ref, "occurrence": occurrence,
                                   "fields": bad})
    uncovered = [normalize_copy(x) for x in actual.get("unscoped", [])
                 if normalize_copy(x)]
    uncovered_accessible = actual.get("uncoveredAccessible", []) or []
    uncovered_shell = [normalize_copy(x) for x in actual.get("uncoveredShell", [])
                       if normalize_copy(x)]
    text_owner_failures = []
    for row in actual.get("textOwners", []) or []:
        owner = relevant.get(row.get("ownerRef"))
        if owner is not None and owner["multiplicity"] > 0 and not active(owner):
            continue
        if owner is None or owner.get("accessibleAttribute") is not False:
            text_owner_failures.append(row)
    accessible_owner_failures = []
    for row in actual.get("accessibleOwners", []) or []:
        owner = relevant.get(row.get("ownerRef"))
        if owner is not None and owner["multiplicity"] > 0 and not active(owner):
            continue
        if (owner is None or owner.get("accessibleAttribute") is not True or
                owner.get("accessibleAttributeName") != row.get("attribute")):
            accessible_owner_failures.append(row)
    nested = actual.get("nestedRefs", []) or []
    nested_violations = []
    for pair in nested:
        if not isinstance(pair, dict):
            nested_violations.append(pair)
            continue
        ancestor = relevant.get(pair.get("ancestorRef"))
        child = relevant.get(pair.get("childRef"))
        if not (ancestor and ancestor.get("accessibleAttribute") is True and
                child and child.get("accessibleAttribute") is False):
            nested_violations.append(pair)
    passed = (not missing and not extra and not malformed and not mismatches and
              not visible_inactive_refs and
              not uncovered and not uncovered_shell and
              not uncovered_accessible and not text_owner_failures and
              not accessible_owner_failures and not nested_violations)
    return {"passed": passed, "expectedCount": sum(u["multiplicity"] for u in expected_units),
            "actualCount": sum(len(x) for x in actual_by_ref.values()),
            "missing": missing, "extra": extra,
            "malformedRefs": malformed, "mismatches": mismatches,
            "visibleInactiveRefs": visible_inactive_refs,
            "nestedRefs": nested_violations,
            "allowedNestedRefs": [x for x in nested if x not in nested_violations],
            "textOwnerFailures": text_owner_failures,
            "accessibleOwnerFailures": accessible_owner_failures,
            "activeApplicableStates": sorted(active_states),
            "uncoveredText": uncovered,
            "uncoveredShellText": uncovered_shell,
            "uncoveredAccessibleStrings": uncovered_accessible}


def declared_applicable_states(manifest: dict, route: str,
                               requested) -> frozenset:
    requested = frozenset(requested)
    unknown = requested - COPY_APPLICABLE_STATES
    if unknown:
        raise FS5Failure("unknown requested copy applicable state(s): %s" %
                         ", ".join(sorted(unknown)))
    return frozenset(state for state in requested if any(
        unit["route"] in ("shared", route) and unit.get("multiplicity", 0) > 0
        and unit.get("applicableState") == state
        for unit in manifest.get("units", [])))


def live_copy_reconciliation(page: FS5Page, route: str, manifest: dict,
                             applicable_states=()) -> dict:
    actual = page.evaluate(BASE_MEASURE % "[]", await_promise=True)["copy"]
    ax = enrich_computed_accessible_names(page, actual, manifest)
    active = declared_applicable_states(manifest, route, applicable_states)
    result = reconcile_copy(route, actual, manifest, applicable_states=active)
    result["requestedApplicableStates"] = sorted(applicable_states)
    result["computedAccessibleNames"] = ax
    return result


def observe_copy_states(page: FS5Page, manifest: dict, label: str) -> list:
    expected = {u["dataCopyRef"]: u for u in manifest["units"]
                if "exactStates" in u and u["multiplicity"] > 0}
    actual = page.evaluate(BASE_MEASURE % "[]", await_promise=True)["copy"]["units"]
    observations = []
    for unit in actual:
        wanted = expected.get(unit.get("ref"))
        if not wanted:
            continue
        state = unit.get("state")
        states = {x["id"]: x["text"] for x in wanted["exactStates"]}
        text_value = normalize_copy(unit.get("text"))
        observations.append({"label": label, "route": wanted["route"],
                             "ref": unit.get("ref"), "state": state,
                             "text": text_value,
                             "passed": state in states and states.get(state) == text_value})
    return observations


def copy_state_coverage(manifest: dict, observations: list) -> dict:
    dynamic_units = [u for u in manifest["units"]
                     if "exactStates" in u and u["multiplicity"] > 0]
    allowed = {(u["route"], u["dataCopyRef"], state["id"])
               for u in dynamic_units for state in u["exactStates"]}
    required = set()
    for unit in dynamic_units:
        state_ids = unit.get("fs5RequiredState")
        if state_ids is None:
            state_ids = [state["id"] for state in unit["exactStates"]]
        elif isinstance(state_ids, str):
            state_ids = [state_ids]
        required.update((unit["route"], unit["dataCopyRef"], state_id)
                        for state_id in state_ids)
    observed = {(o.get("route"), o.get("ref"), o.get("state"))
                for o in observations if o.get("passed") is True}
    unexpected = [o for o in observations if o.get("passed") is not True]
    missing = sorted(required - observed)
    extra = sorted(observed - allowed)
    optional = sorted((observed & allowed) - required)
    return {"required": [list(x) for x in sorted(required)],
            "observed": [list(x) for x in sorted(observed)],
            "observations": observations, "missing": [list(x) for x in missing],
            "optionalObserved": [list(x) for x in optional],
            "extra": [list(x) for x in extra], "unexpected": unexpected,
            "passed": not missing and not extra and not unexpected}


def timeline_copy_state_observations(timing: dict, manifest: dict,
                                     label: str) -> list:
    expected = {u["dataCopyRef"]: u for u in manifest["units"]
                if "exactStates" in u and u["multiplicity"] > 0}
    rows = []
    for event_index, event in enumerate((timing.get("raw") or {}).get("timeline", [])):
        for unit in event.get("copyStates", []) or []:
            wanted = expected.get(unit.get("ref"))
            if not wanted:
                continue
            states = {x["id"]: x["text"] for x in wanted["exactStates"]}
            state = unit.get("state")
            observed = normalize_copy(unit.get("text"))
            rows.append({"label": "%s-%s" % (label, event_index),
                         "route": wanted["route"], "ref": unit.get("ref"),
                         "state": state, "text": observed,
                         "passed": state in states and states.get(state) == observed})
    return rows


def screenshot_record(root: Path, records: list, snapshot: str, relative: str,
                      data: bytes, route: str, lane: str, viewport: tuple, kind: str):
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    dims = p2.png_size(data)
    record = {"path": relative, "sha256": sha256(data), "bytes": len(data),
              "pixelDimensions": dims, "snapshotId": snapshot, "route": route,
              "lane": lane, "viewport": list(viewport), "kind": kind}
    records.append(record)
    return record


def visual_pair_metadata(shots: list, snapshot: str) -> dict:
    canonical = [s for s in shots if s.get("route") in VISUAL_ROUTES and
                 tuple(s.get("viewport", ())) in VISUAL_VIEWPORTS and
                 s.get("lane") == "base-matrix" and
                 s.get("kind") in ("viewport", "full-page-documentation")]
    by_key = {(s["route"], tuple(s["viewport"]), s["kind"]): s
              for s in canonical}
    expected = {(r, v, k) for r in VISUAL_ROUTES for v in VISUAL_VIEWPORTS
                for k in ("viewport", "full-page-documentation")}
    continuity = []
    for route in VISUAL_ROUTES:
        for left, right in zip(VISUAL_VIEWPORTS, VISUAL_VIEWPORTS[1:]):
            continuity.append({"id": "%s-%sx%s-to-%sx%s" %
                               (route, left[0], left[1], right[0], right[1]),
                               "route": route, "left": list(left), "right": list(right),
                               "shots": [by_key.get((route, left, "viewport")),
                                         by_key.get((route, right, "viewport"))]})
    silhouette = []
    route_pairs = tuple(zip(VISUAL_ROUTES, VISUAL_ROUTES[1:] + VISUAL_ROUTES[:1]))
    for viewport in VISUAL_VIEWPORTS:
        for left, right in route_pairs:
            silhouette.append({"id": "%s-vs-%s-%sx%s" %
                               (left, right, viewport[0], viewport[1]),
                               "viewport": list(viewport), "left": left, "right": right,
                               "shots": [by_key.get((left, viewport, "viewport")),
                                         by_key.get((right, viewport, "viewport"))]})
    rhythm = [{"id": "%s-%sx%s-first-vs-full" % (route, v[0], v[1]),
               "route": route, "viewport": list(v),
               "shots": [by_key.get((route, v, "viewport")),
                         by_key.get((route, v, "full-page-documentation"))]}
              for route in VISUAL_ROUTES for v in VISUAL_VIEWPORTS]
    return {"schemaVersion": 1, "snapshotId": snapshot,
            "protocolPath": VISUAL_PROTOCOL.relative_to(REPO_ROOT).as_posix(),
            "protocolSha256": sha256(VISUAL_PROTOCOL.read_bytes()) if VISUAL_PROTOCOL.is_file() else None,
            "canonicalScreenshotCount": len(canonical),
            "complete": set(by_key) == expected and len(canonical) == len(expected),
            "canonicalScreenshotSha256": {s["path"]: s["sha256"] for s in canonical},
            "breakpointContinuity": continuity,
            "routeSilhouette": silhouette, "whitespaceRhythm": rhythm}


def external_visual_review(review_path, metadata: dict) -> dict:
    """Validate, but never manufacture, caption-free/grayscale judgment."""
    if not review_path:
        return {"passed": False, "hardFailure":
                "external visual pair review is required; pass --visual-review JSON",
                "expected": {"snapshotId": metadata["snapshotId"],
                             "protocolSha256": metadata["protocolSha256"],
                             "canonicalScreenshotSha256": metadata["canonicalScreenshotSha256"]}}
    path = Path(review_path).resolve()
    if not path.is_file():
        return {"passed": False, "hardFailure": "visual review file missing: %s" % path}
    try:
        review = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        return {"passed": False, "hardFailure": "invalid visual review JSON: %s" % exc}
    required_ids = {
        "breakpointContinuity": {x["id"] for x in metadata["breakpointContinuity"]},
        "routeSilhouette": {x["id"] for x in metadata["routeSilhouette"]},
        "whitespaceRhythm": {x["id"] for x in metadata["whitespaceRhythm"]},
    }
    failures = []
    if review.get("schemaVersion") != 1:
        failures.append("schemaVersion")
    if review.get("snapshotId") != metadata["snapshotId"]:
        failures.append("snapshotId")
    if review.get("protocolSha256") != metadata["protocolSha256"]:
        failures.append("protocolSha256")
    if review.get("canonicalScreenshotSha256") != metadata["canonicalScreenshotSha256"]:
        failures.append("canonicalScreenshotSha256")
    reviewer = review.get("reviewer") or {}
    if reviewer.get("kind") not in ("human", "fable") or not reviewer.get("name"):
        failures.append("reviewer")
    for category, wanted in required_ids.items():
        rows = review.get(category)
        actual = {row.get("id") for row in rows or [] if isinstance(row, dict)}
        if (actual != wanted or len(rows or []) != len(wanted) or not rows or
                not all(row.get("passed") is True for row in rows)):
            failures.append(category)
    two_second = review.get("twoSecondRouteChecks") or []
    fidelity = review.get("assetRenderFidelity") or []
    if (len(two_second) != len(VISUAL_ROUTES) or
            {x.get("route") for x in two_second} != set(VISUAL_ROUTES) or
            not all(x.get("passed") is True for x in two_second)):
        failures.append("twoSecondRouteChecks")
    if (len(fidelity) != len(VISUAL_ROUTES) or
            {x.get("route") for x in fidelity} != set(VISUAL_ROUTES) or
            not all(x.get("passed") is True for x in fidelity)):
        failures.append("assetRenderFidelity")
    return {"passed": not failures, "path": str(path),
            "sha256": sha256(path.read_bytes()), "failures": failures,
            "review": review}


def h1_line_limit(route: str, width: int) -> int:
    """Return the route-specific authored H1 ceiling at a CSS width."""
    if route == "home":
        return 2 if width >= 1024 else (3 if width >= 768 else (4 if width >= 390 else 5))
    if route == "transformation":
        return 3 if width >= 1280 else (4 if width >= 390 else 5)
    if route == "workgraph":
        return 2 if width >= 1024 else (3 if width >= 768 else (5 if width >= 390 else 6))
    if route == "build":
        return 4 if width >= 390 else 5
    if route == "trust":
        return 2 if width >= 1024 else (3 if width >= 390 else 4)
    if route == "company":
        return 3 if width >= 1024 else (5 if width >= 390 else 6)
    if route == "assessment":
        return 3 if width >= 390 else 4
    if route == "impact":
        return 2 if width >= 1024 else (3 if width >= 390 else 4)
    raise FS5Failure("missing H1 line contract for route %s" % route)


def home_disclosure_gate(disclosure: dict) -> bool:
    """Require one rendered disclosure before the first synthetic record."""
    return (
        disclosure.get("count") == 1 and
        disclosure.get("rendered") is True and
        disclosure.get("firstSyntheticRef") == "home.record.identity" and
        disclosure.get("precedes") is True
    )


def matrix_assertions(route: str, viewport: tuple, facts: dict, network: dict,
                      snapshot: str, copy_manifest: dict):
    checks = []
    assertion(checks, "snapshot meta", facts.get("snapshot") == snapshot, facts.get("snapshot"))
    v = facts.get("viewport", {})
    assertion(checks, "exact CSS viewport", (round(v.get("width", -1)), round(v.get("height", -1))) == viewport, v)
    assertion(checks, "visible target", facts.get("visibility") == "visible", facts.get("visibility"))
    assertion(checks, "200ms timer not throttled", 180 <= facts.get("timerElapsed", 9999) <= 250, facts.get("timerElapsed"))
    assertion(checks, "no horizontal overflow", facts["scroll"]["scrollWidth"] == facts["scroll"]["clientWidth"], facts["scroll"])
    structure = facts["structure"]
    assertion(checks, "one header main footer", (structure["header"], structure["main"], structure["footer"]) == (1, 1, 1), structure)
    assertion(checks, "one H1", structure["h1"] == 1, structure["h1"])
    assertion(checks, "no heading skip", not structure["skips"], structure["skips"])
    assertion(checks, "no duplicate ID", not structure["duplicateIds"], structure["duplicateIds"])
    assertion(checks, "all images complete with intrinsic size", all(i["complete"] and i["naturalWidth"] > 0 and i["naturalHeight"] > 0 for i in facts["images"]), facts["images"])
    target_failures = [x for x in facts["focusables"]
                       if x["rect"]["width"] < (48 if x["inNav"] or x["inAssessment"] else 44)
                       or x["rect"]["height"] < (48 if x["inNav"] or x["inAssessment"] else 44)]
    assertion(checks, "interactive target sizes", not target_failures, target_failures)
    h1 = facts.get("h1") or {}
    size_limit = 92 if route == "home" else 68
    line_limit = h1_line_limit(route, viewport[0])
    h1_geometry_present = (
        isinstance(h1.get("fontSize"), (int, float)) and
        isinstance(h1.get("lineHeight"), (int, float)) and
        isinstance(h1.get("lineCount"), int) and
        h1.get("rect") is not None and h1.get("lineCount", 0) > 0
    )
    assertion(checks, "H1 geometry measured", h1_geometry_present, h1)
    assertion(
        checks, "H1 size and integer line count",
        h1_geometry_present and
        h1["fontSize"] <= size_limit + .5 and
        h1["lineCount"] <= line_limit,
        {"fontSize": h1.get("fontSize"), "lineCount": h1.get("lineCount"),
         "limits": {"fontSize": size_limit, "lineCount": line_limit}},
    )
    heights = [x["height"] for x in facts["sections"] if x["height"] > 0]
    assertion(checks, "route rhythm ratio", len(heights) >= 2 and max(heights) / min(heights) >= 2.5,
              {"heights": heights, "ratio": max(heights) / min(heights) if len(heights) >= 2 else None})
    for name in ("unresolved", "orphanEvents", "failed", "httpErrors", "remote", "console", "missingSnapshotHeaders"):
        assertion(checks, "network %s empty" % name, not network[name], network[name])
    if viewport in FIRST_VIEWPORTS:
        contract = FIRST_VIEW_CONTRACTS.get((route, viewport))
        assertion(checks, "first-viewport contract declared", contract is not None,
                  {"route": route, "viewport": viewport})
        expected_ids = [x["id"] for x in (contract or ())]
        observed_ids = [x.get("id") for x in facts["firstView"]]
        assertion(checks, "first-viewport contract complete",
                  observed_ids == expected_ids,
                  {"expected": expected_ids, "actual": observed_ids})
        for item in facts["firstView"]:
            assertion(checks, "first-viewport %s" % item.get("id"),
                      item.get("passed") is True,
                      item)
    low, high = COPY_BANDS[route]
    assertion(checks, "default copy band", low <= facts["copy"]["default"] <= high, {"count": facts["copy"]["default"], "band": [low, high]})
    assertion(checks, "progressive copy ceiling",
              facts["copy"]["progressive"] <= PROGRESSIVE_MAX[route],
              {"count": facts["copy"]["progressive"],
               "ceiling": PROGRESSIVE_MAX[route]})
    assertion(checks, "copy fully scoped", not facts["copy"]["unscoped"], facts["copy"]["unscoped"][:20])
    copy_result = reconcile_copy(route, facts["copy"], copy_manifest)
    assertion(checks, "exact keyed copy authority", copy_result["passed"],
              copy_result)
    if route == "home":
        h = facts["routeFacts"]["home"]
        required = ("Request", "Operating reality", "Decision retained", "Governed execution", "Evidence returns")
        assertion(checks, "Home static Request and four states", len(h["states"]) == 4 and all(t in (h["bodyText"] or "") for t in required), h)
        assertion(checks, "Home no junk state tab stop", h["stateTabStops"] == 0, h["stateTabStops"])
        assertion(checks, "Home resolved copy has no WG-041", "WG-041" not in (h["bodyText"] or ""), h["bodyText"])
        assertion(
            checks,
            "Home disclosure precedes first synthetic identifier",
            home_disclosure_gate(h["disclosure"]),
            h["disclosure"],
        )
    if route == "transformation":
        t = facts["routeFacts"]["transformation"]
        assertion(checks, "Transformation provenance visible outside details", t["provenanceVisible"] and not t["provenanceInsideDetails"], t)
        if viewport[0] < 1180 or facts["inputCapabilities"]["coarse"]:
            assertion(checks, "all five Transformation explanations visible", len(t["outcomes"]) == 5 and all(o["visible"] for o in t["outcomes"]), t["outcomes"])
    if route == "build":
        b = facts["buildContract"]
        assertion(checks, "Build summary/link contract", b == {"summaryTag": "SUMMARY", "summaryText": b.get("summaryText"), "firstText": "Build overview The decision becomes a build with a boundary.", "firstHref": "/preview/golden-standard/routes/build/", "nestedLink": False} or (b.get("summaryTag") == "SUMMARY" and (b.get("summaryText") or "").startswith("Build") and (b.get("firstText") or "").startswith("Build overview") and b.get("firstHref") == "/preview/golden-standard/routes/build/" and not b.get("nestedLink")), b)
    return checks


class LinkParser(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"])


def audit_links(base_url: str, snapshot: str, source_rows: list):
    records, cache, failures = [], {}, []
    for row in source_rows:
        route = row["route"]
        for link in row["measurement"]["links"]:
            href = link.get("href") or ""
            rec = {"sourceRoute": route, "text": link.get("text"), "href": href, "passed": True}
            if href.startswith("mailto:"):
                rec["kind"] = "mailto"
            elif href.startswith(("http://", "https://")) and urllib.parse.urlsplit(href).netloc != urllib.parse.urlsplit(base_url).netloc:
                rec.update(passed=False, reason="remote link")
            else:
                absolute = urllib.parse.urljoin(base_url + row["path"], href)
                parsed = urllib.parse.urlsplit(absolute)
                key = parsed.path
                if key not in cache:
                    code, headers, body = p2.fetch(base_url, key)
                    parser = LinkParser()
                    if code == 200:
                        parser.feed(body.decode("utf-8", "replace"))
                    cache[key] = (code, {k.lower(): v for k, v in headers.items()}, parser.ids)
                code, headers, ids = cache[key]
                ok = code == 200 and headers.get(SNAPSHOT_HEADER) == snapshot and (not parsed.fragment or parsed.fragment in ids)
                rec.update(kind="local", destination=key, fragment=parsed.fragment or None, status=code, passed=ok)
                if link.get("text") == "Start an assessment" and key != ASSESSMENT_PATH:
                    rec.update(passed=False, reason="visible Assessment CTA has wrong destination")
                if route != "impact" and key.rstrip("/").endswith("/impact"):
                    rec.update(passed=False, reason="Impact linked while gated")
            records.append(rec)
            if not rec["passed"]:
                failures.append(rec)
    return {"schemaVersion": SCHEMA_VERSION, "snapshotId": snapshot, "records": records, "passed": not failures, "failures": failures}


def static_lane_assertions(route, facts, copy_manifest):
    checks = []
    text = facts["dom"]["text"]
    expected = {
        "home": ("Operating reality", "Decision retained", "Governed execution", "Evidence returns"),
        "transformation": ("Preserve", "Simplify", "Automate", "Rebuild", "Retire"),
        "workgraph": ("Connect", "Decide", "Build", "Learn"),
        "build": ("Intervention", "Specification", "Architecture", "Build", "Evaluation", "Governed review"),
        "assessment": ("hello@dagg.ai",),
    }.get(route, ())
    assertion(checks, "DOM snapshot nonempty", facts["dom"]["nodeCount"] > 0, facts["dom"]["nodeCount"])
    assertion(checks, "accessibility tree nonempty", facts["accessibility"]["nodeCount"] > 0, facts["accessibility"]["nodeCount"])
    positions = [text.find(token) for token in expected]
    assertion(checks, "static route meaning present in source order",
              all(x >= 0 for x in positions) and positions == sorted(positions),
              {"tokens": expected, "positions": positions})
    ax_names = [x.get("name") for x in facts["accessibility"]["nodes"]]
    assertion(checks, "routes remain reachable", sum(1 for x in facts["accessibility"]["nodes"] if x.get("role") == "link") > 0,
              ax_names[:30])
    inert_names = {"Pause sequence", "Replay sequence", "Inspect resolved progression"}
    assertion(checks, "no inert timed controls in no-JS accessibility tree",
              not inert_names.intersection({x for x in ax_names if x}),
              sorted(inert_names.intersection({x for x in ax_names if x})))
    copy_result = reconcile_copy(route, facts.get("copy", {}), copy_manifest,
                                 applicable_states={"no-js"})
    assertion(checks, "exact keyed no-JS copy authority", copy_result["passed"],
              copy_result)
    if route == "assessment":
        assertion(checks, "Assessment noscript mail path", facts["dom"]["noscriptCount"] >= 1 and "hello@dagg.ai" in text, facts["dom"])
    return checks


def run_axe(page: FS5Page, axe_source: str | None):
    if not axe_source:
        return {"passed": False, "hardFailure": "axe-core source unavailable; set --axe-script or DAGG_AXE_SCRIPT"}
    if page.evaluate("typeof axe==='undefined'"):
        page.evaluate(axe_source)
    result = page.evaluate("axe.run(document,{resultTypes:['violations']})", await_promise=True)
    bad = [v for v in result.get("violations", []) if v.get("impact") in ("critical", "serious")]
    return {"passed": not bad, "criticalOrSerious": bad, "violationCount": len(result.get("violations", []))}


def axe_state_lanes(cdp, base_url, snapshot, axe_source):
    """Run axe in defaults and every discoverable opened/record state."""
    records = []

    def add(route, state, result, assertion_detail=None, page=None):
        network = page.events() if page is not None else None
        network_clean = (network is not None and not any(network[k] for k in
            ("unresolved", "orphanEvents", "failed", "httpErrors", "remote",
             "console", "missingSnapshotHeaders")))
        passed = result.get("passed") is True and not (
            isinstance(assertion_detail, dict) and assertion_detail.get("passed") is False) and network_clean
        records.append({"route": route, "state": state, "result": result,
                        "stateAssertion": assertion_detail, "network": network,
                        "passed": passed})

    for route, path, _ in ROUTES:
        for width, height in ((1440, 900), (390, 844)):
            def defaults(page, n=route, p=path, w=width, h=height):
                page.navigate(base_url + p, w, h, touch=w < 600)
                add(n, "default-%dx%d" % (w, h), run_axe(page, axe_source), page=page)
            fresh(cdp, base_url, snapshot, defaults)

        def disclosures(page, n=route, p=path):
            page.navigate(base_url + p, 390, 844, touch=True)
            page.evaluate(r"""[...document.querySelectorAll('main details')].forEach((d,i)=>{
              d.setAttribute('data-fs5-axe-detail-index',String(i));
              const s=d.querySelector(':scope > summary');if(s)s.setAttribute('data-fs5-axe-summary-index',String(i));});""")
            total = page.evaluate("document.querySelectorAll('main details').length")
            covered = set()
            for _ in range(total + 2):
                states = page.evaluate(r"""[...document.querySelectorAll('main details')].map((d,i)=>{const s=d.querySelector(':scope > summary');const r=s&&s.getBoundingClientRect();const style=s&&getComputedStyle(s);return {index:i,open:d.open,text:s&&s.textContent.replace(/\s+/g,' ').trim(),visible:!!(s&&r&&r.width&&r.height&&style.display!=='none'&&style.visibility!=='hidden')}})""")
                candidates = [x for x in states if x["visible"] and x["index"] not in covered]
                if not candidates:
                    break
                for state in candidates:
                    selector = '[data-fs5-axe-summary-index="%s"]' % state["index"]
                    if not state["open"]:
                        probe = page.touch(selector, cancel=False)
                        page.wait(30)
                    else:
                        probe = {"passed": True, "alreadyOpen": True}
                    opened = page.evaluate("document.querySelector('[data-fs5-axe-detail-index=%s]').open" % json.dumps(str(state["index"])))
                    state_check = {"passed": probe.get("passed") is True and opened is True,
                                   "touch": probe, "open": opened,
                                   "summary": state["text"]}
                    add(n, "disclosure-%s-open" % state["index"],
                        run_axe(page, axe_source), state_check, page)
                    covered.add(state["index"])
            if len(covered) != total:
                add(n, "disclosure-coverage", {"passed": False,
                    "hardFailure": "not every main disclosure became touch-reachable"},
                    {"passed": False, "expected": total, "covered": sorted(covered)}, page)
        fresh(cdp, base_url, snapshot, disclosures)

    def header_states(page):
        page.navigate(base_url + ROUTES[0][1], 1440, 900)
        page.mouse("[data-flyout-trigger]")
        opened = wait_browser_condition(page, "document.querySelector('[data-flyout]').open", 400)
        add("global-header", "desktop-build-open", run_axe(page, axe_source), opened, page)
    fresh(cdp, base_url, snapshot, header_states)

    def mobile_header(page):
        page.navigate(base_url + ROUTES[0][1], 390, 844, touch=True)
        first = page.touch("[data-summary]", cancel=False); page.wait(50)
        add("global-header", "mobile-sheet-open", run_axe(page, axe_source),
            {"passed": first["passed"] and page.evaluate("document.querySelector('[data-disclosure]').open")}, page)
        second = page.touch("[data-flyout-trigger]", cancel=False); page.wait(50)
        add("global-header", "mobile-sheet-build-open", run_axe(page, axe_source),
            {"passed": second["passed"] and page.evaluate("document.querySelector('[data-flyout]').open")}, page)
    fresh(cdp, base_url, snapshot, mobile_header)

    # Timed Home/Factory record states are paused only while axe inspects the
    # live state; advancement before/after remains driven by route JavaScript.
    for route, path, selector, state_expr, expected_states in (
        ("home", ROUTES[0][1], "[data-home-execution-states]",
         "document.querySelector('[data-home-execution]').dataset.homeStateIndex",
         ("0", "1", "2", "3")),
        ("build", dict((n, p) for n, p, _ in ROUTES)["build"],
         "[data-build-factory-stages]",
         "String([...document.querySelectorAll('[data-build-stage]')].findIndex(x=>x.classList.contains('build-stage--active')))",
         ("0", "1", "2", "3", "4", "5")),
    ):
        def timed_states(page, n=route, p=path, hover=selector,
                         expression=state_expr, states=expected_states):
            page.navigate(base_url + p, 1440, 900)
            page.evaluate("document.querySelector(%s).scrollIntoView({block:'center'})" % json.dumps(hover))
            for wanted in states:
                waited = wait_browser_condition(page, "(%s)===%s" % (expression, json.dumps(wanted)), 3500)
                if waited["passed"]:
                    page.mouse(hover); page.wait(30)
                state_check = {"passed": waited["passed"], "wanted": wanted,
                               "observed": page.evaluate(expression), "wait": waited}
                add(n, "record-state-%s" % wanted, run_axe(page, axe_source), state_check, page)
                page.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": 1, "y": 1}, session_id=page.session)
        fresh(cdp, base_url, snapshot, timed_states)

    def transformation_records(page):
        path = dict((n, p) for n, p, _ in ROUTES)["transformation"]
        page.navigate(base_url + path, 1024, 768, touch=True)
        values = page.evaluate("[...document.querySelectorAll('input[name=outcome]')].map((e,i)=>{e.setAttribute('data-fs5-axe-outcome',String(i));return e.value})")
        for index, wanted in enumerate(values):
            probe = page.touch('[data-fs5-axe-outcome="%s"]' % index,
                               cancel=False); page.wait(30)
            selected = page.evaluate("(document.querySelector('input[name=outcome]:checked')||{}).value")
            add("transformation", "record-outcome-%s" % wanted,
                run_axe(page, axe_source),
                {"passed": probe["passed"] and selected == wanted,
                 "wanted": wanted, "selected": selected, "touch": probe}, page)
    fresh(cdp, base_url, snapshot, transformation_records)

    def workgraph_records(page):
        path = dict((n, p) for n, p, _ in ROUTES)["workgraph"]
        page.navigate(base_url + path, 1440, 900)
        states = ("connect", "decide", "build", "learn")
        geometry = page.evaluate("(()=>{const e=document.querySelector('[data-workgraph-section=lifecycle]');return {top:e.offsetTop,travel:Math.max(1,e.offsetHeight-innerHeight)}})()")
        for index, wanted in enumerate(states):
            position = geometry["top"] + geometry["travel"] * (index / (len(states) - 1))
            page.evaluate("scrollTo(0,%s)" % position)
            waited = wait_browser_condition(page,
                "document.querySelector('[data-workgraph-record-state]').dataset.workgraphActiveState===%s" % json.dumps(wanted), 1500)
            add("workgraph", "record-state-%s" % wanted,
                run_axe(page, axe_source),
                {"passed": waited["passed"], "wanted": wanted,
                 "observed": page.evaluate("document.querySelector('[data-workgraph-record-state]').dataset.workgraphActiveState"),
                 "wait": waited}, page)
    fresh(cdp, base_url, snapshot, workgraph_records)

    return {"records": records, "expectedDefaultStates": len(ROUTES) * 2,
            "passed": bool(records) and all(row["passed"] for row in records)}


CONTROL_DISCOVERY = r"""
(() => {
  const rendered=el=>{if(!el||!el.getClientRects().length)return false;
    const s=getComputedStyle(el);return s.display!=='none'&&s.visibility!=='hidden'&&s.pointerEvents!=='none'};
  const controls=[...document.querySelectorAll('header a[href],header button,header input:not([type="hidden"]),header textarea,header select,header summary,header [role="button"],header [tabindex]:not([tabindex="-1"]),main a[href],main button,main input:not([type="hidden"]),main textarea,main select,main summary,main [role="button"],main [tabindex]:not([tabindex="-1"]),footer a[href],footer button,footer input:not([type="hidden"]),footer textarea,footer select,footer summary,footer [role="button"],footer [tabindex]:not([tabindex="-1"])')]
    .filter((el,index,all)=>all.indexOf(el)===index);
  controls.forEach((el,index)=>el.setAttribute('data-fs5-touch-index',String(index)));
  return {candidateCount:controls.length,controls:controls.map((el,index)=>({index,
    tag:el.tagName,type:el.getAttribute('type'),href:el.getAttribute('href'),
    text:(el.textContent||el.getAttribute('aria-label')||'').replace(/\s+/g,' ').trim(),
    rendered:rendered(el),disabled:!!el.disabled,hidden:el.hidden,
    closedAncestor:!!el.closest('details:not([open])')}))};
})()
"""


def touch_traverse_route(page: FS5Page, route: str, url: str,
                         copy_manifest: dict) -> dict:
    """Deliver trusted CDP touch events to every route control/state.

    Links receive touchstart+touchcancel so the evidence run cannot open a mail
    client or leave the immutable origin; their destinations are independently
    proved by anchors.json.  State controls receive a complete touch gesture so
    disclosures, radios and record selectors reveal their subsequent controls.
    """
    facts = page.navigate(url, 390, 844, touch=True)
    checks, attempts, seen, activated = [], [], set(), set()
    state_observations = observe_copy_states(page, copy_manifest,
                                             "%s-touch-initial" % route)
    caps = facts["inputCapabilities"]
    assertion(checks, "real touch capability", caps["touch"] > 0 and caps["coarse"], caps)
    page.evaluate("for(const e of document.querySelectorAll('[data-home-execution],[data-build-factory-progress]'))e.scrollIntoView({block:'center'})")
    page.wait(300)
    for round_index in range(8):
        discovery = page.evaluate(CONTROL_DISCOVERY)
        visible = [c for c in discovery["controls"] if c["rendered"] and not c["disabled"]]
        changed = False
        for control in visible:
            index = control["index"]
            selector = '[data-fs5-touch-index="%s"]' % index
            if index not in seen:
                try:
                    probe = page.touch(selector, cancel=True)
                except Exception as exc:
                    attempts.append({"control": control, "passed": False,
                                     "error": "%s: %s" % (type(exc).__name__, exc)})
                else:
                    attempts.append({"control": control, "probe": probe,
                                     "passed": probe["passed"]})
                    if probe["passed"]:
                        seen.add(index)
                        changed = True
            should_activate = (control["tag"] == "SUMMARY" or
                               control["type"] in ("radio", "checkbox") or
                               (control["tag"] in ("BUTTON",) and
                                control["type"] != "submit" and
                                index not in activated and
                                "pause" not in control["text"].lower()))
            if should_activate and index not in activated:
                try:
                    activation = page.touch(selector, cancel=False)
                except Exception as exc:
                    attempts.append({"control": control, "activation": True,
                                     "passed": False,
                                     "error": "%s: %s" % (type(exc).__name__, exc)})
                else:
                    attempts.append({"control": control, "activation": True,
                                     "probe": activation,
                                     "passed": activation["passed"]})
                    if activation["passed"]:
                        activated.add(index)
                        changed = True
                page.wait(50)
                state_observations.extend(observe_copy_states(
                    page, copy_manifest,
                    "%s-touch-control-%s" % (route, index)))
        # Home's replay control is intentionally time-gated; allow the one
        # complete finite pass to reveal it without inventing DOM state.
        if route == "home" and round_index == 0:
            page.wait(sum(HOME_INTERVALS_MS) + 700)
            changed = True
        if not changed:
            break
    final = page.evaluate(CONTROL_DISCOVERY)
    disabled = [c for c in final["controls"] if c["disabled"]]
    all_indices = {c["index"] for c in final["controls"] if not c["disabled"]}
    missed = [c for c in final["controls"] if not c["disabled"] and c["index"] not in seen]
    assertion(checks, "every non-disabled route control received trusted CDP touch",
              seen == all_indices and all(a.get("passed") for a in attempts),
              {"candidateCount": len(all_indices), "seen": sorted(seen),
               "missed": missed, "failedAttempts": [a for a in attempts if not a.get("passed")]})
    assertion(checks, "route controls exist", bool(all_indices), final)
    assertion(checks, "no route control is disabled and untestable",
              not disabled, disabled)
    return {"route": route, "viewport": [390, 844], "assertions": checks,
            "attempts": attempts, "candidateCount": len(all_indices),
            "seenCount": len(seen), "missed": missed,
            "copyStateObservations": state_observations,
            "passed": all_passed(checks)}


def interval_evidence(timeline: list, expected: tuple,
                      tolerance: int = INTERVAL_TOLERANCE_MS) -> dict:
    """Validate every adjacent state interval; missing/extra samples fail."""
    samples = []
    for event in timeline or []:
        try:
            index = int(event.get("index"))
            at = float(event.get("at"))
        except (TypeError, ValueError, AttributeError):
            continue
        if not samples or samples[-1]["index"] != index:
            samples.append({"index": index, "at": at})
    intervals = [round(samples[i + 1]["at"] - samples[i]["at"], 3)
                 for i in range(len(samples) - 1)]
    comparisons = [{"index": index, "expectedMs": wanted,
                    "actualMs": intervals[index] if index < len(intervals) else None,
                    "toleranceMs": tolerance,
                    "passed": index < len(intervals) and
                    abs(intervals[index] - wanted) <= tolerance}
                   for index, wanted in enumerate(expected)]
    return {"samples": samples, "intervalsMs": intervals,
            "expectedIntervalsMs": list(expected), "toleranceMs": tolerance,
            "comparisons": comparisons,
            "passed": len(intervals) == len(expected) and
                      all(item["passed"] for item in comparisons)}


def factory_interval_evidence(timeline: list) -> dict:
    samples = []
    for event in timeline or []:
        try:
            index, at = int(event.get("index")), float(event.get("at"))
        except (TypeError, ValueError, AttributeError):
            continue
        if not samples or samples[-1]["index"] != index:
            samples.append({"index": index, "at": at})
    intervals = [round(samples[i + 1]["at"] - samples[i]["at"], 3)
                 for i in range(len(samples) - 1)]
    total = sum(intervals)
    normal = intervals[1:4] if len(intervals) == FACTORY_INTERVAL_COUNT else []
    holds = [intervals[0], intervals[4]] if len(intervals) == FACTORY_INTERVAL_COUNT else []
    checks = []
    assertion(checks, "six Factory states yield five intervals",
              len(intervals) == FACTORY_INTERVAL_COUNT,
              {"samples": samples, "intervals": intervals})
    assertion(checks, "Factory total is finite 6-8 seconds",
              FACTORY_TOTAL_RANGE_MS[0] <= total <= FACTORY_TOTAL_RANGE_MS[1],
              {"actualMs": total, "rangeMs": list(FACTORY_TOTAL_RANGE_MS)})
    assertion(checks, "Factory ordinary intervals are stable",
              len(normal) == 3 and max(normal) - min(normal) <= INTERVAL_TOLERANCE_MS,
              normal)
    assertion(checks, "Factory has two longer judgment/evaluation holds",
              len(holds) == 2 and len(normal) == 3 and
              min(holds) >= max(normal) + FACTORY_HOLD_MIN_DELTA_MS and
              max(holds) - min(holds) <= INTERVAL_TOLERANCE_MS,
              {"holdsMs": holds, "ordinaryMs": normal,
               "minimumDeltaMs": FACTORY_HOLD_MIN_DELTA_MS})
    return {"samples": samples, "intervalsMs": intervals,
            "totalMs": total, "checks": checks, "passed": all_passed(checks)}


def carrier_timeline(page: FS5Page, route: str) -> dict:
    if route == "home":
        selector, index_expr, phase_expr = (
            "[data-home-execution]", "el.dataset.homeStateIndex",
            "el.dataset.homeSequence")
        expected, timeout = HOME_INTERVALS_MS, sum(HOME_INTERVALS_MS) + 2500
        terminal = "phase==='complete'"
    elif route == "build":
        selector, index_expr, phase_expr = (
            "[data-build-factory-progress]",
            "[...document.querySelectorAll('[data-build-stage]')].findIndex(x=>x.classList.contains('build-stage--active'))",
            "el.dataset.buildPass")
        expected, timeout = None, FACTORY_TOTAL_RANGE_MS[1] + 2500
        terminal = "phase==='complete'"
    else:
        raise FS5Failure("no interval contract for %s" % route)
    script = r"""
      (() => new Promise(resolve => {
        const el=document.querySelector(%(selector)s);
        if(!el){resolve({error:'missing carrier',timeline:[]});return;}
        const timeline=[]; const started=performance.now(); let last='';
        const unitText=el=>{const values=[];const w=document.createTreeWalker(el,NodeFilter.SHOW_TEXT);let n;
          while((n=w.nextNode())){const v=n.nodeValue.replace(/\u00a0/g,' ').replace(/\s+/g,' ').trim();if(v)values.push(v);}return values.join('\n')};
        const record=()=>{const phase=%(phase)s;const index=%(index)s;
          const key=phase+'|'+index;if(key!==last){last=key;timeline.push({phase,index,at:performance.now()-started,
            copyStates:[...document.querySelectorAll('[data-copy-ref][data-copy-state]')].map(e=>({ref:e.getAttribute('data-copy-ref'),state:e.getAttribute('data-copy-state'),text:unitText(e)}))});}};
        const observer=new MutationObserver(record);
        observer.observe(el,{attributes:true,childList:true,characterData:true,subtree:true,attributeFilter:['data-home-state-index','data-home-sequence','data-build-pass','data-copy-state','class']});
        record(); el.scrollIntoView({block:'center'}); record();
        const poll=()=>{const phase=%(phase)s;if(%(terminal)s){observer.disconnect();record();resolve({timeline,terminal:phase,elapsedMs:performance.now()-started});return;}
          if(performance.now()-started>%(timeout)d){observer.disconnect();resolve({error:'carrier timeout',timeline,terminal:phase,elapsedMs:performance.now()-started});return;}
          setTimeout(poll,20);}; poll();
      }))()
    """ % {"selector": json.dumps(selector), "index": index_expr,
             "phase": phase_expr, "terminal": terminal, "timeout": timeout}
    raw = page.evaluate(script, await_promise=True)
    # Ignore the pre-trigger idle sample; interval zero begins at the first
    # running/resolved index and duplicate indices are collapsed by the helper.
    running = [event for event in raw.get("timeline", [])
               if event.get("phase") in ("running", "complete") and
               str(event.get("index")) not in ("", "None", "-1")]
    timing = (factory_interval_evidence(running) if route == "build"
              else interval_evidence(running, expected))
    timing.update(raw=raw, route=route)
    timing["passed"] = timing["passed"] and raw.get("terminal") == "complete" and not raw.get("error")
    return timing


def wait_browser_condition(page: FS5Page, expression: str, timeout_ms: int,
                           start_ms=None) -> dict:
    origin = "performance.now()" if start_ms is None else repr(float(start_ms))
    script = r"""(() => new Promise(resolve => {const start=%s;
      const poll=()=>{let value=false;try{value=!!(%s)}catch(e){}
        if(value){resolve({passed:true,elapsedMs:performance.now()-start});return;}
        if(performance.now()-start>%d){resolve({passed:false,elapsedMs:performance.now()-start});return;}
        setTimeout(poll,4);};poll();}))()""" % (origin, expression, timeout_ms)
    return page.evaluate(script, await_promise=True)


def flyout_timing(page: FS5Page, url: str) -> dict:
    page.navigate(url, 1440, 900)
    trigger = page.point("[data-flyout-trigger]")
    open_start = page.evaluate("performance.now()")
    page.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", **trigger},
                  session_id=page.session)
    opened = wait_browser_condition(page, "document.querySelector('[data-flyout]').open", 400, open_start)
    panel = page.point("[data-flyout]")
    page.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", **panel},
                  session_id=page.session)
    page.wait(FLYOUT_CLOSE_RANGE_MS[1] + 30)
    bridged = page.evaluate("document.querySelector('[data-flyout]').open")
    close_start = page.evaluate("performance.now()")
    page.cdp.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": 1, "y": 1},
                  session_id=page.session)
    closed = wait_browser_condition(page, "!document.querySelector('[data-flyout]').open", 500, close_start)
    checks = []
    assertion(checks, "Build flyout pointer-intent interval",
              opened["passed"] and FLYOUT_OPEN_RANGE_MS[0] <= opened["elapsedMs"] <= FLYOUT_OPEN_RANGE_MS[1],
              {"observed": opened, "expectedRangeMs": list(FLYOUT_OPEN_RANGE_MS)})
    assertion(checks, "Build flyout leave bridge remains open", bridged is True, bridged)
    assertion(checks, "Build flyout leave-grace interval",
              closed["passed"] and FLYOUT_CLOSE_RANGE_MS[0] <= closed["elapsedMs"] <= FLYOUT_CLOSE_RANGE_MS[1],
              {"observed": closed, "expectedRangeMs": list(FLYOUT_CLOSE_RANGE_MS)})
    return {"open": opened, "bridgeOpen": bridged, "close": closed,
            "assertions": checks, "passed": all_passed(checks)}


def fresh(cdp, base_url, snapshot, callback):
    page = FS5Page(cdp, base_url, snapshot)
    try:
        return callback(page)
    finally:
        page.close()


def run_interactions(cdp, base_url, snapshot, output, shots, axe_source,
                     copy_manifest):
    lanes = []
    state_observations = []
    def record(name, route, viewport, checks, detail, page=None):
        if page is not None:
            network = page.events()
            network_clean = not any(network[k] for k in
                ("unresolved", "orphanEvents", "failed", "httpErrors",
                 "remote", "console", "missingSnapshotHeaders"))
            assertion(checks, "interaction network/runtime clean",
                      network_clean, network)
            detail = dict(detail)
            detail["network"] = network
            png = page.screenshot(False)
            screenshot_record(output, shots, snapshot, "screenshots/interactions/%s.png" % name, png, route, name, viewport, "viewport")
        lanes.append({"lane": name, "route": route, "viewport": list(viewport), "assertions": checks, "detail": detail, "passed": all_passed(checks)})

    def desktop_pointer(page):
        facts = page.navigate(base_url + ROUTES[0][1], 1440, 900)
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "desktop-default"))
        checks=[]; started=time.monotonic(); page.mouse("[data-flyout-trigger]")
        page.wait(100); opened=page.evaluate("document.querySelector('[data-flyout]').open")
        elapsed=(time.monotonic()-started)*1000
        assertion(checks,"pointer intent opens flyout",opened and elapsed<=180,{"open":opened,"ms":elapsed})
        page.mouse("[data-flyout] a[data-preview-key='factory']")
        selected=page.evaluate("document.querySelector('[data-preview-state="+json.dumps("factory")+"]')!==null")
        assertion(checks,"pointer reaches destination",selected,selected)
        record("desktop-pointer","home",(1440,900),checks,{"axe":run_axe(page,axe_source),"facts":facts},page)
    fresh(cdp,base_url,snapshot,desktop_pointer)

    def desktop_keyboard(page):
        page.navigate(base_url + ROUTES[0][1],1440,900)
        checks=[]
        page.evaluate("document.querySelector('[data-flyout-trigger]').focus()")
        page.key("Enter","Enter",13,text="\r"); page.wait(80)
        opened=page.evaluate("document.querySelector('[data-flyout]').open")
        assertion(checks,"Enter opens Build",opened,opened)
        tabs=[]
        for _ in range(4):
            page.key("Tab","Tab",9); tabs.append(page.evaluate("document.activeElement&&document.activeElement.textContent.replace(/\\s+/g,' ').trim()"))
        assertion(checks,"four destinations keyboard reachable",len([x for x in tabs if x])==4,tabs)
        page.key("Escape","Escape",27); page.wait(50)
        state=page.evaluate("({open:document.querySelector('[data-flyout]').open,restored:document.activeElement===document.querySelector('[data-flyout-trigger]')})")
        assertion(checks,"Escape closes and restores focus",not state["open"] and state["restored"],state)
        record("desktop-keyboard","home",(1440,900),checks,{"tabs":tabs},page)
    fresh(cdp,base_url,snapshot,desktop_keyboard)

    for width,height in ((390,844),(768,1024)):
        def mobile(page,w=width,h=height):
            facts=page.navigate(base_url+ROUTES[0][1],w,h,touch=True); checks=[]
            state_observations.extend(observe_copy_states(page, copy_manifest,
                                                          "mobile-closed-%s" % w))
            caps=facts["inputCapabilities"]
            assertion(checks,"real touch capability",caps["touch"]>0 and caps["coarse"],caps)
            page.touch("[data-summary]"); page.wait(80)
            opened=page.evaluate("document.querySelector('[data-disclosure]').open")
            assertion(checks,"touch opens mobile sheet",opened,opened)
            state_observations.extend(observe_copy_states(page, copy_manifest,
                                                          "mobile-open-%s" % w))
            main_state=page.evaluate("({mainInert:document.querySelector('main').inert,footerInert:document.querySelector('footer').inert,locked:getComputedStyle(document.documentElement).overflow})")
            assertion(checks,"background inert and scroll locked",main_state["mainInert"] and main_state["footerInert"] and main_state["locked"] in ("hidden","clip"),main_state)
            page.touch("[data-flyout-trigger]"); page.wait(60)
            inner=page.evaluate("document.querySelector('[data-flyout]').open")
            assertion(checks,"touch opens inner Build",inner,inner)
            responsive_copy = live_copy_reconciliation(
                page, "home", copy_manifest,
                {"separate-responsive-menu-layer"})
            assertion(checks, "responsive menu exact applicable copy",
                      responsive_copy["passed"], responsive_copy)
            page.key("Escape","Escape",27); page.wait(50)
            layered=page.evaluate("({inner:document.querySelector('[data-flyout]').open,outer:document.querySelector('[data-disclosure]').open})")
            assertion(checks,"Escape closes inner layer first",not layered["inner"] and layered["outer"],layered)
            page.key("Escape","Escape",27); page.wait(50)
            restored=page.evaluate("({outer:document.querySelector('[data-disclosure]').open,focus:document.activeElement===document.querySelector('[data-summary]'),main:document.querySelector('main').inert,footer:document.querySelector('footer').inert})")
            assertion(checks,"second Escape closes sheet and restores focus",not restored["outer"] and restored["focus"] and not restored["main"] and not restored["footer"],restored)
            record("touch-%dx%d"%(w,h),"home",(w,h),checks,{"facts":facts,"axe":run_axe(page,axe_source),"applicableCopy":responsive_copy},page)
        fresh(cdp,base_url,snapshot,mobile)

    def home(page):
        page.navigate(base_url+ROUTES[0][1],1440,900); checks=[]
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "home-initial"))
        page.evaluate("document.querySelector('[data-home-execution]').scrollIntoView({block:'center'})"); page.wait(250)
        started=page.evaluate("document.querySelector('[data-home-execution]').getAttribute('data-home-sequence')")
        assertion(checks,"Home begins when visible",started=="running",started)
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "home-running"))
        page.mouse("[data-home-execution-states]"); before=page.evaluate("document.querySelector('[data-home-execution]').getAttribute('data-home-state-index')"); page.wait(1800); after=page.evaluate("document.querySelector('[data-home-execution]').getAttribute('data-home-state-index')")
        assertion(checks,"Home hover suspends",before==after,{"before":before,"after":after})
        page.cdp.call("Input.dispatchMouseEvent",{"type":"mouseMoved","x":1,"y":1},session_id=page.session); page.wait(1800)
        resumed=page.evaluate("document.querySelector('[data-home-execution]').getAttribute('data-home-state-index')")
        assertion(checks,"Home hover leave resumes",resumed!=after,{"before":after,"after":resumed})
        page.mouse("[data-home-pause]",click=True); paused=page.evaluate("({phase:document.querySelector('[data-home-execution]').dataset.homeSequence,status:document.querySelector('[data-home-execution-status]').textContent.trim(),index:document.querySelector('[data-home-execution]').dataset.homeStateIndex})"); page.wait(2400); held=page.evaluate("document.querySelector('[data-home-execution]').dataset.homeStateIndex")
        assertion(checks,"Home explicit Pause authoritative",paused["phase"]=="paused" and paused["status"]=="Operating change paused" and held==paused["index"],{"paused":paused,"held":held})
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "home-paused"))
        page.mouse("[data-home-pause]",click=True); running=page.evaluate("({phase:document.querySelector('[data-home-execution]').dataset.homeSequence,status:document.querySelector('[data-home-execution-status]').textContent.trim()})")
        assertion(checks,"Home explicit Resume",running=={"phase":"running","status":"Operating change in progress"},running)
        assertion(checks,"Home state list has no junk tab stop",page.evaluate("document.querySelectorAll('[data-home-execution-states] a,[data-home-execution-states] button,[data-home-execution-states] [tabindex]').length")==0,None)
        record("home-carrier","home",(1440,900),checks,{},page)
    fresh(cdp,base_url,snapshot,home)

    def transformation(page):
        page.navigate(base_url+dict((n,p) for n,p,_ in ROUTES)["transformation"],1440,900); checks=[]
        positions=page.evaluate("(()=>{const s=document.querySelector('[data-transformation-stage]');return {top:s.offsetTop,bottom:s.offsetTop+s.offsetHeight-innerHeight};})()")
        page.evaluate("scrollTo(0,%d)"%positions["bottom"]); page.wait(250); forward=page.evaluate("document.querySelector('input[name="+json.dumps("outcome")+"]:checked').value")
        page.evaluate("scrollTo(0,%d)"%positions["top"]); page.wait(250); reverse=page.evaluate("document.querySelector('input[name="+json.dumps("outcome")+"]:checked').value")
        assertion(checks,"Transformation advances",forward=="retire",forward)
        assertion(checks,"Transformation reverses",reverse=="preserve",reverse)
        record("transformation-carrier","transformation",(1440,900),checks,{"forward":forward,"reverse":reverse},page)
    fresh(cdp,base_url,snapshot,transformation)

    def workgraph(page):
        page.navigate(base_url+dict((n,p) for n,p,_ in ROUTES)["workgraph"],1440,900); checks=[]
        positions=page.evaluate("(()=>{const s=document.querySelector('[data-workgraph-section="+json.dumps("lifecycle")+"]');return {top:s.offsetTop,travel:Math.max(1,s.offsetHeight-innerHeight*.4)};})()")
        observed=[]
        for index, wanted in enumerate(("connect", "decide", "build", "learn")):
            page.evaluate("scrollTo(0,%s)" % (positions["top"] + positions["travel"] * index / 3))
            waited=wait_browser_condition(page,"document.querySelector('[data-workgraph-record-state]').dataset.workgraphActiveState===%s" % json.dumps(wanted),1500)
            actual=page.evaluate("document.querySelector('[data-workgraph-record-state]').dataset.workgraphActiveState")
            observed.append({"wanted":wanted,"actual":actual,"wait":waited})
            state_observations.extend(observe_copy_states(page,copy_manifest,
                                                          "workgraph-%s" % wanted))
        forward=observed[-1]["actual"]
        page.evaluate("scrollTo(0,%s)"%positions["top"]); page.wait(250); reverse=page.evaluate("document.querySelector('[data-workgraph-record-state]').dataset.workgraphActiveState")
        state_observations.extend(observe_copy_states(page,copy_manifest,
                                                      "workgraph-reverse"))
        assertion(checks,"WorkGraph advances",forward=="learn",forward); assertion(checks,"WorkGraph reverses",reverse=="connect",reverse)
        assertion(checks,"WorkGraph exposes every lifecycle state",
                  all(x["wait"]["passed"] and x["actual"]==x["wanted"] for x in observed),observed)
        record("workgraph-carrier","workgraph",(1440,900),checks,{"forward":forward,"reverse":reverse,"states":observed},page)
    fresh(cdp,base_url,snapshot,workgraph)

    def factory(page):
        page.navigate(base_url+dict((n,p) for n,p,_ in ROUTES)["build"],1440,900); checks=[]
        page.evaluate("document.querySelector('[data-build-factory-progress]').scrollIntoView({block:'center'})"); page.wait(250)
        page.mouse("[data-build-factory-stages]"); before=page.evaluate("document.querySelector('[data-build-stage].build-stage--active')?.dataset.buildStage"); page.wait(1100); held=page.evaluate("document.querySelector('[data-build-stage].build-stage--active')?.dataset.buildStage")
        assertion(checks,"Factory hover suspends",before==held,{"before":before,"after":held})
        page.cdp.call("Input.dispatchMouseEvent",{"type":"mouseMoved","x":1,"y":1},session_id=page.session); page.wait(1100)
        after=page.evaluate("document.querySelector('[data-build-stage].build-stage--active')?.dataset.buildStage")
        assertion(checks,"Factory resumes",after!=held,{"before":held,"after":after})
        page.mouse("[data-build-pause]",click=True); paused=page.evaluate("document.querySelector('[data-build-factory-progress]').dataset.buildPass"); page.wait(1100)
        assertion(checks,"Factory Pause",paused=="paused" and page.evaluate("document.querySelector('[data-build-factory-progress]').dataset.buildPass")=="paused",paused)
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "factory-paused"))
        page.mouse("[data-build-pause]",click=True); assertion(checks,"Factory Resume",page.evaluate("document.querySelector('[data-build-factory-progress]').dataset.buildPass")=="running",None)
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "factory-resumed"))
        page.mouse("[data-build-inspect]",click=True); page.wait(60); complete=page.evaluate("({pass:document.querySelector('[data-build-factory-progress]').dataset.buildPass,status:document.querySelector('[data-build-status]').textContent.trim(),replay:!document.querySelector('[data-build-replay]').hidden})")
        assertion(checks,"Factory Inspect resolves",complete["pass"]=="complete" and complete["status"]=="Governed review complete" and complete["replay"],complete)
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "factory-resolved"))
        page.mouse("[data-build-replay]",click=True); assertion(checks,"Factory Replay starts one pass",page.evaluate("document.querySelector('[data-build-factory-progress]').dataset.buildPass")=="running",None)
        record("factory-carrier","build",(1440,900),checks,{},page)
    fresh(cdp,base_url,snapshot,factory)

    for route, path, _ in ROUTES:
        def route_touch(page, n=route, p=path):
            result = touch_traverse_route(page, n, base_url + p,
                                          copy_manifest)
            state_observations.extend(result["copyStateObservations"])
            record("route-touch-controls-%s" % n, n, (390, 844),
                   result["assertions"], result, page)
        fresh(cdp, base_url, snapshot, route_touch)

    for route, path in (("home", ROUTES[0][1]),
                        ("build", dict((n, p) for n, p, _ in ROUTES)["build"])):
        def timing_lane(page, n=route, p=path):
            page.navigate(base_url + p, 1440, 900)
            evidence = carrier_timeline(page, n)
            state_observations.extend(timeline_copy_state_observations(
                evidence, copy_manifest, "%s-timeline" % n))
            state_observations.extend(observe_copy_states(page, copy_manifest,
                                                          "%s-complete" % n))
            checks = []
            assertion(checks, "%s interval-level timing" % n,
                      evidence["passed"], evidence)
            record("%s-interval-timing" % n, n, (1440, 900), checks,
                   evidence, page)
        fresh(cdp, base_url, snapshot, timing_lane)

    def flyout_timing_lane(page):
        evidence = flyout_timing(page, base_url + ROUTES[0][1])
        record("build-flyout-timing", "home", (1440, 900),
               evidence["assertions"], evidence, page)
    fresh(cdp, base_url, snapshot, flyout_timing_lane)

    required = ["desktop-pointer", "desktop-keyboard", "touch-390x844",
                "touch-768x1024", "home-carrier", "transformation-carrier",
                "workgraph-carrier", "factory-carrier",
                "home-interval-timing", "build-interval-timing",
                "build-flyout-timing"]
    required.extend("route-touch-controls-%s" % n for n, _, _ in ROUTES)
    return {"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,
            "requiredLanes":required,"lanes":lanes,
            "copyStateObservations":state_observations,
            "passed":set(required)=={x["lane"] for x in lanes} and
                     all(x["passed"] for x in lanes)}


def assessment_lane(cdp, base_url, snapshot, output, shots, axe_source,
                    copy_manifest):
    path=dict((n,p) for n,p,_ in ROUTES)["assessment"]
    def run(page):
        page.navigate(base_url+path,390,844); checks=[]; state_observations=[]
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "assessment-idle"))
        values = (("name", "FS5 Test", "validation-name", "Enter your name."),
                  ("email", "fs5@example.test", "validation-email", "Enter a valid work email."),
                  ("company", "Dagg FS5", "validation-company", "Enter your company."),
                  ("path", "Supplier exception", "validation-path", "Describe one workflow or operating path."),
                  ("why", "Material approval boundary", "validation-why", "Explain why the decision matters now."))
        validation = []
        for index, (name, value, state, message) in enumerate(values):
            page.mouse("[data-assessment-submit]", click=True); page.wait(30)
            observed = page.evaluate("({count:[...document.querySelectorAll('[data-assessment-form] [required]')].filter(e=>e.getAttribute('aria-invalid')==='true').length,focus:document.activeElement&&document.activeElement.name,button:document.querySelector('[data-assessment-submit]').textContent.trim(),buttonState:document.querySelector('[data-assessment-submit]').getAttribute('data-copy-state'),status:document.querySelector('[data-assessment-status]').textContent.trim(),statusState:document.querySelector('[data-assessment-status]').getAttribute('data-copy-state')})")
            observed.update({"expectedState": state, "expectedMessage": message})
            validation.append(observed)
            assertion(checks, "Assessment %s exact validation state" % state,
                      observed["count"] == 5 - index and
                      observed["focus"] == name and
                      observed["button"] == "Send the path for review" and
                      observed["buttonState"] == "idle" and
                      observed["status"] == message and
                      observed["statusState"] == state,
                      observed)
            state_observations.extend(observe_copy_states(
                page, copy_manifest, "assessment-%s" % state))
            page.evaluate("""(() => { const field=document.querySelector('[name=%s]');
              field.value=%s;field.dispatchEvent(new Event('input',{bubbles:true})); })()""" %
                          (json.dumps(name), json.dumps(value)))
        invalid = validation[0]
        page.evaluate(r"""(() => {
          const original=window.setTimeout.bind(window);
          window.__fs5AssessmentTimerCalls=[];
          window.setTimeout=(fn,ms,...args)=>{
            if(Number(ms)===450)window.__fs5AssessmentTimerCalls.push(ms);
            return original(fn,ms,...args);
          };
        })()""")
        page.mouse("[data-assessment-submit]",click=True); page.wait(30)
        checking=page.evaluate("({button:document.querySelector('[data-assessment-submit]').textContent.trim(),status:document.querySelector('[data-assessment-status]').textContent.trim(),buttonState:document.querySelector('[data-assessment-submit]').getAttribute('data-copy-state'),statusState:document.querySelector('[data-assessment-status]').getAttribute('data-copy-state'),disabled:document.querySelector('[data-assessment-submit]').disabled,timerCount:window.__fs5AssessmentTimerCalls.length})")
        assertion(checks,"truthful local checking status",checking=={
            "button":"Checking the path locally…","status":"Checking the path locally…",
            "buttonState":"submitting","statusState":"submitting",
            "disabled":False,"timerCount":1},checking)
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "assessment-submitting"))
        page.mouse("[data-assessment-submit]",click=True); page.wait(20)
        duplicate=page.evaluate("({button:document.querySelector('[data-assessment-submit]').textContent.trim(),status:document.querySelector('[data-assessment-status]').textContent.trim(),buttonState:document.querySelector('[data-assessment-submit]').getAttribute('data-copy-state'),statusState:document.querySelector('[data-assessment-status]').getAttribute('data-copy-state'),disabled:document.querySelector('[data-assessment-submit]').disabled,timerCount:window.__fs5AssessmentTimerCalls.length})")
        assertion(checks,"duplicate submit has exact non-transmitting state",
                  duplicate=={"button":"Path received. No need to send it again.",
                              "status":"Path received. No need to send it again.",
                              "buttonState":"duplicate","statusState":"duplicate",
                              "disabled":False,"timerCount":1},
                  duplicate)
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "assessment-duplicate"))
        page.wait(500); success=page.evaluate("({visible:!document.querySelector('[data-assessment-success]').hidden,focus:document.activeElement===document.querySelector('[data-assessment-success]'),text:document.querySelector('[data-assessment-success]').textContent.replace(/\\s+/g,' ').trim()})")
        assertion(checks,"truthful non-transmitting confirmation",success["visible"] and success["focus"] and "has not sent any data" in success["text"],success)
        network=page.events(); transmitting=[r for r in network["requests"] if r.get("method") not in (None,"GET")]
        assertion(checks,"zero transmitting requests",not transmitting,transmitting)
        png=page.screenshot(False); shot=screenshot_record(output,shots,snapshot,"screenshots/interactions/assessment-confirmation.png",png,"assessment","assessment",(390,844),"viewport")
        success_axe = run_axe(page, axe_source)
        assertion(checks, "axe passes Assessment confirmation state",
                  success_axe.get("passed") is True, success_axe)
        state_observations.extend(observe_copy_states(page, copy_manifest,
                                                      "assessment-confirmation"))
        applicable_copy = live_copy_reconciliation(
            page, "assessment", copy_manifest, {"local-preview-success"})
        assertion(checks, "Assessment success exact applicable copy",
                  applicable_copy["passed"], applicable_copy)
        return {"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,"assertions":checks,"validation":validation,"checking":checking,"duplicate":duplicate,"confirmation":success,"axeConfirmation":success_axe,"applicableCopy":applicable_copy,"copyStateObservations":state_observations,"network":network,"screenshot":shot,"passed":all_passed(checks)}
    return fresh(cdp,base_url,snapshot,run)


def resilience_lanes(cdp, base_url, snapshot, output, shots, copy_manifest):
    lanes=[]
    for name,path,_ in ROUTES:
        def zoom(page,n=name,p=path):
            facts=page.navigate(base_url+p,640,450,scale=2.0); net=page.events(); checks=[]
            assertion(checks,"verified 640x450 CSS viewport",round(facts["viewport"]["width"])==640 and round(facts["viewport"]["height"])==450 and facts["viewport"]["dpr"]==2,facts["viewport"])
            assertion(checks,"200 percent no overflow",facts["scroll"]["scrollWidth"]==facts["scroll"]["clientWidth"],facts["scroll"])
            assertion(checks,"200 percent network clean",not any(net[k] for k in ("unresolved","orphanEvents","failed","httpErrors","remote","console")),net)
            png=page.screenshot(False); shot=screenshot_record(output,shots,snapshot,"screenshots/resilience/%s-200-percent.png"%n,png,n,"200-percent",(640,450),"viewport")
            assertion(checks,"verified 1280x900 physical capture",
                      shot["pixelDimensions"] == {"width":1280,"height":900},
                      shot["pixelDimensions"])
            return {"lane":"200-percent","route":n,"assertions":checks,"measurement":facts,"network":net,"screenshot":shot,"passed":all_passed(checks)}
        lanes.append(fresh(cdp,base_url,snapshot,zoom))
        def reduced(page,n=name,p=path):
            facts=page.navigate(base_url+p,390,844,reduced=True); net=page.events(); checks=[]; rf=facts["routeFacts"]
            ok=True
            if n=="home": ok=rf["home"]["sequence"]=="complete" and rf["home"]["status"]=="Human decision recorded. Release remains withheld."
            elif n=="transformation": ok=rf["transformation"]["resolved"] and len(rf["transformation"]["outcomes"])==5 and all(o["visible"] for o in rf["transformation"]["outcomes"])
            elif n=="workgraph": ok=rf["workgraph"]["mode"]=="resolved" and rf["workgraph"]["active"]=="learn"
            elif n=="build": ok=rf["build"]["pass"]=="complete" and not rf["build"]["pauseVisible"] and not rf["build"]["replayVisible"]
            assertion(checks,"route resolved without timed control",ok,rf.get(n,rf))
            assertion(checks,"reduced-motion network/runtime clean",
                      not any(net[k] for k in ("unresolved","orphanEvents","failed","httpErrors","remote","console","missingSnapshotHeaders")),net)
            png=page.screenshot(False); shot=screenshot_record(output,shots,snapshot,"screenshots/resilience/%s-reduced.png"%n,png,n,"reduced-motion",(390,844),"viewport")
            return {"lane":"reduced-motion","route":n,"assertions":checks,"measurement":facts,"network":net,"screenshot":shot,"passed":all_passed(checks)}
        lanes.append(fresh(cdp,base_url,snapshot,reduced))
        def missing_observer(page,n=name,p=path):
            facts=page.navigate(base_url+p,390,844,preload="Object.defineProperty(window,'IntersectionObserver',{value:undefined,configurable:true});"); net=page.events(); checks=[]
            assertion(checks,"IntersectionObserver truly absent",page.evaluate("typeof IntersectionObserver==='undefined'") is True,None)
            if n=="home": assertion(checks,"Home resolves without observer",facts["routeFacts"]["home"]["sequence"]=="complete",facts["routeFacts"]["home"])
            if n=="workgraph": assertion(checks,"WorkGraph resolves without observer",facts["routeFacts"]["workgraph"]["mode"]=="resolved",facts["routeFacts"]["workgraph"])
            if n=="build": assertion(checks,"Build resolves without observer",facts["routeFacts"]["build"]["pass"]=="complete",facts["routeFacts"]["build"])
            if n not in ("home","workgraph","build"): assertion(checks,"route remains complete without observer",facts["structure"]["h1"]==1 and facts["scroll"]["scrollWidth"]==facts["scroll"]["clientWidth"],facts["structure"])
            assertion(checks,"missing-observer network/runtime clean",
                      not any(net[k] for k in ("unresolved","orphanEvents","failed","httpErrors","remote","console","missingSnapshotHeaders")),net)
            return {"lane":"missing-observer","route":n,"assertions":checks,"measurement":facts,"network":net,"passed":all_passed(checks)}
        lanes.append(fresh(cdp,base_url,snapshot,missing_observer))
        for label, token in (("missing-component-script",COMPONENT_SCRIPT),("missing-direction-script",ROUTE_SCRIPT[name])):
            def missing_script(page,n=name,p=path,l=label,t=token):
                pattern="*%s*"%t; facts=page.navigate(base_url+p,390,844,block=[pattern]); net=page.events(intentional_blocks=[t]); checks=[]
                blocked=[r for r in net["requests"] if r.get("intentionalBlock")]
                assertion(checks,"exact enhancement script blocked",len(blocked)==1,{"token":t,"blocked":blocked})
                assertion(checks,"no unrelated failure",not any(net[k] for k in ("unresolved","orphanEvents","failed","httpErrors","remote","console")),net)
                assertion(checks,"page complete and legible",facts["structure"]["h1"]==1 and facts["scroll"]["scrollWidth"]==facts["scroll"]["clientWidth"],facts["structure"])
                png=page.screenshot(False); shot=screenshot_record(output,shots,snapshot,"screenshots/resilience/%s-%s.png"%(n,l),png,n,l,(390,844),"viewport")
                return {"lane":l,"route":n,"assertions":checks,"measurement":facts,"network":net,"screenshot":shot,"passed":all_passed(checks)}
            lanes.append(fresh(cdp,base_url,snapshot,missing_script))
        def nojs(page,n=name,p=path):
            facts=page.navigate(base_url+p,390,844,script_disabled=True)
            facts["copy"]["computedAccessibleNames"] = enrich_computed_accessible_names(page,facts["copy"],copy_manifest)
            net=page.events(); checks=static_lane_assertions(n,facts,copy_manifest)
            assertion(checks,"true no-JS network clean",not any(net[k] for k in ("unresolved","orphanEvents","failed","httpErrors","remote","console")),net)
            png=page.screenshot(False); shot=screenshot_record(output,shots,snapshot,"screenshots/resilience/%s-no-js.png"%n,png,n,"true-no-js",(390,844),"viewport")
            return {"lane":"true-no-js","route":n,"assertions":checks,"measurement":facts,"network":net,"screenshot":shot,"passed":all_passed(checks)}
        lanes.append(fresh(cdp,base_url,snapshot,nojs))
    return {"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,"lanes":lanes,"expectedPerLane":{"200-percent":8,"reduced-motion":8,"missing-observer":8,"missing-component-script":8,"missing-direction-script":8,"true-no-js":8},"passed":all(x["passed"] for x in lanes)}


def served_disk_identity(base_url, snapshot, revision):
    accepted, attempts, rejected = serve_preview.acquire_consistent(REPO_ROOT)
    differences=[]; headers=[]
    if accepted.snapshot_id != snapshot:
        differences.append({"kind":"snapshot","served":snapshot,"disk":accepted.snapshot_id})
    for relative, disk in accepted.files.items():
        code, response_headers, served = p2.fetch(base_url,"/"+urllib.parse.quote(relative,safe="/"))
        lowered={k.lower():v for k,v in response_headers.items()}
        # The immutable server injects the three revision meta elements into
        # served HTML by contract.  Compare against that deterministic
        # transformation; all other candidate types must remain byte-for-byte
        # identical to disk.
        expected = (serve_preview.inject_revision_meta(disk, revision)
                    if relative.lower().endswith((".html", ".htm")) else disk)
        if code!=200 or served!=expected:
            differences.append({"kind":"bytes","path":relative,"status":code,
                                "diskOrExpectedSha256":sha256(expected),
                                "servedSha256":sha256(served)})
        if lowered.get(SNAPSHOT_HEADER)!=snapshot:
            headers.append({"path":relative,"actual":lowered.get(SNAPSHOT_HEADER)})
    return {"diskSnapshotId":accepted.snapshot_id,"servedSnapshotId":snapshot,"candidatePathCount":len(accepted.candidate_paths),"comparedFileCount":len(accepted.files),"skipped":list(accepted.skipped),"acquisitionAttempts":attempts,"rejectedPairs":rejected[:-1],"differingFiles":differences,"headerFailures":headers,"passed":not differences and not headers}


def decode_png_rgb(path: Path):
    """Decode the 8-bit, non-interlaced RGB/RGBA PNGs emitted by Chrome.

    A tiny decoder keeps the exact-pixel gate dependency-free.  Unsupported
    PNG modes are a hard failure instead of being silently color-converted.
    """
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        raise FS5Failure("not a PNG: %s" % path)
    offset = 8
    width = height = bit_depth = color_type = interlace = None
    compressed = bytearray()
    while offset < len(data):
        length = struct.unpack(">I", data[offset:offset + 4])[0]
        kind = data[offset + 4:offset + 8]
        body = data[offset + 8:offset + 8 + length]
        offset += 12 + length
        if kind == b"IHDR":
            width, height, bit_depth, color_type, _compression, _filter, interlace = struct.unpack(">IIBBBBB", body)
        elif kind == b"IDAT":
            compressed.extend(body)
        elif kind == b"IEND":
            break
    if bit_depth != 8 or color_type not in (2, 6) or interlace != 0:
        raise FS5Failure("unsupported PNG mode in %s: depth=%r type=%r interlace=%r"
                         % (path, bit_depth, color_type, interlace))
    channels = 3 if color_type == 2 else 4
    stride = width * channels
    raw = zlib.decompress(bytes(compressed))
    rows = []
    previous = bytearray(stride)
    pos = 0
    for _ in range(height):
        filter_type = raw[pos]
        source = raw[pos + 1:pos + 1 + stride]
        pos += stride + 1
        current = bytearray(stride)
        for i, value in enumerate(source):
            left = current[i - channels] if i >= channels else 0
            up = previous[i]
            upper_left = previous[i - channels] if i >= channels else 0
            if filter_type == 0:
                predictor = 0
            elif filter_type == 1:
                predictor = left
            elif filter_type == 2:
                predictor = up
            elif filter_type == 3:
                predictor = (left + up) // 2
            elif filter_type == 4:
                estimate = left + up - upper_left
                pa, pb, pc = abs(estimate - left), abs(estimate - up), abs(estimate - upper_left)
                predictor = left if pa <= pb and pa <= pc else (up if pb <= pc else upper_left)
            else:
                raise FS5Failure("unsupported PNG filter %r in %s" % (filter_type, path))
            current[i] = (value + predictor) & 255
        rows.append(bytes(current))
        previous = current
    return width, height, channels, rows


def protected_invariant_gate(matrix_rows, manifest_path=PROTECTED_INVARIANT):
    path = Path(manifest_path).resolve()
    result = {"path": path.relative_to(REPO_ROOT).as_posix()
              if path.is_relative_to(REPO_ROOT) else str(path), "passed": False}
    if not path.is_file():
        result["hardFailure"] = "protected invariant manifest missing"
        return result
    raw = path.read_bytes()
    try:
        doc = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        result["hardFailure"] = "invalid protected invariant manifest: %s" % exc
        return result
    checks = []
    assertion(checks, "protected schema", doc.get("schemaVersion") == 1,
              doc.get("schemaVersion"))
    assertion(checks, "frozen source snapshot",
              str(doc.get("sourceSnapshotId", "")).startswith("6ef754faf00f"),
              doc.get("sourceSnapshotId"))
    home = doc.get("homeHero") or {}
    assets = home.get("assets") or []
    asset_records = []
    for item in assets:
        asset = (REPO_ROOT / item.get("path", "")).resolve()
        record = {"path": item.get("path"), "exists": asset.is_file()}
        if asset.is_file():
            record["sha256"] = sha256(asset.read_bytes())
        record["passed"] = record.get("sha256") == item.get("sha256")
        asset_records.append(record)
    assertion(checks, "four selected Home assets are byte-identical",
              len(asset_records) == 4 and all(x["passed"] for x in asset_records),
              asset_records)
    copy_expected = home.get("copy") or {}
    home_rows = [r for r in matrix_rows if r.get("route") == "home"]
    copy_records, source_records = [], []
    for row in home_rows:
        actual = row.get("measurement", {}).get("protectedHome", {})
        copy_actual = {k: actual.get(k) for k in
                       ("eyebrow", "h1", "lead", "primaryAction", "secondaryAction")}
        copy_actual["alt"] = (actual.get("image") or {}).get("alt")
        copy_record = {"viewport": row.get("viewport"), "expected": copy_expected,
                       "actual": copy_actual,
                       "passed": copy_actual == copy_expected}
        copy_records.append(copy_record)
        width = row.get("viewport", [0])[0]
        token = "mobile-v4.webp" if width < 640 else "desktop-v4.webp"
        wanted = next((item for item in assets
                       if str(item.get("path", "")).endswith(token)), {})
        image = actual.get("image") or {}
        source_record = {"viewport": row.get("viewport"),
                         "expectedPath": wanted.get("path"),
                         "actualCurrentSrc": image.get("currentSrc"),
                         "expectedDimensions": [wanted.get("width"), wanted.get("height")],
                         "actualDimensions": [image.get("naturalWidth"), image.get("naturalHeight")]}
        source_record["passed"] = (str(image.get("currentSrc", "")).endswith(str(wanted.get("path", ""))) and
                                   source_record["actualDimensions"] == source_record["expectedDimensions"])
        source_records.append(source_record)
    assertion(checks, "Home hero copy and alt are invariant at all matrix sizes",
              len(copy_records) == len(VIEWPORTS) and all(x["passed"] for x in copy_records),
              copy_records)
    assertion(checks, "Home responsive source and intrinsic dimensions",
              len(source_records) == len(VIEWPORTS) and all(x["passed"] for x in source_records),
              source_records)
    rendered = home.get("renderedBaselines") or {}
    capture_records = []
    for item in rendered.get("captures") or []:
        capture = (REPO_ROOT / item.get("path", "")).resolve()
        capture_records.append({"path": item.get("path"), "exists": capture.is_file(),
                                "sha256": sha256(capture.read_bytes()) if capture.is_file() else None,
                                "expectedSha256": item.get("sha256")})
    baseline_manifest = (REPO_ROOT / rendered.get("manifest", "")).resolve()
    baseline_alignment = False
    if baseline_manifest.is_file():
        try:
            baseline_doc = json.loads(baseline_manifest.read_text(encoding="utf-8"))
            protected_by_view = {tuple(x.get("viewport", [])): x for x in
                                 rendered.get("captures", [])}
            baseline_by_view = {tuple(x.get("viewport", [])): x for x in
                                baseline_doc.get("captures", [])
                                if x.get("kind") == "viewport"}
            baseline_alignment = (set(protected_by_view) == set(baseline_by_view) and
                all(protected_by_view[v].get("sha256") == baseline_by_view[v].get("sha256") and
                    Path(protected_by_view[v].get("path", "")).name == baseline_by_view[v].get("path")
                    for v in protected_by_view))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            baseline_alignment = False
    assertion(checks, "protected lossless baselines and manifest exist and match",
              baseline_manifest.is_file() and len(capture_records) == 4 and
              all(x["sha256"] == x["expectedSha256"] for x in capture_records) and
              baseline_alignment,
              {"manifest": str(baseline_manifest), "captures": capture_records,
               "manifestAlignment": baseline_alignment})
    result.update(schemaVersion=1, sha256=sha256(raw), checks=checks,
                  assetRecords=asset_records, copyRecords=copy_records,
                  sourceRecords=source_records,
                  baselineDirectory=str(baseline_manifest.parent),
                  maximumDifferentPixelPercent=rendered.get("maximumDifferentPixelPercent"),
                  passed=all_passed(checks))
    return result


def reference_gate(output, matrix_rows, baseline_dir=None):
    refs={
        (1440,900):REPO_ROOT/"evidence/FULL-SITE-STAGING/FS4B/home-selected-hero-1440x900.png",
        (1024,768):REPO_ROOT/"evidence/FULL-SITE-STAGING/FS4B/snapshot-6ef754faf00f/tablet/home-first-1024x768.jpg",
        (390,844):REPO_ROOT/"evidence/FULL-SITE-STAGING/FS4B/snapshot-6ef754faf00f/mobile/home-first-390x844.jpg",
        (1536,1024):REPO_ROOT/"evidence/FULL-SITE-STAGING/FS4B/reference/home-founder-selected-1536x1024.png",
    }
    baseline_manifest = None
    baseline_hashes = {}
    if baseline_dir:
        baseline_dir = Path(baseline_dir).resolve()
        manifest_path = baseline_dir / "manifest.json"
        if not manifest_path.is_file():
            return {"passed": False, "records": [],
                    "hardFailure": "Home baseline manifest missing: %s" % manifest_path}
        baseline_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if (baseline_manifest.get("kind") != "fs4-home-lossless-baseline"
                or baseline_manifest.get("passed") is not True
                or not str(baseline_manifest.get("snapshotId", "")).startswith("6ef754faf00f")
                or baseline_manifest.get("expectedSnapshotPrefix") != "6ef754faf00f"):
            return {"passed": False, "records": [],
                    "hardFailure": "Home baseline manifest is not a passing FS4 baseline"}
        captures = baseline_manifest.get("captures", [])
        refs = {tuple(item["viewport"]): baseline_dir / item["path"]
                for item in captures if item.get("kind") == "viewport"}
        baseline_hashes = {tuple(item["viewport"]): item.get("sha256")
                           for item in captures
                           if item.get("kind") == "viewport"}
    records=[]
    for viewport,ref in refs.items():
        row=next((r for r in matrix_rows if r["route"]=="home" and tuple(r["viewport"])==viewport),None)
        if not row or not ref.exists():
            records.append({"viewport":list(viewport),"passed":False,"reason":"candidate or reference missing"}); continue
        if baseline_manifest and sha256(ref.read_bytes()) != baseline_hashes.get(viewport):
            records.append({"viewport":list(viewport),"passed":False,
                            "reason":"baseline PNG hash does not match manifest",
                            "reference":str(ref)}); continue
        if ref.suffix.lower() not in (".png",):
            records.append({"viewport":list(viewport),"passed":False,"reason":"lossy JPEG cannot prove <=0.5% exact pixel identity","reference":str(ref)}); continue
        candidate=output/row["screenshots"]["viewport"]["path"]
        try:
            aw,ah,ac,arows=decode_png_rgb(candidate)
            bw,bh,bc,brows=decode_png_rgb(ref)
        except Exception as err:
            records.append({"viewport":list(viewport),"passed":False,
                            "reason":"lossless PNG decode failed: %s"%err}); continue
        if (aw,ah)!=(bw,bh):
            records.append({"viewport":list(viewport),"passed":False,"reason":"dimension mismatch","candidate":[aw,ah],"reference":[bw,bh]}); continue
        hero_bottom=max(1,min(ah,int(round(row["measurement"]["hero"]["bottom"]))))
        changed=0
        for y in range(hero_bottom):
            arow,brow=arows[y],brows[y]
            for x in range(aw):
                if arow[x*ac:x*ac+3] != brow[x*bc:x*bc+3]:
                    changed += 1
        total=aw*hero_bottom; ratio=changed/total
        records.append({"viewport":list(viewport),"reference":str(ref),"heroBottom":hero_bottom,"differentPixels":changed,"totalPixels":total,"ratio":ratio,"threshold":0.005,"passed":ratio<=0.005})
    return {"passed":len(records)==4 and all(r["passed"] for r in records),
            "baselineSnapshotId": (baseline_manifest or {}).get("snapshotId"),
            "records":records}


def resolve_axe(value):
    candidates=[value,os.environ.get("DAGG_AXE_SCRIPT"),
                str(REPO_ROOT/"assets/vendor/axe-core/axe.min.js"),
                str(REPO_ROOT/"node_modules/axe-core/axe.min.js")]
    for candidate in candidates:
        if candidate and Path(candidate).is_file():
            path = Path(candidate).resolve()
            package = path.parent / "package.json"
            package_data = json.loads(package.read_text(encoding="utf-8")) if package.is_file() else {}
            data = path.read_bytes()
            return data.decode("utf-8"), {
                "path": str(path.relative_to(REPO_ROOT)) if REPO_ROOT in path.parents else str(path),
                "sha256": sha256(data), "bytes": len(data),
                "version": package_data.get("version"),
                "override": bool(value or os.environ.get("DAGG_AXE_SCRIPT")),
            }
    return None, {"path": None, "sha256": None, "version": None,
                  "override": bool(value or os.environ.get("DAGG_AXE_SCRIPT"))}


HOME_BASELINE_SOURCE_PATHS = (
    "/preview/golden-standard/home/index.html",
    "/preview/golden-standard/home/src/body.html",
    "/preview/golden-standard/home/src/direction.css",
    "/preview/golden-standard/home/src/direction.js",
    "/preview/golden-standard/shared/chrome/header.html",
    "/preview/golden-standard/shared/chrome/footer.html",
    "/preview/golden-standard/shared/chrome/chrome.css",
    "/preview/golden-standard/shared/chrome/chrome.js",
    "/preview/golden-standard/component-library/styles.css",
    "/preview/golden-standard/component-library/script.js",
    "/design/golden-standard/system/tokens.css",
)


def compare_served_resource(base_url: str, revision: dict, url_path: str):
    """Compare one frozen-server resource to its current source byte.

    HTML is compared to serve_preview's deterministic revision-meta
    transformation.  This deliberately limits the baseline gate to Home's
    actual dependency closure: documentation may change after FS4 without
    making the served Home reference stale, while any Home/shared/asset byte
    drift still rejects the baseline.
    """
    path = urllib.parse.unquote(urllib.parse.urlsplit(url_path).path)
    relative = path.lstrip("/")
    if path.endswith("/"):
        relative += "index.html"
    disk_path = (REPO_ROOT / relative).resolve()
    if disk_path != REPO_ROOT and REPO_ROOT not in disk_path.parents:
        return {"path": path, "passed": False, "reason": "path escapes repository"}
    if not disk_path.is_file():
        return {"path": path, "sourcePath": relative, "passed": False,
                "reason": "current source file missing"}
    code, headers, served = p2.fetch(base_url, path)
    lowered = {k.lower(): v for k, v in headers.items()}
    disk = disk_path.read_bytes()
    expected = (serve_preview.inject_revision_meta(disk, revision)
                if relative.lower().endswith((".html", ".htm")) else disk)
    return {
        "path": path, "sourcePath": relative, "status": code,
        "snapshotHeader": lowered.get(SNAPSHOT_HEADER),
        "servedSha256": sha256(served), "currentSourceSha256": sha256(disk),
        "expectedServedSha256": sha256(expected), "bytes": len(served),
        "passed": (code == 200 and served == expected
                   and lowered.get(SNAPSHOT_HEADER) == revision["snapshotId"]),
    }


def capture_home_baseline(args) -> int:
    """Capture lossless FS4 Home baselines from an existing immutable server.

    This mode never launches or restarts the preview server and never reads an
    assembled output for mutation.  It launches only a disposable Chrome
    target, writes only the requested evidence directory, and requires the
    existing server snapshot prefix supplied by the caller.
    """
    output = args.capture_home_baseline
    output = output if output.is_absolute() else REPO_ROOT / output
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = Path(tempfile.mkdtemp(prefix=".%s.tmp-" % output.name,
                                dir=str(output.parent)))
    profile = chrome = cdp = None
    snapshot = "unknown"
    try:
        base_url = args.baseline_base_url.rstrip("/")
        status, headers, body = p2.fetch(base_url, "/__revision")
        if status != 200:
            raise FS5Failure("baseline /__revision returned %s" % status)
        revision = json.loads(body)
        snapshot = revision["snapshotId"]
        lowered = {k.lower(): v for k, v in headers.items()}
        if lowered.get(SNAPSHOT_HEADER) != snapshot:
            raise FS5Failure("baseline revision response has a mixed snapshot header")
        if not snapshot.startswith(args.expected_baseline_snapshot):
            raise FS5Failure("baseline server snapshot %s does not match required FS4 prefix %s"
                             % (snapshot, args.expected_baseline_snapshot))
        if (revision.get("snapshotAcquisitionStable") is not True
                or revision.get("snapshotConsistencyPasses") != 2):
            raise FS5Failure("baseline server does not report a stable two-pass acquisition")

        profile = Path(tempfile.mkdtemp(prefix="dagg-fs4-home-baseline-chrome-"))
        chrome, browser_ws, chrome_path, chrome_launch = start_fs5_chrome(
            profile, temp / "chrome-startup-failure.json")
        cdp = p2.CDP(browser_ws)
        captures = []
        requested_resources = set(HOME_BASELINE_SOURCE_PATHS)
        for width, height in ((390, 844), (1024, 768), (1440, 900), (1536, 1024)):
            page = FS5Page(cdp, base_url, snapshot)
            try:
                facts = page.navigate(base_url + "/preview/golden-standard/home/",
                                      width, height)
                network = page.events()
                if facts.get("snapshot") != snapshot:
                    raise FS5Failure("Home %dx%d page meta has mixed snapshot %r"
                                     % (width, height, facts.get("snapshot")))
                if facts.get("visibility") != "visible":
                    raise FS5Failure("Home %dx%d target is not visible" % (width, height))
                if (round(facts["viewport"]["width"]),
                        round(facts["viewport"]["height"])) != (width, height):
                    raise FS5Failure("Home baseline CSS viewport mismatch at %dx%d"
                                     % (width, height))
                bad = {key: network[key] for key in
                       ("unresolved", "orphanEvents", "failed", "httpErrors",
                        "remote", "console", "missingSnapshotHeaders")
                       if network[key]}
                if bad:
                    raise FS5Failure("Home baseline network/runtime failure: %s"
                                     % json.dumps(bad)[:1000])
                for request in network["requests"]:
                    request_url = request.get("responseUrl") or request.get("url")
                    parsed = urllib.parse.urlsplit(request_url or "")
                    if parsed.netloc == urllib.parse.urlsplit(base_url).netloc:
                        requested_resources.add(parsed.path)
                relative = "home-%dx%d.png" % (width, height)
                data = page.screenshot(False)
                path = temp / relative
                path.write_bytes(data)
                captures.append({"path": relative, "kind": "viewport",
                                 "viewport": [width, height],
                                 "pixelDimensions": p2.png_size(data),
                                 "sha256": sha256(data), "bytes": len(data),
                                 "snapshotId": snapshot,
                                 "heroRect": facts.get("hero")})
            finally:
                page.close()

        resources = [compare_served_resource(base_url, revision, path)
                     for path in sorted(requested_resources)]
        resource_failures = [item for item in resources if not item["passed"]]
        if resource_failures:
            raise FS5Failure("baseline source/served identity failed: %s"
                             % json.dumps(resource_failures)[:1200])
        manifest = {
            "schemaVersion": SCHEMA_VERSION,
            "kind": "fs4-home-lossless-baseline",
            "snapshotId": snapshot,
            "expectedSnapshotPrefix": args.expected_baseline_snapshot,
            "capturedAt": dt.datetime.now(dt.timezone.utc).isoformat(),
            "serverBaseUrl": base_url,
            "serverRevision": revision,
            "chromePath": chrome_path,
            "chromeLaunch": chrome_launch,
            "chromeVersion": cdp.call("Browser.getVersion"),
            "captures": captures,
            "resources": resources,
            "sourceServedComparedCount": len(resources),
            "sourceServedFailures": resource_failures,
            "passed": len(captures) == 4 and not resource_failures,
        }
        json_write(temp / "manifest.json", manifest)
        if output.exists():
            raise FS5Failure("refusing to replace existing Home baseline: %s" % output)
        os.replace(temp, output)
        print("FS4 Home lossless baseline %s -> %s" % (snapshot, output))
        return 0
    except Exception as err:
        try:
            json_write(temp / "failure.json", {
                "schemaVersion": SCHEMA_VERSION, "snapshotId": snapshot,
                "passed": False, "error": "%s: %s" % (type(err).__name__, err)})
            failed = output.parent / (".failed-home-baseline-%s-%s"
                                      % (str(snapshot)[:12], utc_stamp()))
            if failed.exists():
                failed = output.parent / (failed.name + "-%d" % os.getpid())
            os.replace(temp, failed)
            print("Home baseline REJECT; preserved at %s: %s" % (failed, err),
                  file=sys.stderr)
        except Exception as preserve:
            print("Home baseline REJECT; preservation failed: %s (original: %s)"
                  % (preserve, err), file=sys.stderr)
        return 1
    finally:
        if cdp:
            try:
                cdp.close()
            except Exception:
                pass
        if chrome:
            chrome.terminate()
            try:
                chrome.wait(timeout=10)
            except Exception:
                chrome.kill()
        if profile:
            shutil.rmtree(profile, ignore_errors=True)


def finalize_package(root: Path, revision: dict):
    # revision.json is the final seal: all other required artifacts must
    # already exist before it is written and binds their hashes.
    missing=[name for name in REQUIRED_OUTPUTS
             if name != "revision.json" and not (root/name).is_file()]
    if missing:
        raise FS5Failure("required outputs missing: %s"%", ".join(missing))
    hashes={name:sha256((root/name).read_bytes()) for name in REQUIRED_OUTPUTS if name!="revision.json"}
    revision=dict(revision); revision.update(schemaVersion=SCHEMA_VERSION,artifactSha256=hashes,requiredOutputs=list(REQUIRED_OUTPUTS))
    json_write(root/"revision.json",revision)
    for name,digest in hashes.items():
        if sha256((root/name).read_bytes())!=digest:
            raise FS5Failure("artifact changed during finalization: %s"%name)


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output",type=Path,default=DEFAULT_OUTPUT)
    parser.add_argument("--port",type=int,default=0)
    parser.add_argument("--host",default="127.0.0.1")
    parser.add_argument("--axe-script",default=None)
    parser.add_argument("--copy-manifest", type=Path, default=DEFAULT_COPY_MANIFEST,
                        help="exact keyed copy authority inside the candidate")
    parser.add_argument("--visual-review", type=Path,
                        help="external caption-free/grayscale review JSON bound to captured hashes")
    parser.add_argument("--home-baseline", type=Path,
                        default=os.environ.get("DAGG_FS5_HOME_BASELINE"),
                        help="passing lossless FS4 Home baseline directory")
    parser.add_argument("--capture-home-baseline", type=Path,
                        help="baseline-only output; connects to an existing immutable server")
    parser.add_argument("--baseline-base-url", default="http://127.0.0.1:8933")
    parser.add_argument("--expected-baseline-snapshot", default="6ef754faf00f")
    args=parser.parse_args(argv)
    if args.capture_home_baseline:
        return capture_home_baseline(args)
    output=args.output if args.output.is_absolute() else REPO_ROOT/args.output
    output=output.resolve(); output.parent.mkdir(parents=True,exist_ok=True)
    temp=Path(tempfile.mkdtemp(prefix=".%s.tmp-"%output.name,dir=str(output.parent)))
    snapshot="unknown"; server=chrome=cdp=None; profile=None
    hard=[]; rows=[]; shots=[]
    started=time.monotonic(); base_url=None
    try:
        copy_manifest, copy_meta = load_copy_manifest(args.copy_manifest)
        server,base_url,startup=p2.start_server(args.port,args.host)
        status,headers,body=p2.fetch(base_url,"/__revision")
        if status!=200: raise FS5Failure("/__revision returned %s"%status)
        revision=json.loads(body); snapshot=revision["snapshotId"]
        if snapshot.startswith("6ef754faf00f"):
            raise FS5Failure("FS4 snapshot 6ef754faf00f is forbidden as FS5 evidence")
        if {k.lower():v for k,v in headers.items()}.get(SNAPSHOT_HEADER)!=snapshot: raise FS5Failure("revision response lacks matching snapshot header")
        profile=Path(tempfile.mkdtemp(prefix="dagg-fs5-chrome-"))
        chrome,browser_ws,chrome_path,chrome_launch=start_fs5_chrome(
            profile,temp/"chrome-startup-failure.json")
        cdp=p2.CDP(browser_ws)
        axe_source,axe_meta=resolve_axe(args.axe_script)
        environment={"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,"baseUrl":base_url,"serverStartupSeconds":startup,"chromePath":chrome_path,"chromeLaunch":chrome_launch,"chromeVersion":cdp.call("Browser.getVersion"),"axeCore":axe_meta,"copyAuthority":copy_meta,"capturedAt":dt.datetime.now(dt.timezone.utc).isoformat(),"matrixRows":EXPECTED_MATRIX_ROWS}
        performance=[]; network_rows=[]
        for route,path,_public in ROUTES:
            for width,height in VIEWPORTS:
                def capture(page,n=route,p=path,w=width,h=height):
                    facts=page.navigate(base_url+p,w,h)
                    facts["copy"]["computedAccessibleNames"] = enrich_computed_accessible_names(page,facts["copy"],copy_manifest)
                    network=page.events(); checks=matrix_assertions(n,(w,h),facts,network,snapshot,copy_manifest)
                    stem="screenshots/matrix/%s-%dx%d"%(n,w,h)
                    viewport_shot=screenshot_record(temp,shots,snapshot,stem+"-viewport.png",page.screenshot(False),n,"base-matrix",(w,h),"viewport")
                    full_shot=screenshot_record(temp,shots,snapshot,stem+"-full.png",page.screenshot(True),n,"base-matrix",(w,h),"full-page-documentation")
                    row={"id":"%s-%dx%d"%(n,w,h),"lane":"base-matrix","route":n,"path":p,"viewport":[w,h],"snapshotId":snapshot,"assertions":checks,"measurement":facts,"network":network,"screenshots":{"viewport":viewport_shot,"fullPage":full_shot},"passed":all_passed(checks)}
                    if w in PERFORMANCE_WIDTHS:
                        resource_bytes=sum((x.get("encodedDataLength") or 0) for x in network["requests"])
                        hero=next((i for i in facts["images"] if i["rendered"]["width"]>facts["viewport"]["width"]*.3),None)
                        hero_bytes=0
                        if hero:
                            hero_bytes=sum((x.get("encodedDataLength") or 0) for x in network["requests"] if (x.get("responseUrl") or x.get("url"))==hero["currentSrc"])
                        performance.append({"route":n,"viewport":[w,h],"snapshotId":snapshot,"transferBytes":resource_bytes,"heroTransferBytes":hero_bytes,"heroBudgetBytes":300000 if w==390 else 500000,"heroWithinBudget":hero is None or hero_bytes<= (300000 if w==390 else 500000),"images":facts["images"],"lcpMs":facts["performance"].get("lcp"),"cls":facts["performance"].get("cls"),"navigation":facts["performance"].get("navigation"),"passed":facts["performance"].get("lcp") is not None and facts["performance"].get("cls") is not None and (hero is None or hero_bytes>0) and (hero is None or hero_bytes<= (300000 if w==390 else 500000))})
                    network_rows.append({"rowId":row["id"],"passed":not any(network[k] for k in ("unresolved","orphanEvents","failed","httpErrors","remote","console","missingSnapshotHeaders")),"network":network})
                    return row
                rows.append(fresh(cdp,base_url,snapshot,capture))
        matrix={"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,"expectedRows":EXPECTED_MATRIX_ROWS,"routes":[n for n,_,_ in ROUTES],"viewports":[list(v) for v in VIEWPORTS],"rows":rows,"passed":len(rows)==EXPECTED_MATRIX_ROWS and all(r["passed"] for r in rows)}
        json_write(temp/"route-matrix.json",matrix)
        source_rows=[r for r in rows if r["viewport"]==[1440,900]]
        anchors=audit_links(base_url,snapshot,source_rows); json_write(temp/"anchors.json",anchors)
        interactions=run_interactions(cdp,base_url,snapshot,temp,shots,axe_source,copy_manifest)
        assessment=assessment_lane(cdp,base_url,snapshot,temp,shots,axe_source,copy_manifest); json_write(temp/"assessment.json",assessment)
        state_coverage=copy_state_coverage(copy_manifest,
            interactions.get("copyStateObservations", []) +
            assessment.get("copyStateObservations", []))
        interactions["copyStateCoverage"]=state_coverage
        interactions["passed"]=interactions["passed"] and state_coverage["passed"]
        json_write(temp/"interactions.json",interactions)
        resilience=resilience_lanes(cdp,base_url,snapshot,temp,shots,copy_manifest)
        axe_states=axe_state_lanes(cdp,base_url,snapshot,axe_source)
        resilience["axeStateCoverage"]=axe_states
        resilience["passed"]=resilience["passed"] and axe_states["passed"]
        if not axe_source: hard.append("axe-core is unavailable; accessibility critical/serious gate cannot run")
        json_write(temp/"resilience.json",resilience)
        perf={"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,"expectedRows":16,"rows":performance,"passed":len(performance)==16 and all(r["passed"] for r in performance)}; json_write(temp/"performance.json",perf)
        identity=served_disk_identity(base_url,snapshot,revision)
        protected=protected_invariant_gate(rows)
        baseline_dir=args.home_baseline or protected.get("baselineDirectory")
        reference=reference_gate(temp,rows,baseline_dir)
        visual_meta=visual_pair_metadata(shots,snapshot)
        visual_review=external_visual_review(args.visual_review,visual_meta)
        environment["servedDiskIdentity"]=identity; environment["protectedInvariantGate"]=protected
        environment["homeReferenceGate"]=reference
        environment["externalVisualReview"]=visual_review
        environment["passed"]=identity["passed"] and protected["passed"] and reference["passed"] and visual_meta["complete"] and visual_review["passed"]
        if not protected["passed"]: hard.append("FS5 protected Home invariant manifest failed")
        if not reference["passed"]: hard.append("Home <=0.5% reference gate unavailable or failed")
        if not visual_meta["complete"]: hard.append("canonical visual pair screenshot set is incomplete")
        if not visual_review["passed"]: hard.append(visual_review.get("hardFailure") or "external visual pair review failed")
        json_write(temp/"environment.json",environment)
        json_write(temp/"screenshots-manifest.json",{"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,"count":len(shots),"screenshots":shots,"visualPairReview":visual_meta,"passed":visual_meta["complete"] and all((temp/s["path"]).is_file() and sha256((temp/s["path"]).read_bytes())==s["sha256"] for s in shots)})
        failed_rows=[{"rowId":r["id"],"assertions":[a for a in r["assertions"] if not a["passed"]]} for r in rows if not r["passed"]]
        failures={"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,"hardFailures":hard,"matrixFailures":failed_rows,"networkRows":network_rows,"componentFailures":{"matrix":not matrix["passed"],"anchors":not anchors["passed"],"interactions":not interactions["passed"],"resilience":not resilience["passed"],"assessment":not assessment["passed"],"performance":not perf["passed"],"environment":not environment["passed"]}}
        failures["passed"]=not hard and not failed_rows and not any(failures["componentFailures"].values()) and all(r["passed"] for r in network_rows)
        json_write(temp/"failures.json",failures)
        status_word="PASS" if failures["passed"] else "REJECT"
        report="# FS5 immutable acceptance\n\n**%s**\n\nSnapshot: `%s`\n\nBase matrix: %d/%d passing. Screenshots: %d. Hard failures: %d.\n"%(status_word,snapshot,sum(r["passed"] for r in rows),EXPECTED_MATRIX_ROWS,len(shots),len(hard))
        if hard: report+="\n## Hard failures\n\n"+"\n".join("- "+x for x in hard)+"\n"
        (temp/"report.md").write_text(report,encoding="utf-8")
        (temp/"tests-output.txt").write_text("FS5 runner structural validation: %s\nSnapshot: %s\nRows: %d\n"%(status_word,snapshot,len(rows)),encoding="utf-8")
        revision_record=dict(revision); revision_record["servedDiskIdentity"]=identity; revision_record["runSeconds"]=round(time.monotonic()-started,3)
        finalize_package(temp,revision_record)
        if not failures["passed"]: raise FS5Failure("FS5 gates rejected the candidate; inspect failures.json")
        if output.exists(): raise FS5Failure("refusing to replace existing package: %s"%output)
        os.replace(temp,output)
        print("FS5 PASS %s -> %s"%(snapshot,output)); return 0
    except Exception as err:
        try:
            if not (temp/"failures.json").exists(): json_write(temp/"failures.json",{"schemaVersion":SCHEMA_VERSION,"snapshotId":snapshot,"passed":False,"hardFailures":["%s: %s"%(type(err).__name__,err)]})
            if not (temp/"report.md").exists(): (temp/"report.md").write_text("# FS5 immutable acceptance\n\n**REJECT**\n\n%s: %s\n"%(type(err).__name__,err),encoding="utf-8")
            failed=output.parent/(".failed-%s-%s"%(str(snapshot)[:12],utc_stamp()))
            if failed.exists(): failed=output.parent/(failed.name+"-%d"%os.getpid())
            os.replace(temp,failed); print("FS5 REJECT; partial evidence preserved at %s: %s"%(failed,err),file=sys.stderr)
        except Exception as preserve:
            print("FS5 REJECT and could not preserve %s: %s (original: %s)"%(temp,preserve,err),file=sys.stderr)
        return 1
    finally:
        if cdp:
            try: cdp.close()
            except Exception: pass
        if chrome:
            chrome.terminate()
            try: chrome.wait(timeout=10)
            except Exception: chrome.kill()
        if profile: shutil.rmtree(profile,ignore_errors=True)
        if server: p2.stop_server(server)


if __name__ == "__main__":
    raise SystemExit(main())
