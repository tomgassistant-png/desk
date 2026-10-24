(function(){
'use strict';
var D=window.PRAYER_DATA, $=function(s,r){return (r||document).querySelector(s)};
var app=$('#app');
function h(tag,attrs){var e=document.createElement(tag);attrs=attrs||{};for(var k in attrs){var v=attrs[k];if(k==='class')e.className=v;else if(k==='text')e.textContent=v;else if(k.indexOf('on')===0)e.addEventListener(k.slice(2),v);else if(v===true)e.setAttribute(k,'');else if(v!==false&&v!=null)e.setAttribute(k,v)}
 function add(c){if(c==null||c===false)return;if(Array.isArray(c)){c.forEach(add)}else e.appendChild(typeof c==='object'?c:document.createTextNode(String(c)))}
 for(var i=2;i<arguments.length;i++)add(arguments[i]);return e}
/* ---------- storage ---------- */
var store={
 get:function(k,d){try{var v=localStorage.getItem('vl.'+k);return v==null?d:JSON.parse(v)}catch(e){return d}},
 set:function(k,v){try{localStorage.setItem('vl.'+k,JSON.stringify(v))}catch(e){}}
};
function dkey(d){d=d||new Date();return d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0')}
function dayIndex(){var d=new Date();return Math.floor(Date.UTC(d.getFullYear(),d.getMonth(),d.getDate())/864e5)}
function streak(){var days=store.get('days',[]),set={};days.forEach(function(x){set[x]=1});var d=new Date(),n=0;if(!set[dkey(d)])d.setDate(d.getDate()-1);while(set[dkey(d)]){n++;d.setDate(d.getDate()-1)}return n}
function logDone(mins,id){var days=store.get('days',[]),t=dkey();if(days.indexOf(t)<0)days.push(t);store.set('days',days.slice(-800));store.set('minutes',(store.get('minutes',0)||0)+mins);store.set('sessions',(store.get('sessions',0)||0)+1);if(id){var ds=store.get('doneIds',{});ds[id]=dkey();store.set('doneIds',ds)}}
function favs(){return store.get('fav',[])}
function isFav(id){return favs().indexOf(id)>=0}
function toggleFav(id){var f=favs(),i=f.indexOf(id);if(i>=0)f.splice(i,1);else f.push(id);store.set('fav',f)}
/* ---------- data helpers ---------- */
var byId={};D.sessions.forEach(function(s){byId[s.id]=s});
var catName={};D.cats.forEach(function(c){catName[c.id]=c.name});
function hash(s){var x=0;for(var i=0;i<s.length;i++)x=(x*31+s.charCodeAt(i))>>>0;return x}
function closingFor(id){return D.closings[hash(id)%D.closings.length]}
function dailySession(){var pool=D.sessions.filter(function(s){return !s.night});return pool[dayIndex()%pool.length]}
function votd(){return D.votd[dayIndex()%D.votd.length]}
function passText(p){return p.verses.map(function(v){return v.t}).join(' ')}
function ordinalSum(t){var n=0;t.toUpperCase().replace(/[A-Z]/g,function(c){n+=c.charCodeAt(0)-64});return n}
function droot(n){while(n>9)n=String(n).split('').reduce(function(a,b){return a+ +b},0);return n}
function stagesFor(s,closing){
 var st=[{id:'read',label:'Scripture',passages:s.read,conf:s.conf},{id:'med',label:'Meditation',paras:s.med},{id:'prayer',label:'Prayer',paras:s.prayer},{id:'close',label:'Closing',paras:[closing.text],passages:[closing.read]}];return st}
/* ---------- audio ---------- */
var ac=null;
function audio(){if(!ac){var C=window.AudioContext||window.webkitAudioContext;if(C)ac=new C()}if(ac&&ac.state==='suspended')ac.resume();return ac}
function bell(vol){var a=audio();if(!a)return;vol=vol||0.5;var t=a.currentTime,base=392,parts=[[1,1],[2.01,.5],[2.76,.35],[5.4,.15]];
 parts.forEach(function(p){var o=a.createOscillator(),g=a.createGain();o.type='sine';o.frequency.value=base*p[0];g.gain.setValueAtTime(0,t);g.gain.linearRampToValueAtTime(vol*p[1]*.4,t+.01);g.gain.exponentialRampToValueAtTime(.0001,t+(p[0]>2?3.2:7));o.connect(g);g.connect(a.destination);o.start(t);o.stop(t+7.5)})}
/* ---------- speech ---------- */
var tts={on:false,q:[],i:0,paused:false};
var synth=window.speechSynthesis;
function voices(){return synth?synth.getVoices().filter(function(v){return /^en/i.test(v.lang)}):[]}
function speakQueue(items,onItem,onEnd){
 if(!synth)return;stopSpeech();tts.on=true;tts.q=items;tts.i=0;tts.paused=false;
 (function next(){if(!tts.on)return;if(tts.i>=tts.q.length){tts.on=false;onEnd&&onEnd();return}
  var it=tts.q[tts.i];onItem&&onItem(it,tts.i);var u=new SpeechSynthesisUtterance(it.text);var vn=store.get('voice',''),vs=voices();for(var k=0;k<vs.length;k++)if(vs[k].name===vn)u.voice=vs[k];
  u.rate=store.get('rate',0.9);u.pitch=0.95;u.lang='en-US';u.onend=function(){if(!tts.on||tts.paused)return;tts.i++;setTimeout(next,tts.q[tts.i-1].pause||500)};u.onerror=function(e){if(e&&(e.error==='canceled'||e.error==='interrupted'))return;tts.on=false;onEnd&&onEnd()};synth.speak(u)})()}
function stopSpeech(){tts.on=false;tts.paused=false;if(synth)synth.cancel()}
/* ---------- chrome ---------- */
function applyNight(){document.body.classList.toggle('night',!!store.get('night',false));var b=$('#nightBtn');if(b){b.setAttribute('aria-pressed',String(!!store.get('night',false)));b.textContent=store.get('night',false)?'Night: on':'Night'}var m=document.querySelector('meta[name=theme-color]');if(m)m.content=store.get('night',false)?'#050609':'#0a0b10'}
function setNav(route){document.querySelectorAll('nav.main a').forEach(function(a){var r=a.getAttribute('data-r');if(r===route)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current')})}
/* ---------- views ---------- */
function sessionCard(s){
 var c=h('a',{class:'scard',href:'#/session/'+s.id},h('span',{class:'eyebrow',text:catName[s.cat]}),h('span',{class:'t',text:s.title}),h('span',{class:'m',text:s.min+' min · '+s.read.map(function(p){return p.ref}).join(', ')}));
 var f=h('button',{class:'fav'+(isFav(s.id)?' on':''),'aria-label':'Favorite '+s.title,'aria-pressed':String(isFav(s.id)),text:isFav(s.id)?'★':'☆',onclick:function(e){e.preventDefault();e.stopPropagation();toggleFav(s.id);f.className='fav'+(isFav(s.id)?' on':'');f.textContent=isFav(s.id)?'★':'☆';f.setAttribute('aria-pressed',String(isFav(s.id)))}});
 c.appendChild(f);return c}
function numNote(p){
 if(store.get('nums',true)===false)return null;
 var t=passText(p),sum=ordinalSum(t),r=droot(sum);
 return h('div',{class:'numnote'},h('b',{text:'Number note · speculative'}),h('div',{text:'Simple English letter values (A=1 to Z=26) add up to '+sum+' for these words, with a digital root of '+r+'. This is a contemplative curiosity and carries no weight as teaching. The letter values belong to the English text, not to the original Hebrew or Greek.'}))}
function passageEl(p,big){return h('div',{class:'passage'},h('div',{class:'ref',text:p.ref+' · King James Version'}),h('p',{class:'verse'},p.verses.map(function(v){return [h('sup',{text:String(v.n)}),v.t+' ']})))}
function homeView(){
 var s=dailySession(),v=votd(),closing=D.closings[dayIndex()%D.closings.length];
 var hour=new Date().getHours(),night=(hour>=20||hour<5)?D.sessions.filter(function(x){return x.night})[dayIndex()%2]:null;
 var st=streak();
 var left=h('div',{},
  h('section',{class:'card hero'},h('p',{class:'eyebrow',text:'Today · '+new Date().toLocaleDateString(undefined,{weekday:'long',month:'long',day:'numeric'})}),h('h1',{text:s.title}),h('p',{class:'lede',style:'margin:0 auto 16px',text:catName[s.cat]+' · '+s.min+' minutes · '+s.read.map(function(p){return p.ref}).join(', ')}),
   h('div',{class:'row center'},h('a',{class:'btn',href:'#/daily'},'Begin today’s prayer'),h('a',{class:'btn ghost',href:'#/silence'},'Silent meditation'))),
  h('section',{class:'card'},h('p',{class:'eyebrow',text:'Verse of the day'}),passageEl(v),numNote(v)),
  night?h('section',{class:'card'},h('p',{class:'eyebrow',text:'For the evening'}),h('h3',{text:night.title}),h('p',{class:'muted',text:'A short prayer for the end of the day, with dimmed text.'}),h('a',{class:'btn ghost small',href:'#/session/'+night.id,onclick:function(){store.set('night',true);applyNight()}},'Begin night prayer')):null);
 var right=h('div',{},
  h('section',{class:'card'},h('div',{class:'stats'},h('div',{class:'stat'},h('b',{text:String(st)}),h('span',{text:st===1?'day streak':'day streak'})),h('div',{class:'stat'},h('b',{text:String(store.get('sessions',0)||0)}),h('span',{text:'sessions'})),h('div',{class:'stat'},h('b',{text:String(store.get('minutes',0)||0)}),h('span',{text:'minutes'}))),h('p',{class:'muted',style:'margin:12px 0 0;text-align:center',text:'Kept only on this device. No account and no tracking.'})),
  h('section',{class:'card'},h('p',{class:'eyebrow',text:'Library'}),h('div',{class:'row'},D.cats.map(function(c){return h('a',{class:'chip',href:'#/library/'+c.id,text:c.name})})),h('p',{style:'margin:14px 0 0'},h('a',{href:'#/library'},'Open the full library →'))));
 return h('div',{class:'home'},left,right)}
function libraryView(cat){
 var wrap=h('div',{},h('h1',{text:cat?catName[cat]:'Library'}),h('p',{class:'lede',text:cat?D.cats.filter(function(c){return c.id===cat})[0].desc:'Sessions in eight groups. Each has a reading, a meditation, a prayer and a closing.'}),
  h('div',{class:'row',style:'margin:10px 0 0'},h('a',{class:'chip'+(!cat?' on':''),href:'#/library',text:'All'}),D.cats.map(function(c){return h('a',{class:'chip'+(cat===c.id?' on':''),href:'#/library/'+c.id,text:c.name})})));
 D.cats.forEach(function(c){if(cat&&cat!==c.id)return;var list=D.sessions.filter(function(s){return s.cat===c.id});wrap.appendChild(h('section',{class:'cat'},cat?null:h('h2',{text:c.name}),cat?null:h('p',{text:c.desc}),h('div',{class:'grid'},list.map(sessionCard))))});
 return wrap}
function favView(){var f=favs().map(function(id){return byId[id]}).filter(Boolean);
 return h('div',{},h('h1',{text:'Favorites'}),f.length?h('div',{class:'grid'},f.map(sessionCard)):h('p',{class:'lede',text:'No favorites yet. Select the star on any session to keep it here.'}))}
function sessionView(s,daily){
 stopSpeech();
 var closing=daily?D.closings[dayIndex()%D.closings.length]:closingFor(s.id),stages=stagesFor(s,closing),cur=0,seen={};
 var body=h('div',{class:'card stage',id:'stage'}),dots=h('div',{class:'dots',role:'tablist'}),title=h('h1',{text:s.title});
 var listenBtn=h('button',{class:'btn ghost small',onclick:toggleListen},'Listen'),stopBtn=h('button',{class:'btn ghost small',onclick:function(){stopSpeech();setL('idle')}},'Stop');stopBtn.hidden=true;
 var favBtn=h('button',{class:'btn ghost small','aria-pressed':String(isFav(s.id)),onclick:function(){toggleFav(s.id);upFav()}});
 function upFav(){favBtn.textContent=isFav(s.id)?'★ Saved':'☆ Save';favBtn.setAttribute('aria-pressed',String(isFav(s.id)))}upFav();
 var prev=h('button',{class:'btn ghost',onclick:function(){go(cur-1)}},'← Back'),next=h('button',{class:'btn',onclick:function(){if(cur<stages.length-1)go(cur+1);else finish()}},'Next →');
 function setL(m){listenBtn.textContent=m==='play'?'Pause':m==='pause'?'Resume':'Listen';stopBtn.hidden=(m==='idle')}
 function go(i,fromSpeech){if(i<0||i>=stages.length)return;cur=i;seen[i]=1;if(!fromSpeech&&tts.on){stopSpeech();setL('idle')}render();window.scrollTo({top:0,behavior:'smooth'})}
 function render(){var st=stages[cur];body.className='card stage '+st.id;body.textContent='';body.appendChild(h('p',{class:'eyebrow',text:st.label+' · '+(cur+1)+' of '+stages.length}));
  if(st.passages)st.passages.forEach(function(p){body.appendChild(passageEl(p));var n=(st.id==='read')?numNote(p):null;if(n&&st.id==='read'&&p===st.passages[0])body.appendChild(n)});
  if(st.conf)body.appendChild(h('blockquote',{class:'quote'},st.conf.text,h('span',{class:'src',text:st.conf.src})));
  if(st.paras)st.paras.forEach(function(t){body.appendChild(h('p',{text:t}))});
  dots.textContent='';stages.forEach(function(x,i){dots.appendChild(h('button',{class:(i===cur?'on':seen[i]?'done':''),'aria-label':x.label,'aria-selected':String(i===cur),onclick:function(){go(i)}}))});
  prev.disabled=cur===0;prev.style.visibility=cur===0?'hidden':'visible';next.textContent=cur===stages.length-1?'Amen · Complete':'Next →'}
 function items(from){var out=[];for(var i=from;i<stages.length;i++){var st=stages[i];if(st.passages)st.passages.forEach(function(p){out.push({stage:i,text:p.ref+'. '+p.verses.map(function(v){return v.t}).join(' '),pause:900})});if(st.conf&&i===0)out.push({stage:i,text:st.conf.text+' '+st.conf.src,pause:900});if(st.paras)st.paras.forEach(function(t){out.push({stage:i,text:t,pause:900})})}return out}
 function toggleListen(){if(!synth){alert('Speech is not available in this browser.');return}
  if(tts.on&&!tts.paused){tts.paused=true;synth.pause();setL('pause');return}
  if(tts.on&&tts.paused){tts.paused=false;synth.resume();setL('play');return}
  setL('play');speakQueue(items(cur),function(it){if(it.stage!==cur)go(it.stage,true)},function(){setL('idle')})}
 function finish(){stopSpeech();logDone(s.min,s.id);bell(.35);var st=streak();app.textContent='';app.appendChild(h('div',{class:'card hero'},h('p',{class:'eyebrow',text:'Amen'}),h('h1',{text:'Session complete'}),h('p',{class:'lede',style:'margin:0 auto 14px',text:'Current streak: '+st+(st===1?' day.':' days.')}),h('div',{class:'row center'},h('a',{class:'btn',href:'#/'},'Return home'),h('a',{class:'btn ghost',href:'#/silence'},'Sit in silence'),h('a',{class:'btn ghost',href:'#/library'},'Library'))))}
 var rate=h('select',{'aria-label':'Speech speed',onchange:function(e){store.set('rate',parseFloat(e.target.value))}},[['0.75','Slow'],['0.9','Calm'],['1','Normal'],['1.15','Brisk']].map(function(o){return h('option',{value:o[0],selected:parseFloat(o[0])===store.get('rate',0.9)},o[1])}));
 var vsel=h('select',{'aria-label':'Voice',onchange:function(e){store.set('voice',e.target.value)}});
 function fillV(){var vs=voices();vsel.textContent='';vsel.appendChild(h('option',{value:'',text:'Default voice'}));vs.forEach(function(v){vsel.appendChild(h('option',{value:v.name,selected:v.name===store.get('voice',''),text:v.name}))});vsel.hidden=vs.length===0}
 if(synth){fillV();synth.onvoiceschanged=fillV}
 render();
 return h('div',{class:'reader'},h('p',{class:'crumb'},h('a',{href:daily?'#/':'#/library/'+s.cat},'← '+(daily?'Home':catName[s.cat]))),h('p',{class:'eyebrow',text:(daily?'Today · ':'')+catName[s.cat]+' · '+s.min+' min'}),title,
  h('div',{class:'row',style:'margin:0 0 16px'},listenBtn,stopBtn,favBtn,synth?rate:null,synth?vsel:null),dots,body,h('div',{class:'row',style:'justify-content:space-between;margin-top:6px'},prev,next))}
/* silence */
var timer=null;
function silenceView(){
 if(timer){clearInterval(timer.iv);timer=null}
 var dur=store.get('sdur',10),breathe=store.get('breath',true),remain,end,running=false,paused=false,wl=null,phase='';
 var clock=h('div',{class:'clock','aria-live':'off',text:'10:00'}),orb=h('div',{class:'orb','aria-hidden':'true'},h('span',{text:'Be still'})),status=h('p',{class:'muted',style:'min-height:1.6em',text:'Choose a length, then begin.'});
 var chipsEl=h('div',{class:'chips'}),startBtn=h('button',{class:'btn',onclick:start,text:'Begin'}),resetBtn=h('button',{class:'btn ghost',onclick:reset,text:'Reset'});resetBtn.hidden=true;
 function fmt(ms){var s=Math.max(0,Math.ceil(ms/1000));return String(Math.floor(s/60)).padStart(2,'0')+':'+String(s%60).padStart(2,'0')}
 function chips(){chipsEl.textContent='';[3,5,10,15,20,30].forEach(function(m){chipsEl.appendChild(h('button',{class:'chip'+(m===dur?' on':''),disabled:running,onclick:function(){dur=m;store.set('sdur',m);clock.textContent=fmt(m*60000);chips()},text:m+' min'}))})}
 function tick(){var now=Date.now();if(paused)return;remain=end-now;clock.textContent=fmt(remain);
  if(breathe){var cyc=(dur*60000-remain)%10000;var p=cyc<4000?'in':'out';if(p!==phase){phase=p;orb.className='orb '+p;orb.firstChild.textContent=p==='in'?'Breathe in':'Breathe out'}}
  if(remain<=0){done()}}
 function start(){audio();if(!running){running=true;paused=false;end=Date.now()+dur*60000;bell(.5);status.textContent='Silence has begun.';if(navigator.wakeLock&&navigator.wakeLock.request)navigator.wakeLock.request('screen').then(function(l){wl=l}).catch(function(){});
   timer={iv:setInterval(tick,250)};startBtn.textContent='Pause';resetBtn.hidden=false;chips();if(!breathe){orb.className='orb';}else{phase='';orb.className='orb'}tick()}
  else if(!paused){paused=true;remain=end-Date.now();startBtn.textContent='Resume';status.textContent='Paused.'}
  else{paused=false;end=Date.now()+remain;startBtn.textContent='Pause';status.textContent='Silence has begun.'}}
 function stopAll(){if(timer){clearInterval(timer.iv);timer=null}running=false;paused=false;if(wl){try{wl.release()}catch(e){}wl=null}orb.className='orb'}
 function reset(){stopAll();clock.textContent=fmt(dur*60000);startBtn.textContent='Begin';resetBtn.hidden=true;status.textContent='Choose a length, then begin.';orb.firstChild.textContent='Be still';chips()}
 function done(){stopAll();bell(.6);setTimeout(function(){bell(.35)},4200);logDone(dur,null);clock.textContent='00:00';status.textContent='The time is complete. Streak: '+streak()+(streak()===1?' day.':' days.');startBtn.textContent='Begin again';resetBtn.hidden=true;orb.firstChild.textContent='Amen';chips()}
 var sw=h('label',{class:'switch'},h('input',{type:'checkbox',checked:breathe,onchange:function(e){breathe=e.target.checked;store.set('breath',breathe);orb.style.visibility=breathe?'visible':'hidden'}}),'Breathing guide (4 seconds in, 6 seconds out)');
 orb.style.visibility=breathe?'visible':'hidden';chips();clock.textContent=fmt(dur*60000);
 return h('div',{class:'timer'},h('h1',{text:'Silent meditation'}),h('p',{class:'lede',style:'margin:0 auto',text:'A bell sounds at the beginning and at the end. Keep this screen open. Sound is made on your device with no files loaded.'}),chipsEl,orb,clock,status,h('div',{class:'row center'},startBtn,resetBtn),h('p',{style:'margin-top:16px'},sw),h('p',{class:'muted',style:'max-width:56ch;margin:14px auto'},'Suggested practice: read one verse, close the eyes, and return to the words “Be still, and know that I am God” (Psalm 46:10) whenever the mind wanders.'),h('div',{class:'row center'},h('button',{class:'btn ghost small',onclick:function(){bell(.5)},text:'Test the bell'})))}
function sourcesView(){
 var li=function(a,b){return h('li',{},a,b?h('span',{class:'muted',text:' '+b}):null)};
 return h('div',{class:'reader'},h('h1',{text:'Texts and sources'}),h('p',{class:'lede',text:'All scripture and quoted texts in this app are in the public domain. The meditations, prayers and closings are original writing for this app.'}),
  h('ul',{},li('The Holy Bible, King James Version (1611, text as in the standard 1769 edition). ','Digital text from Project Gutenberg, ebook 10.'),li('Westminster Confession of Faith, chapter 3 (Westminster Assembly, 1640s). ','Quoted from the standard public-domain text.'),li('Westminster Shorter Catechism, questions 1 and 20 (Westminster Assembly, 1640s).'),li('Heidelberg Catechism, question 1 (1563), in the older public-domain English translation.'),li('John Calvin, Institutes of the Christian Religion, 1.1.1, translated by Henry Beveridge (1845).')),
  h('h2',{text:'Settings'}),
  h('p',{},h('label',{class:'switch'},h('input',{type:'checkbox',checked:store.get('nums',true)!==false,onchange:function(e){store.set('nums',e.target.checked)}}),'Show the optional number notes (speculative)')),
  h('p',{},h('label',{class:'switch'},h('input',{type:'checkbox',checked:!!store.get('night',false),onchange:function(e){store.set('night',e.target.checked);applyNight()}}),'Night mode (dimmed text)')),
  h('p',{},h('button',{class:'btn ghost small',onclick:function(){if(confirm('Erase streak, favorites and settings stored on this device?')){['days','minutes','sessions','doneIds','fav','night','nums','rate','voice','sdur','breath'].forEach(function(k){try{localStorage.removeItem('vl.'+k)}catch(e){}});applyNight();route()}}},'Erase data on this device')),
  h('p',{class:'muted',text:'Everything is stored in this browser only. Nothing is sent to a server, and there are no accounts, cookies or trackers.'}))}
/* ---------- router ---------- */
var titles={'':'Veil and Light: Gnostic Calvinist Prayer and Meditation'};
function route(){
 var hs=(location.hash||'#/').replace(/^#\/?/,''),p=hs.split('/');var r=p[0]||'';
 if(r!=='silence'&&timer){clearInterval(timer.iv);timer=null}
 if(r!=='session'&&r!=='daily')stopSpeech();
 app.textContent='';var v,nav=r;
 if(r==='library'){v=libraryView(p[1]&&catName[p[1]]?p[1]:null)}
 else if(r==='session'&&byId[p[1]]){v=sessionView(byId[p[1]],false);nav='library'}
 else if(r==='daily'){v=sessionView(dailySession(),true);nav=''}
 else if(r==='silence'){v=silenceView()}
 else if(r==='favorites'){v=favView()}
 else if(r==='sources'){v=sourcesView()}
 else{v=homeView();nav=''}
 app.appendChild(v);setNav(nav);window.scrollTo(0,0);
 var sess=(r==='session'&&byId[p[1]])?byId[p[1]].title:null;document.title=(sess?sess+' · ':(r&&{library:'Library · ',silence:'Silent meditation · ',favorites:'Favorites · ',sources:'Texts and sources · ',daily:'Today · '}[r])||'')+titles['']}
$('#nightBtn').addEventListener('click',function(){store.set('night',!store.get('night',false));applyNight()});
window.addEventListener('hashchange',route);
applyNight();route();
})();
