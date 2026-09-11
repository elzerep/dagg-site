(function(){
  "use strict";
  document.documentElement.setAttribute("data-enhanced","true");
  var reduce=window.matchMedia("(prefers-reduced-motion: reduce)");
  function ready(fn){document.readyState==="loading"?document.addEventListener("DOMContentLoaded",fn,{once:true}):fn()}
  function initDisclosure(){
    var root=document.querySelector("[data-disclosure]");if(!root)return;
    var summary=root.querySelector("[data-summary]");var menu=root.querySelector("[data-label-menu]");var close=root.querySelector("[data-label-close]");
    function sync(){var open=root.open;summary.setAttribute("aria-expanded",open?"true":"false");menu.hidden=open;close.hidden=!open;document.body.toggleAttribute("data-menu-open",open)}
    root.addEventListener("toggle",sync);document.addEventListener("keydown",function(e){if(e.key==="Escape"&&root.open){root.open=false;summary.focus()}});sync();
  }
  function initFlyout(){
    var root=document.querySelector("[data-flyout]");if(!root)return;
    var trigger=root.querySelector("summary");var openTimer=0;var closeTimer=0;
    function open(){clearTimeout(closeTimer);openTimer=setTimeout(function(){root.open=true;trigger.setAttribute("aria-expanded","true")},80)}
    function close(){clearTimeout(openTimer);closeTimer=setTimeout(function(){root.open=false;trigger.setAttribute("aria-expanded","false")},200)}
    root.addEventListener("mouseenter",open);root.addEventListener("mouseleave",close);root.addEventListener("focusin",function(){clearTimeout(closeTimer)});root.addEventListener("focusout",function(e){if(!root.contains(e.relatedTarget))close()});
    root.addEventListener("keydown",function(e){if(e.key==="Escape"){root.open=false;trigger.setAttribute("aria-expanded","false");trigger.focus()}})
  }
  function initSignals(){document.querySelectorAll("[data-signal]").forEach(function(root){
    var steps=Array.prototype.slice.call(root.querySelectorAll(".signal__step"));if(!steps.length)return;
    function show(index){steps.forEach(function(step,i){step.toggleAttribute("data-resolved",i<=index);step.toggleAttribute("data-active",i===index)})}
    /* Two 420 ms transitions resolve inside 840 ms: one finite causal
       response, below the threshold that would require pause/replay. */
    if(reduce.matches){show(steps.length-1);return}show(0);var i=0;var timer=setInterval(function(){i+=1;show(i);if(i>=steps.length-1)clearInterval(timer)},420)
  })}
  function initProofs(){document.querySelectorAll("[data-proof]").forEach(function(root){
    var tabs=Array.prototype.slice.call(root.querySelectorAll("[data-proof-tab]"));var panels=Array.prototype.slice.call(root.querySelectorAll("[data-proof-panel]"));if(!tabs.length||tabs.length!==panels.length)return;
    function select(index,focus){tabs.forEach(function(tab,i){var on=i===index;tab.setAttribute("role","tab");tab.setAttribute("aria-selected",on?"true":"false");tab.tabIndex=on?0:-1;panels[i].setAttribute("role","tabpanel");panels[i].hidden=!on});if(focus)tabs[index].focus()}
    root.querySelector("[data-proof-tabs]").setAttribute("role","tablist");tabs.forEach(function(tab,i){tab.addEventListener("click",function(){select(i,false)});tab.addEventListener("keydown",function(e){var n=null;if(e.key==="ArrowRight"||e.key==="ArrowDown")n=(i+1)%tabs.length;if(e.key==="ArrowLeft"||e.key==="ArrowUp")n=(i-1+tabs.length)%tabs.length;if(e.key==="Home")n=0;if(e.key==="End")n=tabs.length-1;if(n!==null){e.preventDefault();select(n,true)}})});select(0,false)
  })}
  function initProductStages(){
    var buttons=Array.prototype.slice.call(document.querySelectorAll("[data-product-stage]"));var panel=document.querySelector("[data-product-panel]");if(!buttons.length||!panel)return;
    var states=[
      ["The workflow becomes legible.","Sources, owners, exceptions and handoffs resolve into one company-specific record.",["4 connected","Finance operations","Strategic decision"]],
      ["The future path becomes explicit.","Dagg decides what to preserve, automate, rebuild or retire before engineering begins.",["5 outcomes","Accountable owner","Factory requirement"]],
      ["The decision becomes a working system.","Dagg Factory turns the approved requirement, context and boundaries into agents and software.",["3 evaluations","Source-linked","Verified release"]],
      ["The result strengthens the next run.","Evidence, exceptions and outcomes return to the same company context instead of disappearing at handoff.",["Full trail","Boundary retained","Context updated"]]
    ];
    function select(i){buttons.forEach(function(b,n){b.classList.toggle("is-active",n===i);b.setAttribute("aria-pressed",n===i?"true":"false")});var s=states[i];panel.querySelector(".h3").textContent=s[0];panel.querySelector(".body").textContent=s[1];panel.querySelectorAll("dd").forEach(function(dd,n){dd.textContent=s[2][n]})}
    buttons.forEach(function(b,i){b.addEventListener("click",function(){select(i)})});select(0)
  }
  ready(function(){initDisclosure();initFlyout();initSignals();initProofs();initProductStages()})
})();
