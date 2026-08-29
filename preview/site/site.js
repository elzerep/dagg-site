/* Movement here is the argument, not the polish: what Dagg sells is work
   moving at machine speed, so a page that sits still contradicts itself.
   The test from the design language still applies — motion earns its place
   when it shows the mechanism. Timings are Anthropic's and Palantir's,
   measured rather than guessed. */
(function(){
  var d=document, root=d.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── entrance: 800ms expo-out, 150ms stagger, per section ───────── */
  if(!reduce){
    root.setAttribute('data-anim','on');
    d.querySelectorAll('.s').forEach(function(s){
      s.querySelectorAll('.rv').forEach(function(el,i){
        el.style.setProperty('--i', Math.min(i,4));
      });
    });
    var io = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); }
      });
    },{threshold:.12, rootMargin:'0px 0px -8% 0px'});
    d.querySelectorAll('.s').forEach(function(s){ io.observe(s); });
  }

  /* ── nav ────────────────────────────────────────────────────────── */
  var tg = d.querySelector('.nav__toggle'), lk = d.getElementById('navlinks');
  if(tg && lk){
    tg.addEventListener('click', function(){
      var open = lk.classList.toggle('open');
      tg.setAttribute('aria-expanded', open ? 'true':'false');
      tg.textContent = open ? 'Close' : 'Menu';
    });
  }

  /* the bar only becomes a bar once it leaves the hero */
  var nav=d.querySelector('.nav'), hero=d.querySelector('.s-hero');
  if(nav && hero){
    d.body.setAttribute('data-hero','dark');
    var nio=new IntersectionObserver(function(es){
      es.forEach(function(e){ nav.classList.toggle('stuck', !e.isIntersecting); });
    },{rootMargin:'-70px 0px 0px 0px',threshold:0});
    nio.observe(hero);
  }

  /* ── progress ───────────────────────────────────────────────────── */
  var bar = d.querySelector('.progress');
  if(bar){
    var tick=function(){
      var h = d.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h>0 ? Math.min(window.scrollY/h,1)*100 : 0)+'%';
    };
    window.addEventListener('scroll',tick,{passive:true});
    window.addEventListener('resize',tick); tick();
  }

  /* ── the rotating word. 3s a word, a blur morph through the swap.
        It is the sentence's object that changes, which is the point:
        the same record does several different jobs. ─────────────── */
  var slot = d.querySelector('[data-rotate]');
  if(slot){
    var words = slot.getAttribute('data-rotate').split('|');
    var host = slot.querySelector('.rot__list');
    words.forEach(function(w,i){
      var span=d.createElement('span');
      span.className='rot__w'+(i===0?' on':''); span.textContent=w;
      host.appendChild(span);
    });
    /* the slot is sized to the longest word so nothing reflows */
    var probe=d.createElement('span'); probe.className='rot__probe';
    probe.textContent=words.reduce(function(a,b){return a.length>b.length?a:b;});
    host.appendChild(probe);
    if(!reduce){
      var k=0, all=host.querySelectorAll('.rot__w');
      setInterval(function(){
        all[k].classList.remove('on');
        k=(k+1)%all.length;
        all[k].classList.add('on');
      },3000);
    }
  }

  /* ── one record, three states. Reader-driven; it does not cycle. ── */
  var lives = d.querySelector('[data-lives]');
  if(lives){
    var states = lives.querySelectorAll('[data-state]');
    var items  = d.querySelectorAll('[data-life]');
    var show=function(n){
      states.forEach(function(s,i){ s.classList.toggle('on', i===n); });
      items.forEach(function(l,i){ l.classList.toggle('on', i===n); });
    };
    show(0);
    items.forEach(function(l,i){
      l.setAttribute('tabindex','0');
      l.addEventListener('mouseenter',function(){ show(i); });
      l.addEventListener('focus',function(){ show(i); });
    });
  }
})();
