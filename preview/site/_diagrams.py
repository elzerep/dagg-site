# Stylized illustration, not engineering schematic. The measured rules:
# a tinted panel with a radius so the drawing never touches the page ground,
# filled pills rather than outlines, dashed rounded groupings, a speech
# bubble for the annotation, mono labels, and exactly two accent hues.

WORKGRAPH = '''<svg class="dg ill" viewBox="0 0 940 400" role="img"
     aria-label="A generic record of how work moves: three inputs pass through people and systems, wait, reach a decision that gets made again, and loop back.">
  <defs>
    <marker id="wa" viewBox="0 0 8 8" refX="7.2" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 1.2 L7.2 4 L0 6.8z" fill="#8A8578"/></marker>
    <marker id="wc" viewBox="0 0 8 8" refX="7.2" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 1.2 L7.2 4 L0 6.8z" fill="#B85C3E"/></marker>
  </defs>

  <rect class="panel" x="0" y="0" width="940" height="400" rx="16"/>

  <g class="grp">
    <rect x="176" y="72" width="196" height="266" rx="12"/>
    <text class="grp-t" x="274" y="60" text-anchor="middle">WHERE THE WORK HAPPENS</text>
  </g>

  <g class="edges" fill="none" marker-end="url(#wa)">
    <path class="edge" d="M148 118 L172 118"/>
    <path class="edge" d="M148 205 L172 205"/>
    <path class="edge" d="M148 292 L172 292"/>
    <path class="edge" d="M376 118 L410 118 Q436 118 436 168 L436 186"/>
    <path class="edge" d="M376 292 L410 292 Q436 292 436 242 L436 224"/>
    <path class="edge" d="M376 205 L436 205"/>
    <path class="edge" d="M576 205 L636 205"/>
  </g>
  <g fill="none" marker-end="url(#wc)"><path class="edge hot" d="M516 205 L544 205"/></g>
  <g fill="none"><path class="edge loop" d="M756 178 Q620 84 300 96 L232 104"/></g>

  <g class="pill in">
    <rect class="node" x="44" y="102" width="104" height="32" rx="8"/>
    <rect class="node" x="44" y="189" width="104" height="32" rx="8"/>
    <rect class="node" x="44" y="276" width="104" height="32" rx="8"/>
  </g>
  <g class="pill mid">
    <rect class="node" x="196" y="98" width="156" height="40" rx="10"/>
    <rect class="node" x="196" y="185" width="156" height="40" rx="10"/>
    <rect class="node" x="196" y="272" width="156" height="40" rx="10"/>
  </g>
  <g class="pill wait"><rect class="node" x="436" y="182" width="80" height="46" rx="10"/></g>
  <g class="pill out">
    <rect class="node" x="636" y="178" width="168" height="54" rx="10"/>
    <rect class="node" x="672" y="300" width="180" height="38" rx="10"/>
  </g>

  <g class="lbl">
    <text class="lab" x="96"  y="122" text-anchor="middle">REQUEST</text>
    <text class="lab" x="96"  y="209" text-anchor="middle">DOCUMENT</text>
    <text class="lab" x="96"  y="296" text-anchor="middle">APPROVAL</text>
    <text class="lab" x="274" y="122" text-anchor="middle">A PERSON</text>
    <text class="lab" x="274" y="209" text-anchor="middle">A SYSTEM</text>
    <text class="lab" x="274" y="296" text-anchor="middle">A HANDOFF</text>
    <text class="lab strong" x="720" y="200" text-anchor="middle">DECISION</text>
    <text class="lab" x="720" y="217" text-anchor="middle">MADE AGAIN</text>
    <text class="lab" x="762" y="323" text-anchor="middle">DOWNSTREAM</text>
    <text class="lab on-dark" x="476" y="210" text-anchor="middle">WAIT</text>
  </g>

  <g class="note">
    <path class="bubble" d="M556 88 h196 a10 10 0 0 1 10 10 v42 a10 10 0 0 1 -10 10 h-118 l-14 16 v-16 h-64 a10 10 0 0 1 -10 -10 v-42 a10 10 0 0 1 10 -10 z"/>
    <text class="nt" x="574" y="112">The expensive step is rarely</text>
    <text class="nt" x="574" y="130">the slow one.</text>
  </g>

  <g class="tag">
    <text class="lab acc" x="440" y="168">queue time</text>
    <text class="lab acc" x="300" y="72">rework loop</text>
  </g>
</svg>'''

AGENT = '''<svg class="dg ill" viewBox="0 0 700 340" role="img"
     aria-label="An agent inside a boundary, with an escalation path to a person and a record written on every action.">
  <defs>
    <marker id="aa" viewBox="0 0 8 8" refX="7.2" refY="4" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0 1.2 L7.2 4 L0 6.8z" fill="#8A8578"/></marker>
  </defs>
  <rect class="panel" x="0" y="0" width="700" height="340" rx="16"/>

  <g class="grp">
    <rect x="40" y="66" width="380" height="212" rx="12"/>
    <text class="grp-t" x="230" y="54" text-anchor="middle">BOUNDS &#183; WHAT IT MAY TOUCH</text>
  </g>

  <g class="edges" fill="none" marker-end="url(#aa)">
    <path class="edge" d="M196 116 L252 134"/>
    <path class="edge" d="M196 214 L252 196"/>
  </g>
  <g fill="none"><path class="edge esc" d="M368 150 Q446 150 446 96 L494 96"/></g>
  <g fill="none"><path class="edge rec" d="M310 216 L310 288 L494 288"/></g>

  <g class="pill mid">
    <rect class="node" x="72" y="98" width="124" height="38" rx="10"/>
    <rect class="node" x="72" y="196" width="124" height="38" rx="10"/>
  </g>
  <g class="pill wait"><rect class="node" x="252" y="146" width="116" height="48" rx="10"/></g>
  <g class="pill out">
    <rect class="node" x="494" y="76" width="150" height="40" rx="10"/>
    <rect class="node" x="494" y="268" width="150" height="40" rx="10"/>
  </g>

  <g class="lbl">
    <text class="lab" x="134" y="121" text-anchor="middle">A SYSTEM</text>
    <text class="lab" x="134" y="219" text-anchor="middle">A SYSTEM</text>
    <text class="lab on-dark" x="310" y="175" text-anchor="middle">AGENT</text>
    <text class="lab strong" x="569" y="101" text-anchor="middle">A PERSON</text>
    <text class="lab strong" x="569" y="293" text-anchor="middle">THE RECORD</text>
  </g>
  <g class="tag"><text class="lab acc" x="392" y="128">escalates</text>
    <text class="lab sec" x="322" y="262">every action, including the ones that work</text></g>
</svg>'''

CSS = '''
/* ── diagrams as stylized illustration, never as schematic ─────────
   A tinted panel so the drawing never sits on the page ground, filled
   pills instead of outlines, dashed groupings, one speech bubble, and
   two accent hues — a drawing for a reader, not a wiring diagram. */
.ill{width:100%;height:auto;overflow:visible}
.ill .panel{fill:var(--warm);stroke:rgba(20,20,19,.06)}
body[data-ground="ivory"] .ill .panel{fill:#EAE7DD}

.ill .grp rect{fill:rgba(47,97,65,.045);stroke:rgba(47,97,65,.34);stroke-width:1;
  stroke-dasharray:5 5}
.ill .grp-t{font-family:var(--mono);font-size:9.5px;letter-spacing:.14em;fill:#4C6B57}

.ill .node{fill:var(--lift);stroke:rgba(20,20,19,.16);stroke-width:1}
.ill .pill.in .node{fill:rgba(20,20,19,.045);stroke:rgba(20,20,19,.13)}
.ill .pill.wait .node{fill:#141413;stroke:var(--accent);stroke-width:1.4}
.ill .pill.out .node{fill:var(--lift);stroke:rgba(20,20,19,.22)}

.ill .edge{stroke:rgba(20,20,19,.24);stroke-width:1.2;stroke-linecap:round}
.ill .edge.hot{stroke:var(--accent);stroke-width:1.8}
.ill .edge.loop{stroke:var(--accent);stroke-opacity:.42;stroke-width:1.2;stroke-dasharray:4 5}
.ill .edge.esc{stroke:var(--accent);stroke-width:1.4;stroke-dasharray:5 4}
.ill .edge.rec{stroke:rgba(47,97,65,.5);stroke-width:1.2;stroke-dasharray:2 5}

.ill .lab{font-family:var(--mono);font-size:10px;letter-spacing:.11em;fill:#5F5E58}
.ill .lab.strong{fill:var(--ink)}
.ill .lab.on-dark{fill:#F0EEE6}
.ill .lab.acc{fill:var(--accent-text);font-size:9.5px;letter-spacing:.09em}
.ill .lab.sec{fill:#4C6B57;font-size:9.5px;letter-spacing:.09em}

.ill .bubble{fill:var(--lift);stroke:var(--accent);stroke-opacity:.5;stroke-width:1}
.ill .nt{font-family:var(--serif);font-size:14px;fill:var(--ink-2)}
.ill .note{opacity:0;transition:opacity .6s ease-out}
.ill.in .note{opacity:1;transition-delay:1.25s}
@media (prefers-reduced-motion:reduce){.ill .note{opacity:1;transition:none}}
'''
