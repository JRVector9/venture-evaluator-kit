/* Optional, local-only interactions. The report is fully readable without JavaScript. */
(()=>{'use strict';
 document.documentElement.classList.add('js');
 const table=document.querySelector('.scorecard');
 document.querySelectorAll('[data-rating-view]').forEach(button=>button.addEventListener('click',()=>{
  const view=button.dataset.ratingView;
  if(table)table.dataset.view=view;
  document.querySelectorAll('[data-rating-view]').forEach(b=>b.setAttribute('aria-pressed',String(b===button)));
  const status=document.getElementById('rating-status');
  if(status)status.textContent=view==='current'?'현재 판정만 표시합니다.':'현재 판정과 조건부 개선 가능성을 함께 표시합니다.';
 }));
 const details=Array.from(document.querySelectorAll('details'));
 const expand=document.getElementById('expand-details');
 if(expand)expand.addEventListener('click',()=>{
  const open=details.some(d=>!d.open);details.forEach(d=>d.open=open);
  expand.textContent=open?'상세 근거 접기':'상세 근거 모두 보기';
  expand.setAttribute('aria-expanded',String(open));
 });
 const links=Array.from(document.querySelectorAll('.toc a'));
 const sections=links.map(a=>document.querySelector(a.getAttribute('href'))).filter(Boolean);
 let ticking=false;
 function onScroll(){
  let active=sections[0];for(const s of sections){if(s.getBoundingClientRect().top<=140)active=s;}
  links.forEach(a=>{const selected=active&&a.getAttribute('href')==='#'+active.id;a.classList.toggle('active',selected);if(selected)a.setAttribute('aria-current','location');else a.removeAttribute('aria-current');});
  const max=document.documentElement.scrollHeight-window.innerHeight;
  const progress=document.querySelector('.progress-line');if(progress)progress.style.width=(max>0?Math.min(100,window.scrollY/max*100):100)+'%';
  ticking=false;
 }
 window.addEventListener('scroll',()=>{if(!ticking){requestAnimationFrame(onScroll);ticking=true;}},{passive:true});onScroll();
 let detailState=null;
 function preparePrint(){if(detailState!==null)return;detailState=details.map(d=>d.open);details.forEach(d=>d.open=true);}
 function restorePrint(){if(detailState===null)return;details.forEach((d,i)=>d.open=detailState[i]);detailState=null;}
 window.addEventListener('beforeprint',preparePrint);window.addEventListener('afterprint',restorePrint);
 document.getElementById('print-report')?.addEventListener('click',()=>{preparePrint();window.print();});
 // A source/criterion link never needs network access. Open local collapsed ancestors when necessary.
 function revealHash(){let target;try{target=document.querySelector(window.location.hash);}catch{return;}if(target){let el=target.parentElement;while(el){if(el.tagName==='DETAILS')el.open=true;el=el.parentElement;}}}
 window.addEventListener('hashchange',revealHash);if(window.location.hash)revealHash();
})();
