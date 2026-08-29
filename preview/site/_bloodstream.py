# The hero graphic: work moving along rails, stations firing as it arrives.
# Timing is non-harmonic so the pattern never visibly repeats. No JS scheduler —
# each station's delay is computed from its own position along its own lane.

LANES = [
    # y, duration, path
    (128, 9.2,  "M -80,128 C 300,110 620,144 780,128 S 1180,114 1520,128"),
    (252, 11.6, "M -80,252 C 300,270 620,236 780,252 S 1180,268 1520,252"),
    (376, 8.4,  "M -80,376 C 300,358 620,392 780,376 S 1180,362 1520,376"),
    (500, 13.1, "M -80,500 C 300,518 620,484 780,500 S 1180,514 1520,500"),
    (624, 10.3, "M -80,624 C 300,606 620,640 780,624 S 1180,610 1520,624"),
]
STATION_X = [120, 380, 640, 900, 1160, 1400]
# normalised position of each station along its lane, used as the fire delay
STATION_F = [0.06, 0.24, 0.42, 0.58, 0.76, 0.94]

def svg():
    out = ['<svg class="bs" viewBox="0 0 1440 720" preserveAspectRatio="xMidYMid slice" aria-hidden="true">']
    out.append('<defs><radialGradient id="bsglow"><stop offset="0" stop-color="#D97757" stop-opacity=".5"/>'
               '<stop offset="1" stop-color="#D97757" stop-opacity="0"/></radialGradient></defs>')
    # cross-links first, so they sit under everything
    out.append('<g class="bs-x">')
    for i,(si) in enumerate([1,2,3,4]):
        if i+1 >= len(LANES): break
        y1, y2 = LANES[i][0], LANES[i+1][0]
        x = STATION_X[si]
        out.append(f'<path d="M {x},{y1} C {x+26},{y1+40} {x+26},{y2-40} {x},{y2}"/>')
    out.append('</g>')
    for li,(y,dur,d) in enumerate(LANES):
        out.append(f'<g class="bs-lane" style="--dur:{dur}s;--n:{li}">')
        out.append(f'<path class="bs-rail" d="{d}"/>')
        for si,(x,f) in enumerate(zip(STATION_X, STATION_F)):
            out.append(f'<g class="bs-st" style="--f:{f}" transform="translate({x},{y})">'
                       f'<rect x="-5" y="-5" width="10" height="10" rx="2" transform="rotate(45)"/>'
                       f'<circle class="bs-flash" r="3"/></g>')
        for t in range(3):
            out.append(f'<g class="bs-t" style="--t:{t};--path:path(\'{d}\')">'
                       f'<circle class="bs-halo" r="7" fill="url(#bsglow)"/>'
                       f'<circle class="bs-dot" r="2.5"/></g>')
        out.append('</g>')
    out.append('</svg>')
    return "\n".join(out)

CSS = """
/* ── the hero graphic: work moving, not type moving ──────────────── */
.bs{position:absolute;inset:0;width:100%;height:100%;z-index:0;pointer-events:none;
  overflow:visible;
  -webkit-mask-image:linear-gradient(100deg,transparent 0%,transparent 26%,
    rgba(0,0,0,.35) 44%,rgba(0,0,0,.9) 64%,#000 100%);
  mask-image:linear-gradient(100deg,transparent 0%,transparent 26%,
    rgba(0,0,0,.35) 44%,rgba(0,0,0,.9) 64%,#000 100%)}
.bs-rail{fill:none;stroke:rgba(20,20,19,.09);stroke-width:1;vector-effect:non-scaling-stroke}
.bs-x path{fill:none;stroke:rgba(20,20,19,.055);stroke-width:1;vector-effect:non-scaling-stroke}
.bs-st rect{fill:none;stroke:rgba(20,20,19,.2);stroke-width:1;vector-effect:non-scaling-stroke}
.bs-flash{fill:var(--accent-bright);opacity:.16}
.bs-dot{fill:var(--accent-bright)}
.bs-t{offset-path:var(--path);offset-rotate:0deg;offset-distance:0%}

[data-anim="on"] .bs-rail,[data-anim="on"] .bs-x path{
  stroke-dasharray:1700;stroke-dashoffset:1700;
  animation:bs-draw 1.1s cubic-bezier(.16,1,.3,1) forwards;
  animation-delay:calc(var(--n,0) * .09s)}
[data-anim="on"] .bs-t{opacity:0;animation:
  bs-flow var(--dur) linear infinite calc(var(--dur) / -3 * var(--t)),
  bs-in .5s ease-out 1.2s forwards}
[data-anim="on"] .bs-flash{animation:bs-fire var(--dur) linear infinite;
  animation-delay:calc(var(--dur) * var(--f))}

@keyframes bs-draw{to{stroke-dashoffset:0}}
@keyframes bs-flow{to{offset-distance:100%}}
@keyframes bs-in{to{opacity:1}}
@keyframes bs-fire{
  0%,100%{opacity:.16;transform:scale(1)}
  6%{opacity:.85;transform:scale(1.9)}
  22%{opacity:.16;transform:scale(1)}}

/* the frozen frame still shows work distributed along the lanes —
   a static fallback must depict the system, not empty pipes */
@media (prefers-reduced-motion:reduce){
  .bs *{animation:none!important}
  .bs-rail,.bs-x path{stroke-dashoffset:0}
  .bs-t:nth-child(4n+2){offset-distance:19%}
  .bs-t:nth-child(4n+3){offset-distance:52%}
  .bs-t:nth-child(4n+4){offset-distance:81%}
  .bs-flash{opacity:.4}}

/* the type has to win: presence is a ratio, and nothing may compete */
.hero{position:relative;z-index:1}
.s-open{position:relative;overflow:hidden}
"""
