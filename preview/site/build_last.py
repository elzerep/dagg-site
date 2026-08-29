exec(open('_h.py').read())

COMPANY = '''
<section class="s s-open">
  <div class="w"><div class="g">
    <div class="m7 rv">
      <span class="eyebrow">Company</span>
      <h1 class="wide">The people who decide what should change are the people accountable for what gets built.</h1>
    </div>
    <div class="m5 rv" style="padding-top:14px">
      <p class="tx">Dagg maps how a company actually works and builds the system that runs it.
        Strategy and engineering are the same engagement here, carried out by the same people.</p>
    </div>
  </div></div>
</section>

<section class="s s-punct">
  <div class="w"><div class="punct">
    <span class="k">So far</span>
    <span class="v">Legal, and banking and finance. The shape of the work decides, not the sector.</span>
  </div></div>
</section>

<section class="s s-bear">
  <div class="w">
    <div class="hd hd--ruled">
      <span class="eyebrow">How we work</span>
      <h2>Clients do not appear here.</h2>
    </div>
    <div class="g">
      <div class="m7 stack">
        <p class="tx">No names, no logos, no case studies, no measurements from real
          engagements. This is not a gap waiting for permission — it is the standard. Anything
          we could show you about another company, we could one day show another company about
          you.</p>
        <p class="tx">Companies where decisions have to be traceable, and where the knowledge
          that matters sits with people rather than in systems, are where this work fits. That
          has meant legal, and banking and finance. The shape of the work decides.</p>
      </div>
      <div class="m5 side">
        <span class="mi">In the agreement</span>
        <div class="rows" style="margin-top:16px">
          <div class="row"><span class="row__n">01</span><span class="row__t">The software is yours, and so is the model of your company</span></div>
          <div class="row"><span class="row__n">02</span><span class="row__t">Access is scoped to the work, and it ends</span></div>
          <div class="row"><span class="row__n">03</span><span class="row__t">An assessment may conclude that nothing should be built</span></div>
        </div>
        <p class="tx" style="margin-top:20px;font-size:16px">The security and data-processing
          pack is reviewed with your team under NDA. <a href="faq.html">More in the FAQ &rarr;</a></p>
      </div>
    </div>
  </div>
</section>

<section class="s s-band">
  <img src="../../assets/img/flow-01.webp" alt="" width="2000" height="750" loading="lazy">
</section>

<section class="s s-reg">
  <div class="w">
    <div class="hd"><span class="eyebrow">Leadership</span>
      <h2>Two people are accountable.</h2></div>
    <div class="g">
      <div class="m6"><div class="ruled">
        <h3>Christian P&eacute;rez</h3>
        <span class="mi">Chief Executive Officer</span>
        <p><a href="https://www.linkedin.com/" rel="noopener">LinkedIn &rarr;</a></p>
      </div></div>
      <div class="m6"><div class="ruled">
        <h3>Simon Lundmark</h3>
        <span class="mi">Chief Technology Officer</span>
        <p><a href="https://www.linkedin.com/" rel="noopener">LinkedIn &rarr;</a></p>
      </div></div>
    </div>
  </div>
</section>

<section class="s s-state">
  <div class="w"><div class="g">
    <p class="statement m8">One workflow problem became a company. Aloi is Dagg&rsquo;s
      AI-native legal venture.</p>
    <div class="m4" style="padding-top:12px">
      <p class="tx"><a href="https://aloi.law">aloi.law &rarr;</a></p>
    </div>
  </div></div>
</section>

<section class="s s-close">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <span class="eyebrow">Working here</span>
      <h2>We do not post roles.</h2>
      <p class="lead">The constraint has never been headcount. It is finding people who hold
        both halves of the work.</p>
      <p style="margin-top:6px">
        <a class="cta" href="careers.html">Careers &rarr;</a>
        <a class="cta" href="index.html#assessment" style="margin-left:10px">Book an assessment &rarr;</a></p>
    </div>
  </div></div>
</section>
'''

FAQ = '''
<section class="s s-open">
  <div class="w"><div class="g">
    <div class="m7 rv">
      <span class="eyebrow">Questions</span>
      <h1>The answers that decide an engagement.</h1>
    </div>
    <div class="m5 rv" style="padding-top:14px">
      <p class="tx">Ownership, data, access and what happens after launch. The security and
        data-processing pack goes further, under NDA.</p>
    </div>
  </div></div>
</section>

<section class="s s-bear">
  <div class="w">
    <div class="hd hd--ruled"><span class="eyebrow">Ownership and data</span>
      <h2>What is yours, and what we hold.</h2></div>
    <div class="qas">
      <div class="qa"><span class="qa__n">01</span><div><h3 class="qa__q">Who owns the software you build?</h3>
        <p class="qa__a">You do — the software written for you, and the model of your company underneath it. Dagg&rsquo;s own tooling and any third-party or open-source components remain what they are, and are identified as such before a build starts.</p></div></div>
      <div class="qa"><span class="qa__n">02</span><div><h3 class="qa__q">Is our data or our work used to improve anything you sell?</h3>
        <p class="qa__a">No. Client material is not used to train or tune models, and it does not become part of anything offered to another company.</p></div></div>
      <div class="qa"><span class="qa__n">03</span><div><h3 class="qa__q">Where does our data sit?</h3>
        <p class="qa__a">In your environment. Where a piece of work requires data to move, what moves, where it goes and for how long is agreed in writing before it does.</p></div></div>
      <div class="qa"><span class="qa__n">04</span><div><h3 class="qa__q">What access do you need?</h3>
        <p class="qa__a">What a specific piece of work requires, asked for specifically, with the reason stated. Access is scoped to the work and ends when the work does. There is no standing access.</p></div></div>
      <div class="qa"><span class="qa__n">05</span><div><h3 class="qa__q">Can we see your security and data-processing documentation?</h3>
        <p class="qa__a">Yes, under NDA. The data-processing agreement, the current subprocessor list, the data map, retention and deletion, incident handling and change control are a single pack, kept current, and reviewed with your security function rather than published here. A public page cannot make commitments to a reader who has no contract.</p></div></div>
    </div>
  </div>
</section>

<section class="s s-punct">
  <div class="w"><div class="punct">
    <span class="k">After launch</span>
    <span class="v">You can operate it, or we can. It is a choice worth making deliberately.</span>
  </div></div>
</section>

<section class="s s-reg">
  <div class="w">
    <div class="hd"><span class="eyebrow">The work itself</span>
      <h2>What changes, and what happens next.</h2></div>
    <div class="qas">
      <div class="qa"><span class="qa__n">06</span><div><h3 class="qa__q">Do you replace our existing systems?</h3>
        <p class="qa__a">Only where the system is what is broken. A large part of the work leaves systems in place and takes over the carrying between them. Replacing software is disruptive, and it earns that disruption when the software models a company that no longer exists.</p></div></div>
      <div class="qa"><span class="qa__n">07</span><div><h3 class="qa__q">Who runs it after you leave?</h3>
        <p class="qa__a">You can, or we can. Operating it yourself requires someone who can read the monitoring, respond to escalations and judge when behaviour has drifted; we set that up and hand it over. Where that is not a capability you intend to build, the operation can stay with us under a separate agreement.</p></div></div>
      <div class="qa"><span class="qa__n">08</span><div><h3 class="qa__q">What if it does not work?</h3>
        <p class="qa__a">A baseline is set before anything moves, so the question has an answer rather than an opinion. Changes ship with a documented way back, and anything that cannot be reversed is identified as such before it is built.</p></div></div>
      <div class="qa"><span class="qa__n">09</span><div><h3 class="qa__q">Can we see examples of your work?</h3>
        <p class="qa__a">No. Clients do not appear on this site, and that will include you. Method questions can be answered specifically in a conversation under NDA.</p></div></div>
      <div class="qa"><span class="qa__n">10</span><div><h3 class="qa__q">How does an engagement start?</h3>
        <p class="qa__a">With an assessment: one path through the company, mapped, ending in a recommendation — including the recommendation not to build.</p></div></div>
    </div>
  </div>
</section>

<section class="s s-close">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <h2>Still something unanswered?</h2>
      <p class="lead">Method questions can be answered specifically in a conversation under NDA.</p>
      <p style="margin-top:6px"><a class="cta" href="index.html#assessment">Book an assessment &rarr;</a></p>
    </div>
  </div></div>
</section>
'''

CAREERS = '''
<section class="s s-open">
  <div class="w"><div class="g">
    <div class="m7 rv">
      <span class="eyebrow">Careers</span>
      <h1>We do not post roles.</h1>
    </div>
    <div class="m5 rv" style="padding-top:14px">
      <p class="tx">The people we want to meet are usually not looking, and a posting is a poor
        way to reach them.</p>
    </div>
  </div></div>
</section>

<section class="s s-bear">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <p class="lead">The constraint has never been headcount. It is finding people who hold
        both halves of the work — who can sit with an operations team on Tuesday and be useful
        in the codebase on Wednesday, and who can tell the difference between a workflow that
        is painful and one that is expensive.</p>
      <p class="tx">That combination does not sort well into a job description, which is part
        of why there is no listing to answer.</p>
      <p class="tx">Small engagements, few clients, and direct contact with the people whose
        work is changing. Everything happens under confidentiality, which means the work is not
        something you can show afterwards. That suits some people and not others, and it is
        worth knowing before you write.</p>
    </div>
    <div class="m5 side">
      <span class="mi">If this is your work</span>
      <p class="tx" style="margin-top:12px">Write and tell us what you have built — the thing
        itself, not the role you held while it happened.</p>
      <p style="margin-top:16px"><a class="cta" href="mailto:hello@dagg.ai">hello@dagg.ai &rarr;</a></p>
      <!-- STAGING: employment or contract, base, remote policy, and how candidate
           material is handled. Needs Christian before this ships. -->
    </div>
  </div></div>
</section>

<section class="s s-close">
  <div class="w"><div class="g">
    <div class="m7 stack">
      <h2>Or come at it from the other side.</h2>
      <p class="lead">If you are a company rather than a candidate, the first piece of work is
        an assessment.</p>
      <p style="margin-top:6px"><a class="cta" href="index.html#assessment">Book an assessment &rarr;</a></p>
    </div>
  </div></div>
</section>
'''

QA_CSS = '''
<style>
.qas{display:flex;flex-direction:column}
.qa{display:grid;grid-template-columns:34px minmax(0,1fr);gap:18px;
  padding:24px 0;border-bottom:1px solid var(--hair)}
.qa:first-child{border-top:1px solid var(--hair)}
.qa__n{font-family:var(--mono);font-size:12px;letter-spacing:.14em;color:var(--accent-text);
  font-variant-numeric:tabular-nums;padding-top:5px}
.qa__q{font-family:var(--sans);font-weight:400;font-size:clamp(19px,2vw,25px);
  line-height:1.14;letter-spacing:-.028em;color:var(--ink)}
.qa__a{font-family:var(--serif);font-optical-sizing:auto;font-size:16.5px;line-height:1.68;
  color:var(--ink-2);max-width:62ch;margin-top:10px}
@media(max-width:560px){.qa{grid-template-columns:1fr;gap:6px}.qa__n{padding-top:0}}
</style>'''

build('company','Company — Dagg','How we work, what is in the agreement, and who is accountable.','clear','c',COMPANY)
build('faq','FAQ — Dagg','Ownership, data, access and what happens after launch.','clear','',FAQ,QA_CSS)
build('careers','Careers — Dagg','We do not post roles.','ivory','',CAREERS)
