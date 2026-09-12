exec(open('_h.py').read())

BODY = '''
<section class="s s-open">
  <div class="w"><div class="g">
    <div class="m7 rv">
      <span class="eyebrow">The first piece of work</span>
      <h1 class="wide">An assessment maps one path through the company and ends in a recommendation.</h1>
    </div>
    <div class="m5 rv" style="padding-top:14px">
      <p class="tx">It can conclude that nothing should be built. That outcome is delivered
        with the same detail as any other, and it is the reason the first piece of work is
        worth buying.</p>
      <p style="margin-top:20px"><a class="cta" href="mailto:hello@dagg.ai?subject=WorkGraph%20assessment">Write to us &rarr;</a></p>
    </div>
  </div></div>
</section>

<section class="s s-punct">
  <div class="w"><div class="punct">
    <span class="k">Scope</span>
    <span class="v">One path through the company. Not the whole company.</span>
  </div></div>
</section>

<section class="s s-bear">
  <div class="w">
    <div class="hd hd--ruled">
      <span class="eyebrow">What happens</span>
      <h2>Four things, in this order.</h2>
    </div>
    <div class="g">
      <div class="m7">
        <div class="rows">
          <div class="row"><span class="row__n">01</span><span class="row__t"><b>We agree the path.</b> One workflow, end to end, chosen because something about it is expensive rather than because it is annoying. Naming it takes a conversation, not a workshop.</span></div>
          <div class="row"><span class="row__n">02</span><span class="row__t"><b>We read the evidence.</b> Build history, version control, ticket and issue data, the artefacts the work already produces. We ask for what a specific question requires, with the reason stated.</span></div>
          <div class="row"><span class="row__n">03</span><span class="row__t"><b>We sit with the people who do it.</b> Not to be told the process, but to find where it departs from the process — the exception nobody documented, the decision that gets made twice.</span></div>
          <div class="row"><span class="row__n">04</span><span class="row__t"><b>We deliver a recommendation.</b> Which of the five outcomes applies, what a change would consist of, who would own the result, and the observation that would make us withdraw it.</span></div>
        </div>
      </div>
      <div class="m5 side">
        <span class="mi">Who takes part</span>
        <p class="tx" style="margin-top:12px;font-size:16px">Someone who owns the outcome, and
          the people who actually carry the work. It does not need a steering group, and it
          does not need everyone.</p>
        <span class="mi" style="margin-top:24px">What we need</span>
        <p class="tx" style="margin-top:12px;font-size:16px">Read access to the systems the
          workflow crosses, scoped to the question and ending when the work does. Nothing
          standing, nothing broad.</p>
        <span class="mi" style="margin-top:24px">Where it stops</span>
        <p class="tx" style="margin-top:12px;font-size:16px">At the recommendation. Building is
          a separate decision, made with the recommendation in hand.</p>
      </div>
    </div>
  </div>
</section>

<section class="s s-band">
  <img src="../../assets/img/flow-01.webp" alt="" width="2000" height="750" loading="lazy">
</section>

<section class="s s-reg">
  <div class="w">
    <div class="hd"><span class="eyebrow">What you receive</span>
      <h2>Three things you keep, whatever you decide next.</h2></div>
    <div class="g">
      <div class="m4"><div class="ruled"><h4>The map</h4>
        <p class="tx">The WorkGraph for the path we followed: who touches the work, which
          systems it crosses, where it waits, and which decisions get made more than once.</p></div></div>
      <div class="m4"><div class="ruled"><h4>The recommendation</h4>
        <p class="tx">What should change and what should not — including the case for leaving
          it alone — with what a change would be made of rather than what it would cost.</p></div></div>
      <div class="m4"><div class="ruled ruled--ac"><h4>The baseline</h4>
        <p class="tx">The measurements taken before anything moves, so that whatever happens
          next can be judged rather than argued about. They are yours and they stay with
          you.</p></div></div>
    </div>
  </div>
</section>

<section class="s s-state">
  <div class="w"><div class="g">
    <p class="statement m8">A recommendation you cannot act on is a report. We write the one we
      would build from.</p>
    <div class="m4" style="padding-top:12px">
      <p class="tx"><a href="strategy.html">How the decision is made &rarr;</a></p>
    </div>
  </div></div>
</section>

<section class="s s-close">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <span class="eyebrow">Getting started</span>
      <h2>Tell us which workflow you would pick, and why.</h2>
      <p class="lead">That one sentence is usually enough to know whether there is work here.
        If there is not, we will say so before anything is agreed.</p>
      <p style="margin-top:6px"><a class="cta" href="mailto:hello@dagg.ai?subject=WorkGraph%20assessment">hello@dagg.ai &rarr;</a></p>
    </div>
    <div class="m5 side">
      <span class="mi">Before you write</span>
      <p class="tx" style="margin-top:12px">Nothing confidential is needed to start a
        conversation, and nothing confidential should be sent in a first email. The NDA comes
        before the detail, not after.</p>
    </div>
  </div></div>
</section>
'''
build('assessment','Book an assessment — Dagg',
      'One path through the company, mapped, ending in a recommendation.',
      'ivory','', BODY)
