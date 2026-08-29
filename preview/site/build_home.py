exec(open('_h.py').read())

EXTRA = '''
<style>


.hero{display:grid;grid-template-columns:minmax(0,7fr) minmax(0,5fr);gap:clamp(30px,4.4vw,72px);align-items:center}
@media(max-width:1040px){.hero{grid-template-columns:1fr}}
.hero__fig svg{max-width:none}
.hg .n rect{fill:var(--warm);stroke:var(--ink);stroke-opacity:.34;stroke-width:1}
.hg .n text{fill:var(--ink-3)}
.hg .e{fill:none;stroke:var(--ink);stroke-opacity:.2;stroke-width:1}
.hg .core rect{fill:var(--ink);stroke:var(--accent);stroke-width:1.3}
.hg .core text{fill:var(--n-fg)}
.hg .lab{fill:var(--accent-text);font-size:9.5px}
.hg .att{opacity:0;transition:opacity .45s cubic-bezier(.16,1,.3,1)}
.hg .att.on{opacity:1}
.hg .att rect{fill:none;stroke:var(--accent);stroke-width:1.2}
.hg .att text{fill:var(--accent-text)}
.hg .att path{stroke:var(--accent);stroke-width:1.4;fill:none}
.lives{display:flex;flex-direction:column}
.life{border-top:1px solid var(--hair);padding:17px 0;transition:border-color .3s ease}
.life:last-child{border-bottom:1px solid var(--hair)}
.life h3{transition:color .3s ease}
.life p{margin-top:5px}
.life.on{border-top-color:var(--accent)}
.life.on h3{color:var(--accent-text)}
@media (prefers-reduced-motion:reduce){.hg .att{transition:none}
  .hg .att:first-of-type{opacity:1}}
</style>'''

BODY = '''
<!-- OPENING · 420–560px · the claim, and nothing behind it -->
<section class="s s-hero">
  <img class="s-hero__bg" src="../../assets/img/hero-01.webp" alt="" width="2200" height="1238">
  <div class="w">
    <div class="hero">
      <div class="rv">
        <span class="eyebrow">AI transformation</span>
        <h1 class="wide">We map how your company actually works — then build the system that runs it.</h1>
        <p class="lead">Dagg starts with the work: how it moves, where it waits, and what is
          worth changing.</p>
      </div>
      <div class="rv" style="padding-bottom:6px">
        <p class="tx">Most companies buy AI tools before they understand their own work. The
          ones that get this right stop running at the speed of the people carrying the work,
          and start running at the speed of the system doing it.</p>
        <p class="tx" style="margin-top:15px"><b>A machine works at machine speed.</b> That
          gap does not close on its own, and it compounds.</p>
        <p style="margin-top:22px"><a class="cta" href="#assessment">Book an assessment &rarr;</a></p>
      </div>
    </div>
  </div>
</section>

<!-- PUNCTUATION · 120–180px · one line, almost nothing -->
<section class="s s-punct">
  <div class="w"><div class="punct">
    <span class="k">Where this fits</span>
    <span class="v">Decisions that must be traceable. Knowledge that sits with people, not systems.</span>
  </div></div>
</section>

<!-- INSTRUMENT · 700–1000px · the mechanism, working -->
<section class="s s-instr">
  <div class="w">
    <div class="hd">
      <span class="eyebrow">WorkGraph</span>
      <h2>One record, read three times.</h2>
    </div>
    <div class="g">
      <figure class="m7 scroll-x" data-lives>
        <svg class="hg" viewBox="0 0 600 300" role="img"
             aria-label="A record of how work moves, shown with three different things attached to it in turn: the evidence it is built from, the agents that query it, and the agents it orchestrates.">
          <defs><marker id="a" viewBox="0 0 8 8" refX="7.4" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1 L7.4 4 L0 7z" fill="#B85C3E"/></marker></defs>
          <g class="e">
            <path d="M104 72 L146 72"/><path d="M104 150 L146 150"/><path d="M104 228 L146 228"/>
            <path d="M258 72 L286 72 Q306 72 306 122 L306 138"/>
            <path d="M258 228 L286 228 Q306 228 306 178 L306 162"/>
            <path d="M258 150 L306 150"/>
          </g>
          <g class="n">
            <rect x="0" y="58" width="104" height="28" rx="1"/><text x="52" y="76" text-anchor="middle">REQUEST</text>
            <rect x="0" y="136" width="104" height="28" rx="1"/><text x="52" y="154" text-anchor="middle">DOCUMENT</text>
            <rect x="0" y="214" width="104" height="28" rx="1"/><text x="52" y="232" text-anchor="middle">APPROVAL</text>
            <rect x="146" y="54" width="112" height="36" rx="1"/><text x="202" y="76" text-anchor="middle">A PERSON</text>
            <rect x="146" y="132" width="112" height="36" rx="1"/><text x="202" y="154" text-anchor="middle">A SYSTEM</text>
            <rect x="146" y="210" width="112" height="36" rx="1"/><text x="202" y="232" text-anchor="middle">A HANDOFF</text>
          </g>
          <g class="n core"><rect x="306" y="128" width="80" height="44" rx="1"/>
            <text x="346" y="146" text-anchor="middle">WORK</text><text x="346" y="160" text-anchor="middle">GRAPH</text></g>
          <text class="lab" x="150" y="112">queue time</text>

          <g class="att" data-state>
            <path d="M386 150 L436 150" marker-end="url(#a)"/>
            <rect x="436" y="130" width="150" height="40" rx="1"/>
            <text x="511" y="147" text-anchor="middle">BUILD HISTORY</text>
            <text x="511" y="161" text-anchor="middle" opacity=".7">TICKETS · VERSIONS</text>
          </g>
          <g class="att" data-state>
            <path d="M436 150 L390 150" marker-end="url(#a)"/>
            <rect x="436" y="130" width="150" height="40" rx="1"/>
            <text x="511" y="147" text-anchor="middle">CODE AGENTS</text>
            <text x="511" y="161" text-anchor="middle" opacity=".7">QUERY THE RECORD</text>
          </g>
          <g class="att" data-state>
            <path d="M386 150 Q412 150 412 118 L436 118" marker-end="url(#a)"/>
            <path d="M386 150 Q412 150 412 182 L436 182" marker-end="url(#a)"/>
            <rect x="436" y="100" width="150" height="36" rx="1"/><text x="511" y="122" text-anchor="middle">AGENT · LIVE</text>
            <rect x="436" y="164" width="150" height="36" rx="1"/><text x="511" y="186" text-anchor="middle">AGENT · LIVE</text>
          </g>
        </svg>
        <figcaption>A generic structure, drawn to show what the record holds. The edges that
          carry a label are the ones a baseline measures first — those measurements belong to
          the client.</figcaption>
      </figure>

      <div class="m5 lives">
        <div class="life" data-life>
          <h3>Mapped</h3>
          <p class="tx">How work moves through the company, including the parts nobody wrote
            down. Built from evidence the company already generates.</p>
        </div>
        <div class="life" data-life>
          <h3>Read</h3>
          <p class="tx">The agents that write the software query it directly, so the structure
            of the work is available to them rather than restated each time.</p>
        </div>
        <div class="life" data-life>
          <h3>Running</h3>
          <p class="tx">The same record orchestrates what is live, where operating agents is
            not a capability a company intends to build.</p>
        </div>
      </div>
    </div>
  </div>
</section>

<!-- STATEMENT · 260–420px · one sentence -->
<section class="s s-state">
  <div class="w"><div class="g">
    <p class="statement m8">It is the same record throughout, which is what keeps a change in
      year two from starting as a new discovery exercise.</p>
    <div class="m4"><p class="tx" style="font-size:16px"><a href="workgraph.html">What the record
      holds &rarr;</a></p></div>
  </div></div>
</section>

<!-- BAND · full-bleed, the page's one piece of atmosphere -->
<section class="s s-band">
  <img src="../../assets/img/flow-01.webp" alt="" width="2000" height="750" loading="lazy">
</section>

<!-- BEARER · 1000–1500px · the section that carries the page -->
<section class="s s-bear">
  <div class="w">
    <div class="hd hd--ruled">
      <span class="eyebrow">How the work runs</span>
      <h2>Two halves, and neither is optional.</h2>
    </div>
    <div class="g">
      <div class="m7 stack">
        <p class="tx">An engagement begins with a decision, and building is only one of the
          things it can conclude. Work is left alone, simplified, automated, rebuilt or
          retired — and three of those five mean nothing gets built.</p>
        <p class="tx">Deciding which is which is the part that cannot be bought as software.
          It needs someone who has followed the work to where it ends, seen where a decision
          gets made twice, and can say plainly that the workflow everyone hates is not the one
          worth changing.</p>
        <p class="tx">Then it has to be built, and shipped, and survive contact with a company
          that is still running while it changes. That needs engineers who will be accountable
          for what happens in production, not a specification handed to someone else.</p>
        <p class="tx"><b>The same people do both.</b> Not as a claim about how we are
          organised — as the reason a recommendation can carry what it would consist of, and
          a build can open with what we chose not to make.</p>
        <p style="margin-top:8px"><a class="cta" href="strategy.html">How the decision is made &rarr;</a></p>
      </div>
      <div class="m5 side">
        <span class="mi">Where we say no</span>
        <div class="rows" style="margin-top:16px">
          <div class="row"><span class="row__n">01</span><span class="row__t">The process is still moving</span></div>
          <div class="row"><span class="row__n">02</span><span class="row__t">The regulation is under revision</span></div>
          <div class="row"><span class="row__n">03</span><span class="row__t">The inputs are unreliable</span></div>
          <div class="row"><span class="row__n">04</span><span class="row__t">The judgement has never been made</span></div>
          <div class="row"><span class="row__n">05</span><span class="row__t">Nobody owns the outcome</span></div>
        </div>
        <p class="tx" style="margin-top:20px;font-size:16px">Saying this before the work starts
          is cheaper than saying it after.</p>
      </div>
    </div>
  </div>
</section>

<!-- PUNCTUATION -->
<section class="s s-punct">
  <div class="w"><div class="punct">
    <span class="k">So far</span>
    <span class="v">Legal, and banking and finance. The shape of the work decides, not the sector.</span>
  </div></div>
</section>

<!-- REGISTER · 400–600px -->
<section class="s s-reg">
  <div class="w"><div class="g">
    <div class="m4">
      <div class="ruled ruled--ac">
        <span class="mi">Aloi</span>
        <p class="tx" style="font-size:16px">Dagg&rsquo;s AI-native legal venture. It shows what
          a workflow problem can become when it is rebuilt rather than assisted.</p>
        <p><a href="https://aloi.law" style="font-size:15px">aloi.law &rarr;</a></p>
      </div>
    </div>
    <div class="m8">
      <div class="inset">
        <p class="q">Most of what a company asks us to automate <b>should not be.</b> Working
          out which part should is the whole of the first engagement.</p>
      </div>
    </div>
  </div></div>
</section>

<!-- CLOSE · 380–470px · the only ground change on the page -->
<section class="s s-close" id="assessment">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <span class="eyebrow">The first piece of work</span>
      <h2>An assessment can conclude that nothing should be built.</h2>
      <p class="lead">It maps one path through the company and ends in a recommendation: what
        should change, what should not, what a change would consist of, who would own the
        result, and what would make the recommendation wrong.</p>
      <p style="margin-top:6px"><a class="cta" href="mailto:hello@dagg.ai">Book an assessment &rarr;</a></p>
    </div>
    <div class="m5 side">
      <span class="mi">What you receive</span>
      <div class="rows" style="margin-top:16px">
        <div class="row"><span class="row__n">01</span><span class="row__t">The map of one path</span></div>
        <div class="row"><span class="row__n">02</span><span class="row__t">A recommendation, or the reason not to</span></div>
        <div class="row"><span class="row__n">03</span><span class="row__t">What would make it wrong</span></div>
      </div>
    </div>
  </div></div>
</section>
'''
build('index','Dagg — AI transformation',
      'Dagg maps how a company actually works, then builds the system that runs it.',
      'ivory','', BODY, EXTRA)
