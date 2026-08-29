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
        <svg class="dg" viewBox="0 0 560 250" role="img"
             aria-label="An agent enclosed by bounds, with an escalation path back to a person and a record written on every action.">
          <g fill="none" stroke="#141413" stroke-opacity=".2" stroke-width="1" stroke-dasharray="4 4">
            <rect class="node" x="8" y="30" width="346" height="156" rx="2"/></g>
          <text x="16" y="20" fill="#5F5E58" font-size="10" letter-spacing=".14em">BOUNDS &middot; WHAT IT MAY TOUCH</text>
          <g fill="#E8E6DC" stroke="#141413" stroke-opacity=".38" stroke-width="1">
            <rect class="node" x="36" y="64" width="118" height="34" rx="1"/>
            <rect class="node" x="36" y="118" width="118" height="34" rx="1"/>
            <rect class="node" x="416" y="26" width="132" height="34" rx="1"/>
            <rect class="node" x="416" y="198" width="132" height="34" rx="1"/></g>
          <g fill="#141413" stroke="#B85C3E" stroke-width="1.4"><rect class="node" x="214" y="86" width="112" height="44" rx="1"/></g>
          <g fill="none" stroke="#141413" stroke-opacity=".26" stroke-width="1">
            <path class="edge" d="M154 81 L214 96"/><path class="edge" d="M154 135 L214 120"/></g>
          <g fill="none" stroke="#B85C3E" stroke-width="1.4" stroke-dasharray="5 4">
            <path class="edge" d="M326 100 Q380 100 380 43 L416 43"/></g>
          <g fill="none" stroke="#141413" stroke-opacity=".3" stroke-width="1">
            <path class="edge" d="M270 130 L270 215 L416 215"/></g>
          <g fill="#5F5E58">
            <text class="lab" x="95" y="85" text-anchor="middle">A SYSTEM</text>
            <text class="lab" x="95" y="139" text-anchor="middle">A SYSTEM</text>
            <text class="lab" x="270" y="112" text-anchor="middle" fill="#F0EEE6">AGENT</text>
            <text class="lab" x="482" y="47" text-anchor="middle">A PERSON</text>
            <text class="lab" x="482" y="219" text-anchor="middle">THE RECORD</text></g>
          <text x="344" y="76" fill="#9E4A2E" font-size="9.5">escalation</text>
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
        <svg class="dg" viewBox="0 0 920 280" role="img"
             aria-label="A generic workflow record: three inputs move through people and systems to a wait, a decision that gets re-made, and a rework loop back to the start.">
          <defs><marker id="g1" viewBox="0 0 8 8" refX="7.4" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1 L7.4 4 L0 7z" fill="#5F5E58"/></marker>
          <marker id="g2" viewBox="0 0 8 8" refX="7.4" refY="4" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M0 1 L7.4 4 L0 7z" fill="#B85C3E"/></marker></defs>
          <g class="edges" fill="none" stroke="#141413" stroke-opacity=".22" stroke-width="1" marker-end="url(#g1)">
            <path class="edge" d="M122 64 L162 64"/><path class="edge" d="M122 146 L162 146"/><path class="edge" d="M122 228 L162 228"/>
            <path class="edge" d="M310 64 L350 64 Q378 64 378 112 L378 126"/>
            <path class="edge" d="M310 228 L350 228 Q378 228 378 180 L378 166"/>
            <path class="edge" d="M310 146 L378 146"/><path class="edge" d="M512 146 L570 146"/><path class="edge" d="M726 172 L726 212"/></g>
          <g fill="none" stroke="#B85C3E" stroke-width="1.6" marker-end="url(#g2)"><path class="edge" d="M452 146 L480 146"/></g>
          <g fill="none" stroke="#B85C3E" stroke-opacity=".5" stroke-width="1"><path class="edge" d="M690 124 Q560 30 210 46 L164 54"/></g>
          <g fill="#F0EEE6" stroke="#141413" stroke-opacity=".34" stroke-width="1" class="nodes">
            <rect class="node" x="0" y="50" width="122" height="28" rx="1"/><rect class="node" x="0" y="132" width="122" height="28" rx="1"/><rect class="node" x="0" y="214" width="122" height="28" rx="1"/>
            <rect class="node" x="162" y="46" width="148" height="36" rx="1"/><rect class="node" x="162" y="128" width="148" height="36" rx="1"/><rect class="node" x="162" y="210" width="148" height="36" rx="1"/>
            <rect class="node" x="570" y="122" width="156" height="48" rx="1"/><rect class="node" x="614" y="212" width="172" height="34" rx="1"/></g>
          <g fill="#141413" stroke="#B85C3E" stroke-width="1.4"><rect class="node" x="378" y="124" width="74" height="44" rx="1"/></g>
          <g fill="#5F5E58" class="labs">
            <text class="lab" x="61" y="68" text-anchor="middle">REQUEST</text><text class="lab" x="61" y="150" text-anchor="middle">DOCUMENT</text><text class="lab" x="61" y="232" text-anchor="middle">APPROVAL</text>
            <text class="lab" x="236" y="68" text-anchor="middle">A PERSON</text><text class="lab" x="236" y="150" text-anchor="middle">A SYSTEM</text><text class="lab" x="236" y="232" text-anchor="middle">A HANDOFF</text>
            <text class="lab" x="648" y="142" text-anchor="middle" fill="#141413">DECISION</text><text class="lab" x="648" y="158" text-anchor="middle">RE-MADE</text>
            <text class="lab" x="700" y="233" text-anchor="middle">DOWNSTREAM</text>
            <text class="lab" x="415" y="150" text-anchor="middle" fill="#F0EEE6">WAIT</text></g>
          <g fill="#9E4A2E" font-size="9.5"><text class="lab" x="382" y="112">queue time</text><text class="lab" x="300" y="30">rework loop</text></g>
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
