/* Motion, held to what the reference tier actually does:
   opacity-first, 8px of travel, one gesture, fired once, above the fold.
   Nothing reveals on scroll. Argument pages at this tier animate nothing,
   and a page that moves as you read it reads as marketing. */
(function(){
  var d=document, root=d.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* the single entrance: the first section only, on load */
  if(!reduce){
    root.setAttribute('data-anim','on');
    var first = d.querySelector('.s-open');
    if(first){
      first.querySelectorAll('.rv').forEach(function(el,i){
        el.style.setProperty('--i', Math.min(i,4));
      });
      requestAnimationFrame(function(){
        requestAnimationFrame(function(){ first.classList.add('in'); });
      });
    }
  }

  /* the nav must not vanish on a phone */
  var tg = d.querySelector('.nav__toggle'), lk = d.getElementById('navlinks');
  if(tg && lk){
    tg.addEventListener('click', function(){
      var open = lk.classList.toggle('open');
      tg.setAttribute('aria-expanded', open ? 'true' : 'false');
      tg.textContent = open ? 'Close' : 'Menu';
    });
  }

  /* progress: the one deck device that is more useful on a page than it was
     in the deck — it reports position, it does not decorate */
  var bar = d.querySelector('.progress');
  if(bar){
    var tick=function(){
      var h = d.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h>0 ? Math.min(window.scrollY/h,1)*100 : 0) + '%';
    };
    window.addEventListener('scroll', tick, {passive:true});
    window.addEventListener('resize', tick); tick();
  }

  /* the three states of one record. It does not cycle on its own — an
     auto-advancing diagram is a carousel, and a carousel is marketing.
     The reader drives it; all three are legible without touching it. */
  var lives = d.querySelector('[data-lives]');
  if(lives){
    var states = lives.querySelectorAll('[data-state]');
    var items  = d.querySelectorAll('[data-life]');
    var show = function(n){
      states.forEach(function(s,i){ s.classList.toggle('on', i===n); });
      items.forEach(function(l,i){ l.classList.toggle('on', i===n); });
    };
    show(0);
    items.forEach(function(l,i){
      l.setAttribute('tabindex','0');
      l.addEventListener('mouseenter', function(){ show(i); });
      l.addEventListener('focus',      function(){ show(i); });
    });
  }
})();
