exec(open('_h.py').read())

# ─────────────────────────────────────────────── STRATEGY · ground: clear
STRATEGY = '''
<section class="s s-open">
  <div class="w"><div class="g">
    <div class="m7 rv">
      <span class="eyebrow">Strategy</span>
      <h1>Pain is evidence, not the decision.</h1>
    </div>
    <div class="m5 rv" style="padding-top:12px">
      <p class="tx">The request usually arrives already answered: a workflow people dislike,
        and a tool that could take it over. That the work is painful is worth knowing — it is
        how a company points at itself. It is not the same as the work being worth changing.</p>
    </div>
  </div></div>
</section>

<section class="s s-punct">
  <div class="w"><div class="punct">
    <span class="k">The decision</span>
    <span class="v">Leave &middot; Simplify &middot; Automate &middot; Rebuild &middot; Retire</span>
  </div></div>
</section>

<section class="s s-bear">
  <div class="w">
    <div class="hd hd--ruled">
      <span class="eyebrow">Five outcomes</span>
      <h2>Building is one of the things an engagement can conclude.</h2>
    </div>
    <div class="g">
      <div class="m4"><div class="ruled"><h4>Leave it</h4>
        <p class="tx">Work done rarely, by people who are good at it, inside a process that is
          stable. Automating it moves the cost from doing the work to maintaining the
          automation.</p></div></div>
      <div class="m4"><div class="ruled"><h4>Simplify it</h4>
        <p class="tx">Steps exist because a system once could not do something. Asking whether
          the step still has to exist removes some of them without software.</p></div></div>
      <div class="m4"><div class="ruled"><h4>Automate it</h4>
        <p class="tx">The work is right and the rules hold. What is missing is that a person is
          carrying it between systems that do not speak.</p></div></div>
      <div class="m6"><div class="ruled"><h4>Rebuild it</h4>
        <p class="tx">The workflow is not slow because people are slow. The software underneath
          models something the company stopped doing.</p></div></div>
      <div class="m6"><div class="ruled"><h4>Retire it</h4>
        <p class="tx">The output has no reader. Nobody finds this without following the work to
          where it ends.</p></div></div>
      <div class="full" style="margin-top:14px"><div class="inset">
        <p class="q">A workflow is worth rebuilding when the cost of the waiting it creates
          exceeds the cost of the building — <b>inside one budget cycle</b>, a cycle the person
          approving it will still be accountable for.</p>
      </div></div>
      <p class="tx m7">That rule can be wrong. When it is, it is usually because the waiting
        turned out to be tolerable and the rework did not.</p>
    </div>
  </div>
</section>

<section class="s s-reg">
  <div class="w"><div class="g">
    <div class="m4">
      <span class="eyebrow" style="margin-bottom:10px">Where we say no</span>
      <p class="tx" style="font-size:16px">Some work is a poor candidate regardless of how much
        time it consumes. Saying so before the work starts costs us engagements. It is cheaper
        than saying it after.</p>
    </div>
    <div class="m8">
      <div class="rows">
        <div class="row"><span class="row__n">01</span><span class="row__t"><b>The process is still moving.</b> Automating a workflow that is being redesigned means building it twice.</span></div>
        <div class="row"><span class="row__n">02</span><span class="row__t"><b>The regulation is under revision.</b> A rule that changes is a rebuild when it changes.</span></div>
        <div class="row"><span class="row__n">03</span><span class="row__t"><b>The inputs are unreliable.</b> Automation makes bad inputs travel faster and reach further.</span></div>
        <div class="row"><span class="row__n">04</span><span class="row__t"><b>The judgement has never been made.</b> If nobody has decided what good looks like, there is nothing to encode.</span></div>
        <div class="row"><span class="row__n">05</span><span class="row__t"><b>Nobody owns the outcome.</b> A system without an owner degrades quietly, and the first person to notice is a customer.</span></div>
      </div>
    </div>
  </div></div>
</section>

<section class="s s-state">
  <div class="w"><div class="g">
    <p class="statement m8">A recommendation names what a change is made of. Not what it costs
      — that belongs in the room where your company is discussed.</p>
    <div class="m4" style="padding-top:8px">
      <div class="rows">
        <div class="row"><span class="row__n">&mdash;</span><span class="row__t">The integrations required</span></div>
        <div class="row"><span class="row__n">&mdash;</span><span class="row__t">Where a person stays in the loop</span></div>
        <div class="row"><span class="row__n">&mdash;</span><span class="row__t">Whether a new interface is needed</span></div>
        <div class="row"><span class="row__n">&mdash;</span><span class="row__t">What gets retired</span></div>
        <div class="row"><span class="row__n">&mdash;</span><span class="row__t">What would make it wrong</span></div>
      </div>
    </div>
  </div></div>
</section>

<section class="s s-close" id="next">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <span class="eyebrow">Next</span>
      <h2>The decision is made against a record.</h2>
      <p class="lead">The WorkGraph holds how work moves, who touches it, where it waits, and
        which decisions get made more than once.</p>
      <p style="margin-top:6px">
        <a class="cta" href="workgraph.html">What the record holds &rarr;</a>
        <a class="cta" href="implementation.html" style="margin-left:10px">What gets built &rarr;</a></p>
    </div>
  </div></div>
</section>
'''

# ─────────────────────────────────────── IMPLEMENTATION · ground: ivory
IMPL = '''
<section class="s s-open">
  <div class="w"><div class="g">
    <div class="m8 rv">
      <span class="eyebrow">Implementation &middot; The Dagg Factory</span>
      <h1 class="wide">Nothing is built until the decision, the owner and the way back are explicit.</h1>
    </div>
    <div class="m4 rv" style="padding-top:14px">
      <p class="tx">A factory is not a place that makes whatever it is asked to make. It makes
        one class of thing, to a standard, and its discipline is at the door.</p>
    </div>
  </div></div>
</section>

<section class="s s-punct">
  <div class="w"><div class="punct">
    <span class="k">Two modes</span>
    <span class="v">Automate what should stay. Rebuild what should change.</span>
  </div></div>
</section>

<section class="s s-cards">
  <div class="w"><div class="g">
    <div class="m6"><div class="ruled"><h3>Automate</h3>
      <p class="tx">Work that is right, carried by people between systems that do not speak.
        Agents take the carrying; the systems remain. Nobody learns a new tool, because the
        work continues where it already lives.</p></div></div>
    <div class="m6"><div class="ruled ruled--ac"><h3>Rebuild</h3>
      <p class="tx">Where the workflow layer is what is broken, an agent placed on top makes
        the wrong thing faster. Then it is new software, and often one fewer system
        afterwards.</p></div></div>
  </div></div>
</section>

<section class="s s-instr">
  <div class="w">
    <div class="hd">
      <span class="eyebrow">Governance</span>
      <h2>An agent needs three things before it is allowed to act.</h2>
    </div>
    <div class="g">
      <figure class="m7 scroll-x">
        <svg class="dg ill" viewBox="0 0 700 340" role="img"
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
</svg>
        <figcaption>Bounds are enforced, not requested. Escalation is decided in advance. The
          record is written on every action, including the ones that succeed.</figcaption>
      </figure>
      <div class="m5 side">
        <div class="rows">
          <div class="row"><span class="row__n">01</span><span class="row__t"><b>Bounds</b>, expressed as what it may touch rather than as an instruction it is asked to respect.</span></div>
          <div class="row"><span class="row__n">02</span><span class="row__t"><b>Escalation</b>, with the cases it must hand back decided in advance rather than discovered in production.</span></div>
          <div class="row"><span class="row__n">03</span><span class="row__t"><b>A record</b> of what it did and on what basis, readable months later when the question is why.</span></div>
        </div>
        <p class="tx" style="margin-top:20px;font-size:16px">The third is usually treated as
          compliance overhead. It is what makes the first two enforceable.</p>
      </div>
    </div>
  </div>
</section>

<section class="s s-state">
  <div class="w"><div class="g">
    <p class="statement m7">The WorkGraph is not documentation kept alongside the work. It is
      what the build reads from.</p>
    <div class="m5" style="padding-top:10px">
      <p class="tx">The agents that write the software query it directly, so the structure of
        the workflow is available rather than restated. <a href="workgraph.html">The record
        &rarr;</a></p>
    </div>
  </div></div>
</section>

<section class="s s-reg">
  <div class="w">
    <div class="hd"><span class="eyebrow">Production and ownership</span>
      <h2>Work ships with monitoring, a named owner and a documented way back.</h2></div>
    <div class="g">
      <div class="m6"><div class="ruled"><h4>You operate it</h4>
        <p class="tx">This requires someone who can read the monitoring, respond when an agent
          escalates, and judge when behaviour has drifted. We set that up and hand it over,
          including what to watch and what should worry you.</p></div></div>
      <div class="m6"><div class="ruled ruled--ac"><h4>We operate it</h4>
        <p class="tx">Where running agents is not a capability a company intends to build, the
          operation can stay with us under a separate agreement. The same record orchestrates
          what is live.</p></div></div>
      <p class="tx full">The software and the model of your company are yours either way, and
        that sits in the agreement rather than in a conversation.</p>
    </div>
  </div>
</section>

<section class="s s-close">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <span class="eyebrow">Aloi</span>
      <h2>One workflow problem became a company.</h2>
      <p class="lead">Aloi is Dagg&rsquo;s AI-native legal venture. It shows what a workflow
        problem can become when it is rebuilt rather than assisted.</p>
      <p style="margin-top:6px">
        <a class="cta" href="https://aloi.law">aloi.law &rarr;</a>
        <a class="cta" href="index.html#assessment" style="margin-left:10px">Book an assessment &rarr;</a></p>
    </div>
  </div></div>
</section>
'''

# ────────────────────────────────────────── WORKGRAPH · ground: clear
WG = '''
<section class="s s-open">
  <div class="w"><div class="g">
    <div class="m7 rv">
      <span class="eyebrow">WorkGraph</span>
      <h1>A company knows its org chart. It does not have a map of how work moves.</h1>
    </div>
    <div class="m5 rv" style="padding-top:12px">
      <p class="tx">Across people&rsquo;s heads, chat, spreadsheets, meetings, legacy systems
        and undocumented judgement. You cannot automate what you cannot see, so before anything
        is built the work has to be understood.</p>
    </div>
  </div></div>
</section>

<section class="s s-punct">
  <div class="w"><div class="punct">
    <span class="k">Built from</span>
    <span class="v">Evidence the company already generates &mdash; not a workshop.</span>
  </div></div>
</section>

<section class="s s-instr">
  <div class="w">
    <div class="hd"><span class="eyebrow">The artefact</span>
      <h2>What a record holds, with the contents removed.</h2></div>
    <div class="g">
      <figure class="full scroll-x">
        <svg class="dg ill" viewBox="0 0 940 400" role="img"
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
</svg>
        <figcaption>A generic structure, drawn to show the form of the record rather than any
          company&rsquo;s contents. The two labelled edges carry metric names, never values —
          the measurements belong to the client and stay there.</figcaption>
      </figure>
    </div>
  </div>
</section>

<section class="s s-bear">
  <div class="w">
    <div class="hd hd--ruled"><span class="eyebrow">Why it is the asset</span>
      <h2>The hard part was never the tooling.</h2></div>
    <div class="g">
      <div class="m7 stack">
        <p class="tx">Building a workflow into software is the part that has become
          straightforward. Getting the workflow out of the people who perform it is not, and it
          is where an engagement actually spends its time.</p>
        <p class="tx">What a company knows about itself is held in a form nobody can query: in
          the judgement of the person who has done the job for nine years, in the exception
          nobody documented, in the meeting where a decision gets made again because the reason
          was never written down.</p>
        <p class="tx">The WorkGraph is that knowledge in a form a machine can read. It is built
          from the artefacts the work already produces — build history, version control, ticket
          and issue data — rather than from a session where people describe what they believe
          they do, which is a different thing and usually wrong in the same places.</p>
        <p class="tx"><b>It is also why the second engagement is not the first one again.</b>
          The record persists after the build, so a later change reads from something that
          already exists.</p>
      </div>
      <div class="m5 side">
        <span class="mi">What it holds</span>
        <div class="rows" style="margin-top:16px">
          <div class="row"><span class="row__n">&mdash;</span><span class="row__t">Workflows, and the paths through them</span></div>
          <div class="row"><span class="row__n">&mdash;</span><span class="row__t">Decisions, and who makes them</span></div>
          <div class="row"><span class="row__n">&mdash;</span><span class="row__t">Systems, and what each holds</span></div>
          <div class="row"><span class="row__n">&mdash;</span><span class="row__t">Handoffs, and where they wait</span></div>
          <div class="row"><span class="row__n">&mdash;</span><span class="row__t">Knowledge that lives in a person</span></div>
        </div>
      </div>
    </div>
  </div>
</section>

<section class="s s-state">
  <div class="w"><div class="g">
    <p class="statement m8">Clients do not appear on this site, and that will include you. What
      can be shown is the form of the record — never its contents.</p>
    <div class="m4" style="padding-top:10px">
      <p class="tx"><a href="faq.html">How confidentiality works &rarr;</a></p>
    </div>
  </div></div>
</section>

<section class="s s-close">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <span class="eyebrow">Three states</span>
      <h2>Built once. Read by the build. Runs what is live.</h2>
      <p class="lead">The record made during the assessment is the same object the code agents
        query while building, and the same one that orchestrates agents in production.</p>
      <p style="margin-top:6px">
        <a class="cta" href="implementation.html">What gets built &rarr;</a>
        <a class="cta" href="index.html#assessment" style="margin-left:10px">Book an assessment &rarr;</a></p>
    </div>
  </div></div>
</section>
'''

build('strategy','Strategy — Dagg','What is worth rebuilding, what is not yet, and what decides.','clear','s',STRATEGY)
build('implementation','Implementation — Dagg','How a decision becomes something running in production.','ivory','i',IMPL)
build('workgraph','WorkGraph — Dagg','The record of how work actually moves through a company.','clear','w',WG)
