/* Reveal, progress, and one diagram that cycles.
   Nothing animates that does not say something true about the content. */
(function(){
  var d=document, root=d.documentElement;
  root.setAttribute('data-anim','on');           /* no JS → nothing hidden */

  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* index the reveals inside each section so the stagger is real, not nth-child luck */
  d.querySelectorAll('.sec').forEach(function(s){
    s.querySelectorAll('.rv').forEach(function(el,i){
      el.style.setProperty('--i', Math.min(i,4));
    });
  });

  var io = new IntersectionObserver(function(es){
    es.forEach(function(e){ if(e.isIntersecting){ e.target.classList.add('in'); io.unobserve(e.target); } });
  }, {threshold:.15, rootMargin:'0px 0px -12% 0px'});
  d.querySelectorAll('.sec').forEach(function(s){ io.observe(s); });

  /* progress: the deck device that is more useful on a page than it was in the deck */
  var bar = d.querySelector('.progress');
  if(bar){
    var tick=function(){
      var h = d.documentElement.scrollHeight - window.innerHeight;
      bar.style.width = (h>0 ? (window.scrollY/h)*100 : 0) + '%';
    };
    window.addEventListener('scroll', tick, {passive:true});
    window.addEventListener('resize', tick); tick();
  }

  /* the three states of one record. The graph never changes; only what is
     attached to it does. That is the argument, so it is what moves. */
  var lives = d.querySelector('[data-lives]');
  if(lives){
    var states = lives.querySelectorAll('[data-state]');
    var labels = d.querySelectorAll('[data-life]');
    var k = 0, timer = null;
    var show = function(n){
      states.forEach(function(s,i){ s.classList.toggle('on', i===n); });
      labels.forEach(function(l,i){ l.classList.toggle('on', i===n); });
    };
    var start = function(){
      if(reduce){ states.forEach(function(s){ s.classList.add('on'); });
                  labels.forEach(function(l){ l.classList.add('on'); }); return; }
      show(0);
      timer = setInterval(function(){ k=(k+1)%3; show(k); }, 2600);
    };
    var lio = new IntersectionObserver(function(es){
      es.forEach(function(e){
        if(e.isIntersecting && !timer){ start(); }
        else if(!e.isIntersecting && timer){ clearInterval(timer); timer=null; }
      });
    },{threshold:.3});
    lio.observe(lives);

    labels.forEach(function(l,i){
      l.addEventListener('mouseenter',function(){
        if(reduce) return;
        if(timer){ clearInterval(timer); timer=null; }
        k=i; show(i);
      });
    });
  }
})();
