/* Map and Text drive modes (HUD v9).
   A simplified drive of the whole Universe deck: Tallinn–Tartu, 186 km at a steady 90 km/h,
   narration at 14 characters a second. Not the trip simulator's real drive or playback rules:
   this is for judging how the two modes look and behave.
   Uses globals from index.html: $, V, playing, mode, SCENES, setTitleText, fitTitle. */
(()=>{
const KM=186, KMH=90, CPS=14, AGE=13.799e9;
const EV=DECK.map((d,i)=>({i,p:d[0],h:d[1].replace(/\.$/,''),d:d[2],t:d[3],n:d[4]}));
EV.forEach((e,i)=>{const nx=EV[i+1];e.zE=nx?e.p+.6*(nx.p-e.p):2;e.secs=e.n/CPS;});
const PICS={60:'img/dino.jpg?v=4',64:'img/earth.jpg?v=4'};

/* ---------- card texts: never in the repo; loaded on the device ---------- */
let TEXTS={};
try{TEXTS=JSON.parse(localStorage.getItem('tm-hud-texts')||'{}');}catch(e){}
const builtIn={60:SCENES.dino.text,64:SCENES.earth.text};
const textOf=i=>TEXTS[i]||builtIn[i]||null;

/* ---------- trip state ---------- */
const T={p:EV[60].p+.0004,cam:'follow'};
try{const s=localStorage.getItem('tm-hud-trip');if(s!==null&&+s>=0&&+s<1)T.p=+s;}catch(e){}
const fired=p=>{let k=-1;for(const e of EV){if(e.p<=p+1e-12)k=e.i;else break;}return k;};
const narr=(i,p)=>Math.max(0,Math.min(1,(p-EV[i].p)*KM/KMH*3600/EV[i].secs));
// H-2: the event stays while its picture zone lasts or its narration plays; a newly fired event always takes over
const activeOf=p=>{const k=fired(p);if(k<0)return -1;return (p<EV[k].zE||narr(k,p)<1)?k:-1;};
const fmtAge=p=>{const y=AGE*(1-p);if(p>=1)return 'Today';if(y>=1e9)return (y/1e9).toFixed(2)+' Ga';if(y>=1e6)return (y/1e6).toFixed(y>=1e8?0:1)+' Ma';if(y>=1e3)return (y/1e3).toFixed(0)+' ka';return Math.round(y)+' years';};
const esc=s=>String(s).replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

/* ---------- route: the real road's shape, scaled to 186 km ---------- */
const LL=[[59.433,24.745,'Tallinn',3],[59.418,24.80],[59.37,24.885],[59.29,24.967,'Vaida',1],[59.186,25.162,'Kose',2],[59.084,25.34,'Ardu',1],[58.99,25.5],[58.906,25.64,'Mäo',2],[58.80,25.785],[58.712,25.913,'Adavere',1],[58.656,26.0,'Põltsamaa',2],[58.60,26.16],[58.567,26.29,'Puurmani',1],[58.50,26.40],[58.423,26.489,'Kärevere',1],[58.40,26.60],[58.38,26.722,'Tartu',3]];
const pj=(la,lo)=>[(lo-24.745)*57.6,(59.433-la)*111.2];
let raw=[];const CP=LL.map(a=>pj(a[0],a[1]));
for(let i=0;i<CP.length-1;i++){const p0=CP[i-1]||CP[i],p1=CP[i],p2=CP[i+1],p3=CP[i+2]||CP[i+1];
 for(let s=0;s<24;s++){const t=s/24,t2=t*t,t3=t2*t;raw.push([0,1].map(k=>.5*(2*p1[k]+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t2+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t3)));}}
raw.push(CP[CP.length-1]);
{let s=0;const out=[];for(let i=0;i<raw.length;i++){if(i)s+=Math.hypot(raw[i][0]-raw[i-1][0],raw[i][1]-raw[i-1][1]);
 const a=raw[Math.max(0,i-1)],b=raw[Math.min(raw.length-1,i+1)],dx=b[0]-a[0],dy=b[1]-a[1],l=Math.hypot(dx,dy)||1;
 const w=(.28*Math.sin(s/2.1)+.16*Math.sin(s/.83+1.3))*Math.min(1,s/3);out.push([raw[i][0]-dy/l*w,raw[i][1]+dx/l*w]);}raw=out;}
const cum=[0];for(let i=1;i<raw.length;i++)cum.push(cum[i-1]+Math.hypot(raw[i][0]-raw[i-1][0],raw[i][1]-raw[i-1][1]));
const SC=KM/cum[cum.length-1],N=3600,R=[];
{let j=0;for(let n=0;n<N;n++){const s=n/(N-1)*cum[cum.length-1];while(j<cum.length-2&&cum[j+1]<s)j++;const t=(s-cum[j])/((cum[j+1]-cum[j])||1);
 R.push([(raw[j][0]+(raw[j+1][0]-raw[j][0])*t)*SC,(raw[j][1]+(raw[j+1][1]-raw[j][1])*t)*SC]);}}
const at=p=>{p=Math.max(0,Math.min(1,p));const f=p*(N-1),i=Math.min(N-2,Math.floor(f)),t=f-i;return [R[i][0]+(R[i+1][0]-R[i][0])*t,R[i][1]+(R[i+1][1]-R[i][1])*t];};
const W2=(la,lo)=>{const q=pj(la,lo);return [q[0]*SC,q[1]*SC];};
const TOWNS=LL.filter(a=>a[2]).map(a=>({n:a[2],r:a[3],w:W2(a[0],a[1])}));
[['Paide',58.886,25.557],['Rapla',59.0,24.79],['Jõgeva',58.746,26.394]].forEach(([n,a,b])=>TOWNS.push({n,r:2,w:W2(a,b),off:1}));
let seed=7;const rnd=()=>(seed=(seed*16807)%2147483647)/2147483647;
const ROADS=[];const wig=(x,y,a,len)=>{const pts=[[x,y]];for(let k=0;k<14;k++){a+=(rnd()-.5)*.5;x+=Math.cos(a)*len/14;y+=Math.sin(a)*len/14;pts.push([x,y]);}return pts;};
TOWNS.forEach(t=>{for(let k=0;k<(t.r>=2?4:2);k++)ROADS.push(wig(t.w[0],t.w[1],rnd()*6.28,10+rnd()*28));});
for(let k=0;k<70;k++)ROADS.push(wig(-30+rnd()*190,-10+rnd()*150,rnd()*6.28,6+rnd()*22));
const LAKES=[{c:W2(58.30,26.03),rx:6,ry:17,a:.35},{c:W2(58.75,27.45),rx:28,ry:55,a:.15},{c:W2(59.05,25.85),rx:1.6,ry:1.1,a:0},{c:W2(58.66,25.55),rx:1.2,ry:2,a:.5}];
const RIVER=[W2(58.33,26.13),W2(58.37,26.25),W2(58.405,26.42),W2(58.39,26.6),W2(58.383,26.72),W2(58.395,26.9),W2(58.42,27.15)];
const COAST=[];for(let x=-60;x<=220;x+=3)COAST.push([x,-2.5*SC-1.2*Math.sin(x/6)-.8*Math.sin(x/2.3)+(x>40?-(x-40)*.06:0)]);
// whole-road orientation: start upper left, finish lower right (a loop uses its longest dimension instead)
const AXIS=(()=>{const a=R[0],b=R[N-1];let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;R.forEach(q=>{x0=Math.min(x0,q[0]);y0=Math.min(y0,q[1]);x1=Math.max(x1,q[0]);y1=Math.max(y1,q[1]);});
 if(Math.hypot(b[0]-a[0],b[1]-a[1])>.25*Math.hypot(x1-x0,y1-y0))return Math.atan2(b[1]-a[1],b[0]-a[0]);
 let mx=0,my=0;R.forEach(q=>{mx+=q[0];my+=q[1];});mx/=N;my/=N;let sxx=0,syy=0,sxy=0;R.forEach(q=>{const dx=q[0]-mx,dy=q[1]-my;sxx+=dx*dx;syy+=dy*dy;sxy+=dx*dy;});
 return .5*Math.atan2(2*sxy,sxx-syy);})();

/* ---------- map canvas and camera ---------- */
const mc=$('mapc'),mx=mc.getContext('2d');let W=390,H=844,dpr=1;
function size(){dpr=Math.min(2,devicePixelRatio||1);W=mc.clientWidth||390;H=mc.clientHeight||844;mc.width=Math.round(W*dpr);mc.height=Math.round(H*dpr);}
const box=()=>{const s=$('stage').getBoundingClientRect(),h=$('hud').getBoundingClientRect(),d=$('dock').getBoundingClientRect();return {top:h.bottom-s.top,bot:d.top-s.top};};
const cam={x:0,y:0,s:30,r:0,ax:195,ay:500};let camInit=false,free=null,lastTouch=0,northUp=false;
function rotOf(dx,dy,r){const c=Math.cos(r),s=Math.sin(r);return [dx*c-dy*s,dx*s+dy*c];}
function target(){if(free)return free;const b=box(),k=W/390;
 if(T.cam==='follow'){const c=at(T.p),a=at(T.p-.003),q=at(T.p+.011),ang=Math.atan2(q[1]-a[1],q[0]-a[0]);
  return {x:c[0],y:c[1],s:30*k,r:northUp?0:-ang-Math.PI/2,ax:W/2,ay:b.top+(b.bot-b.top)*.68};}
 const top=b.top+64,bot=b.bot-24,left=24,right=W-24,theta=Math.atan2(bot-top,right-left),r=northUp?0:theta-AXIS;
 let x0=1e9,y0=1e9,x1=-1e9,y1=-1e9;R.forEach(q=>{const v=rotOf(q[0],q[1],r);x0=Math.min(x0,v[0]);y0=Math.min(y0,v[1]);x1=Math.max(x1,v[0]);y1=Math.max(y1,v[1]);});
 const s=Math.min((right-left)/(x1-x0),(bot-top)/(y1-y0))*.86,c=rotOf((x0+x1)/2,(y0+y1)/2,-r);
 return {x:c[0],y:c[1],s,r,ax:(left+right)/2,ay:(top+bot)/2};}
function stepCam(dt){const t=target();if(!camInit){Object.assign(cam,t);camInit=true;return;}const k=1-Math.exp(-dt*5);
 cam.x+=(t.x-cam.x)*k;cam.y+=(t.y-cam.y)*k;cam.ax+=(t.ax-cam.ax)*k;cam.ay+=(t.ay-cam.ay)*k;cam.s=Math.exp(Math.log(cam.s)+(Math.log(t.s)-Math.log(cam.s))*k);
 let dr=t.r-cam.r;while(dr>Math.PI)dr-=2*Math.PI;while(dr<-Math.PI)dr+=2*Math.PI;cam.r+=dr*k;}
const ws=q=>{const v=rotOf((q[0]-cam.x)*cam.s,(q[1]-cam.y)*cam.s,cam.r);return [cam.ax+v[0],cam.ay+v[1]];};
const sw=(x,y)=>{const v=rotOf(x-cam.ax,y-cam.ay,-cam.r);return [cam.x+v[0]/cam.s,cam.y+v[1]/cam.s];};
function poly(pts,close){mx.beginPath();pts.forEach((q,i)=>{const s=ws(q);i?mx.lineTo(s[0],s[1]):mx.moveTo(s[0],s[1]);});if(close)mx.closePath();}
const F='"Barlow Semi Condensed","Arial Narrow",sans-serif';

let pins=[];
function drawMap(now){
 mx.setTransform(dpr,0,0,dpr,0,0);mx.fillStyle='#12161b';mx.fillRect(0,0,W,H);
 mx.fillStyle='#0c1820';poly([...COAST,[220,-120],[-60,-120]],true);mx.fill();
 LAKES.forEach(l=>{const pts=[];for(let k=0;k<40;k++){const t=k/40*6.283,x=Math.cos(t)*l.rx,y=Math.sin(t)*l.ry;pts.push([l.c[0]+x*Math.cos(l.a)-y*Math.sin(l.a),l.c[1]+x*Math.sin(l.a)+y*Math.cos(l.a)]);}poly(pts,true);mx.fill();});
 mx.lineCap='round';mx.lineJoin='round';
 poly(RIVER);mx.strokeStyle='#0f2230';mx.lineWidth=Math.max(1.5,cam.s*.12);mx.stroke();
 TOWNS.forEach(t=>{const s=ws(t.w);mx.beginPath();mx.arc(s[0],s[1],(t.r===3?4.5:t.r===2?1.6:.8)*cam.s,0,6.283);mx.fillStyle='rgba(120,135,150,.07)';mx.fill();});
 mx.strokeStyle='#1f262e';mx.lineWidth=Math.max(.8,Math.min(2.2,cam.s*.05));ROADS.forEach(r=>{poly(r);mx.stroke();});
 // route: road ahead bright, passed road dark (as navigation apps do)
 const lw=Math.max(4,Math.min(9,cam.s*.27)),pi=Math.round(T.p*(N-1));
 poly(R);mx.strokeStyle='rgba(4,6,9,.85)';mx.lineWidth=lw+4;mx.stroke();
 const seg=(i0,i1,col,glow)=>{if(i1<=i0)return;mx.beginPath();for(let i=i0;i<=i1;i++){const s=ws(R[i]);i===i0?mx.moveTo(s[0],s[1]):mx.lineTo(s[0],s[1]);}
  mx.strokeStyle=col;mx.lineWidth=lw;mx.shadowColor=glow?col:'transparent';mx.shadowBlur=glow?8:0;mx.stroke();mx.shadowBlur=0;};
 seg(0,pi,'#3b4652',false);seg(pi,N-1,V.light,true);
 // towns
 mx.textAlign='center';mx.textBaseline='middle';
 TOWNS.forEach(t=>{if(T.cam==='whole'&&!free&&t.r<2)return;const s=ws(t.w);if(s[0]<-40||s[0]>W+40||s[1]<-20||s[1]>H+20)return;
  mx.font=(t.r===3?'600 15px ':'500 13px ')+F;mx.fillStyle=t.r===3?'#b9c3cd':'#76828f';mx.fillText(t.n,s[0],s[1]-(t.r===3?14:10));});
 // pins: all events, past and future; only the next A-card carries its heading
 const act=activeOf(T.p),k=fired(T.p),nextA=EV.find(e=>e.i>k&&e.t==='A');
 pins=[];const car=ws(at(T.p)),placed=[[car[0]-14,car[1]-14,28,28]];let grp=[];
 const near=T.cam==='whole'&&!free?5:11;
 const flush=()=>{if(!grp.length)return;if(grp.length===1)pin(grp[0],act,now,placed,nextA);else cluster(grp,act);grp=[];};
 EV.forEach(e=>{const s=ws(at(e.p));e.s=s;if(s[0]<-30||s[0]>W+30||s[1]<-30||s[1]>H+30){flush();return;}
  if(grp.length&&Math.hypot(s[0]-grp[0].s[0],s[1]-grp[0].s[1])<near)grp.push(e);else{flush();grp=[e];}});flush();
 if(nextA&&nextA.s)label(nextA,placed);
 // the car
 const sa=ws(at(T.p-.002)),sb=ws(at(T.p+.004)),ang=Math.atan2(sb[1]-sa[1],sb[0]-sa[0]);
 mx.save();mx.translate(car[0],car[1]);mx.rotate(ang+Math.PI/2);mx.beginPath();mx.arc(0,0,17,0,6.283);mx.fillStyle='rgba(255,255,255,.10)';mx.fill();
 mx.beginPath();mx.moveTo(0,-12);mx.lineTo(9,9);mx.lineTo(0,4.5);mx.lineTo(-9,9);mx.closePath();mx.fillStyle='#9e0303';mx.shadowColor='rgba(255,255,255,.55)';mx.shadowBlur=8;mx.fill();mx.shadowBlur=0;
 mx.strokeStyle='#fff';mx.lineWidth=2;mx.stroke();mx.restore();}
function pin(e,act,now,placed){const s=e.s,past=e.i<=fired(T.p)&&e.i!==act,small=T.cam==='whole'&&!free;
 const r=e.i===act?7:past?(small?2.5:3.5):(e.t==='A'?(small?4.5:6):(small?3:4.5));
 if(e.i===act){const ph=(now/1000)%1.6/1.6;mx.beginPath();mx.arc(s[0],s[1],7+ph*16,0,6.283);mx.strokeStyle=V.light;mx.globalAlpha=(1-ph)*.8;mx.lineWidth=2;mx.stroke();mx.globalAlpha=1;}
 mx.beginPath();mx.arc(s[0],s[1],r,0,6.283);mx.fillStyle=past?'#6b7884':V.light;mx.fill();mx.strokeStyle='#080b0f';mx.lineWidth=2;mx.stroke();
 if(!past&&e.t==='A'){mx.beginPath();mx.arc(s[0],s[1],Math.min(2,r-2),0,6.283);mx.fillStyle='#fff';mx.fill();}
 pins.push({x:s[0],y:s[1],r:16,ids:[e.i]});}
function cluster(g,act){const s=g[g.length-1].s,past=g.every(e=>e.i<=fired(T.p)&&e.i!==act);
 mx.beginPath();mx.arc(s[0],s[1],11,0,6.283);mx.fillStyle=past?'#6b7884':V.light;mx.fill();mx.strokeStyle='#080b0f';mx.lineWidth=2;mx.stroke();
 mx.fillStyle='#0a0c0f';mx.font='700 12px '+F;mx.textAlign='center';mx.textBaseline='middle';mx.fillText(g.length,s[0],s[1]+.5);pins.push({x:s[0],y:s[1],r:18,ids:g.map(e=>e.i)});}
function label(e,placed){const s=e.s;mx.font='600 14px '+F;const bw=mx.measureText(e.h).width+16,bh=24;let x=s[0]+12;const y=s[1]-bh/2;if(x+bw>W-8)x=s[0]-12-bw;if(x<8)x=8;
 mx.fillStyle='rgba(8,11,16,.84)';mx.beginPath();mx.roundRect(x,y,bw,bh,7);mx.fill();mx.strokeStyle='rgba(255,255,255,.12)';mx.lineWidth=1;mx.stroke();
 mx.fillStyle='#e9eef3';mx.textAlign='left';mx.textBaseline='middle';mx.fillText(e.h,x+8,y+bh/2+1);}

/* ---------- touch: pan, pinch, wheel, double tap; a tap opens a pin ---------- */
const ptrs=new Map();let moved=false,downAt=0,lastTap={t:0,x:0,y:0},pinch=null;
const local=e=>{const r=mc.getBoundingClientRect();return [(e.clientX-r.left)*W/r.width,(e.clientY-r.top)*H/r.height];};
function takeFree(){if(!free)free={x:cam.x,y:cam.y,s:cam.s,r:cam.r,ax:cam.ax,ay:cam.ay};lastTouch=performance.now();}
function setCam(){Object.assign(cam,free);}
function panBy(dx,dy){takeFree();const v=rotOf(dx,dy,-free.r);free.x-=v[0]/free.s;free.y-=v[1]/free.s;setCam();}
function zoomAt(x,y,f){takeFree();const w=sw(x,y);free.s=Math.max(.6,Math.min(400,free.s*f));const v=rotOf(x-free.ax,y-free.ay,-free.r);free.x=w[0]-v[0]/free.s;free.y=w[1]-v[1]/free.s;setCam();}
let downPt=[0,0];
mc.addEventListener('pointerdown',e=>{mc.setPointerCapture(e.pointerId);ptrs.set(e.pointerId,local(e));if(ptrs.size===1){moved=false;downAt=performance.now();downPt=local(e);}
 if(ptrs.size===2){const [a,b]=[...ptrs.values()];pinch={d:Math.hypot(a[0]-b[0],a[1]-b[1]),m:[(a[0]+b[0])/2,(a[1]+b[1])/2]};moved=true;}});
mc.addEventListener('pointermove',e=>{if(!ptrs.has(e.pointerId))return;const prev=ptrs.get(e.pointerId),p=local(e);ptrs.set(e.pointerId,p);
 if(ptrs.size===1){if(!moved&&Math.hypot(p[0]-downPt[0],p[1]-downPt[1])>6)moved=true;if(moved)panBy(p[0]-prev[0],p[1]-prev[1]);}
 else if(ptrs.size===2&&pinch){const [a,b]=[...ptrs.values()],d=Math.hypot(a[0]-b[0],a[1]-b[1]),m=[(a[0]+b[0])/2,(a[1]+b[1])/2];panBy(m[0]-pinch.m[0],m[1]-pinch.m[1]);zoomAt(m[0],m[1],d/pinch.d);pinch={d,m};}});
const up=e=>{if(!ptrs.has(e.pointerId))return;const p=ptrs.get(e.pointerId);ptrs.delete(e.pointerId);if(ptrs.size<2)pinch=null;
 if(!moved&&ptrs.size===0&&performance.now()-downAt<350){const now=performance.now();
  if(now-lastTap.t<320&&Math.hypot(p[0]-lastTap.x,p[1]-lastTap.y)<30){zoomAt(p[0],p[1],2);lastTap.t=0;return;}
  lastTap={t:now,x:p[0],y:p[1]};let best=null,bd=1e9;pins.forEach(q=>{const d=Math.hypot(q.x-p[0],q.y-p[1]);if(d<q.r&&d<bd){bd=d;best=q;}});best?openSheet(best.ids):closeSheet();}};
mc.addEventListener('pointerup',up);mc.addEventListener('pointercancel',up);
mc.addEventListener('wheel',e=>{e.preventDefault();const p=local(e);zoomAt(p[0],p[1],Math.exp(-e.deltaY*.0015));},{passive:false});

/* ---------- map buttons ---------- */
function setCamMode(m){T.cam=m;free=null;northUp=false;$('camFollow').setAttribute('aria-pressed',m==='follow');$('camWhole').setAttribute('aria-pressed',m==='whole');}
$('camFollow').onclick=()=>setCamMode('follow');$('camWhole').onclick=()=>setCamMode('whole');
$('recenter').onclick=()=>{free=null;northUp=false;};
$('compass').onclick=()=>{if(free){free.r=0;}else northUp=true;};
function updMapButtons(){let r=cam.r%(2*Math.PI);if(r>Math.PI)r-=2*Math.PI;if(r<-Math.PI)r+=2*Math.PI;
 $('compass').hidden=Math.abs(r)<.06;$('compass').querySelector('svg').style.transform=`rotate(${r}rad)`;
 const rc=$('recenter');rc.hidden=!(free||northUp);rc.setAttribute('aria-label',T.cam==='follow'?'Back to the car':'Show the whole road');rc.querySelector('span').textContent=T.cam==='follow'?'Re-centre':'Whole road';
 if(T.cam==='follow'&&free&&performance.now()-lastTouch>10000)free=null;}

/* ---------- event card that slides up in map mode ---------- */
let toastFor=-2,sheetOpen=false;
function updToast(){const a=activeOf(T.p),t=$('evToast'),show=mode==='map'&&a>=0&&narr(a,T.p)<1&&!sheetOpen;
 if(a!==toastFor&&a>=0){const e=EV[a];t.querySelector('.th').style.backgroundImage=PICS[a]?`url(${PICS[a]})`:'';t.querySelector('.th').classList.toggle('ph',!PICS[a]);
  t.querySelector('.d').textContent=e.d;t.querySelector('.h').textContent=e.h;toastFor=a;}
 t.classList.toggle('on',show);t.dataset.i=a;if(a>=0)t.querySelector('.pr i').style.transform=`scaleX(${narr(a,T.p)})`;}
$('evToast').onclick=()=>{const i=+$('evToast').dataset.i;if(i>=0)openSheet([i]);};
const X='<button class="x" aria-label="Close"><svg viewBox="0 0 24 24"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg></button>';
function openSheet(ids){const sh=$('sheet'),k=fired(T.p);sheetOpen=true;const ahead=ids.filter(i=>i>k);
 if(ids.length>1){const past=ids.filter(i=>i<=k);
  sh.innerHTML=`<header><div><div class="d">${ids.length} events here</div><h3>${past.length?esc(EV[past[0]].d)+' to '+esc(EV[past[past.length-1]].d):'Ahead on the road'}</h3></div>${X}</header><div class="list">${past.map(i=>`<button data-i="${i}"><span>${esc(EV[i].d)}</span><span>${esc(EV[i].h)}</span></button>`).join('')}${ahead.length?`<p class="more">${ahead.length} more ahead</p>`:''}</div>`;}
 else{const e=EV[ids[0]];if(ahead.length)sh.innerHTML=`<header><div><div class="d">Ahead</div><h3>Opens when you get there</h3></div>${X}</header>`;
  else{const b=textOf(e.i);sh.innerHTML=`<header><div><div class="d">${esc(e.d)}</div><h3>${esc(e.h)}</h3></div>${X}</header><div class="bd"><p>${b?esc(b):'<span class="miss">Card texts are not loaded on this device.</span>'}</p></div>
   <footer><button class="pill" id="replay"><svg viewBox="0 0 24 24"><path d="M3 12a9 9 0 1 0 9-9 9.75 9.75 0 0 0-6.74 2.74L3 8"/><path d="M3 3v5h5"/></svg><span>Replay narration</span></button></footer>`;}}
 sh.classList.add('on');sh.querySelector('.x').onclick=closeSheet;sh.querySelectorAll('.list button').forEach(b=>b.onclick=()=>openSheet([+b.dataset.i]));
 const rp=sh.querySelector('#replay');if(rp)rp.onclick=()=>{rp.lastChild.textContent='Playing…';setTimeout(()=>{if(rp.isConnected)rp.lastChild.textContent='Replay narration';},2500);};}
function closeSheet(){$('sheet').classList.remove('on');sheetOpen=false;}

/* ---------- text mode: the logbook, highlighted by sentence ---------- */
const sentences=b=>b.split(/(?<=[.!?…]["”’)]?)\s+(?=["“‘(]?[A-Z0-9])/);
let logKey='',follow=true,prog=false,expanded=new Set(),chunks=[],litIdx=-2,curEl=null;
function buildLog(){const k=fired(T.p),a=activeOf(T.p),key=k+'|'+a+'|'+[...expanded].join(',')+'|'+Object.keys(TEXTS).length;if(key===logKey)return;logKey=key;let h='';
 for(let i=0;i<=k;i++){const e=EV[i],b=textOf(i);
  if(i===a){chunks=[e.h.length+1];let body='';if(b){sentences(b).forEach((s,j)=>{chunks.push(s.length+1);body+=`<span class="s">${esc(s)}</span> `;});}
   h+=`<article class="cur" id="cur"><div class="ct"><span class="cd">${esc(e.d)}</span><span class="eq" aria-hidden="true"><i></i><i></i><i></i><i></i></span></div><h2>${esc(e.h)}</h2>${b?`<p>${body}</p>`:`<p class="miss">Card texts are not loaded on this device. In the panel: Map &amp; Text → Load card texts.</p>`}</article>`;}
  else h+=`<button class="lrow" data-i="${i}" aria-expanded="${expanded.has(i)}"><span class="rl"><span class="rd">${esc(e.d)}</span><span class="rh">${esc(e.h)}</span></span>${expanded.has(i)?`<p class="rb">${b?esc(b):'<span class="miss">Text not loaded.</span>'}</p>`:''}</button>`;}
 const n=EV[k+1];if(n)h+=`<div class="nextRow"><small>Next stop</small><span>${esc(n.h)}, ${esc(n.d)}</span></div>`;
 $('logIn').innerHTML=h;litIdx=-2;curEl=$('cur');
 $('logIn').querySelectorAll('.lrow').forEach(b=>b.onclick=()=>{const i=+b.dataset.i;expanded.has(i)?expanded.delete(i):expanded.add(i);follow=false;$('backNow').hidden=false;buildLog();});}
function updLog(dt){buildLog();const lg=$('log'),a=activeOf(T.p);
 if(curEl&&a>=0){const nn=narr(a,T.p),tot=chunks.reduce((x,y)=>x+y,0),c=nn*tot;let acc=0,idx=0;while(idx<chunks.length&&acc+chunks[idx]<=c){acc+=chunks[idx];idx++;}
  const lit=nn>=1?chunks.length:idx-1;   // -1 while the heading is being read
  if(lit!==litIdx){curEl.querySelectorAll('.s').forEach((s,j)=>{s.classList.toggle('r',j<lit);s.classList.toggle('c',j===lit);});litIdx=lit;}
  curEl.querySelector('.eq').style.visibility=nn<1?'visible':'hidden';}
 if(follow){let target=lg.scrollHeight-lg.clientHeight;const cs=curEl&&curEl.querySelector('.s.c');if(cs)target=Math.min(target,Math.max(0,cs.offsetTop-lg.clientHeight*.38));
  const d=target-lg.scrollTop;if(Math.abs(d)>.5){prog=true;lg.scrollTop+=d*(1-Math.exp(-dt*6));}}}
$('log').addEventListener('scroll',()=>{if(prog){prog=false;return;}const lg=$('log');if(lg.scrollHeight-lg.clientHeight-lg.scrollTop>40){follow=false;$('backNow').hidden=false;}});
['wheel','touchstart'].forEach(ev=>$('log').addEventListener(ev,()=>{prog=false;},{passive:true}));
$('backNow').onclick=()=>{follow=true;expanded.clear();$('backNow').hidden=true;};

/* ---------- top panel in Map and Text modes (H-1 … H-10) ---------- */
let panelKey='';
function panel(){const a=activeOf(T.p),k=fired(T.p);let title,date=null;
 if(a>=0){title=EV[a].h;date=EV[a].d;}else{const n=EV[k+1];title=n?`Next: ${n.h}, ${n.d}`:'';}
 const key=title+'|'+date;if(key!==panelKey){panelKey=key;const d=$('date');
  if(date){d.classList.remove('off');const m=date.match(/^([\d.,]+)\s*(.*)$/);d.innerHTML=m?`${m[1]}<small>${m[2]}</small>`:esc(date);}else d.classList.add('off');setTitleText(title);}
 $('tripBar').firstChild.style.width=(T.p*100)+'%';const p0=k>=0?EV[k].p:0,p1=EV[k+1]?EV[k+1].p:1;$('nextBar').firstChild.style.width=(p1>p0?Math.min(1,(T.p-p0)/(p1-p0))*100:100)+'%';}

/* ---------- tune panel: trip and texts ---------- */
const JUMP=[[0,'Big Bang'],[9,'Milky Way'],[37,'Sun & Earth'],[40,'Life'],[54,'Cambrian'],[60,'Dinosaurs'],[64,'Modern Earth'],[66,'Apes stand up']];
$('tripCtl').innerHTML=`<label for="tPos">Position<span id="tRead"></span></label><input type="range" id="tPos" min="0" max="100000" step="1">
 <div class="chips">${JUMP.map(([i,l])=>`<button data-j="${i}">${l}</button>`).join('')}</div>
 <p class="hint">Card texts are not on GitHub. Load the texts file once on each device; it stays in this browser.</p>
 <div class="tb" style="margin-top:6px"><button id="tLoad">Load card texts</button><button id="tForget">Forget texts</button></div><input type="file" id="tFile" accept=".json,application/json" hidden>
 <p class="hint" id="tStat"></p>`;
const stat=()=>{const n=Object.keys(TEXTS).length;$('tStat').textContent=n?`Texts on this device: ${n} cards.`:'No texts loaded. Two cards (The age of dinosaurs, Modern Earth) show their text anyway.';};stat();
$('tLoad').onclick=()=>$('tFile').click();
$('tFile').onchange=e=>{const f=e.target.files[0];if(!f)return;f.text().then(s=>{const j=JSON.parse(s);TEXTS=j.texts||j;try{localStorage.setItem('tm-hud-texts',JSON.stringify(TEXTS));}catch(er){}stat();logKey='';toast('Card texts loaded');}).catch(()=>toast('That file is not a texts file'));};
$('tForget').onclick=()=>{TEXTS={};try{localStorage.removeItem('tm-hud-texts');}catch(e){}stat();logKey='';};
const jumpTo=p=>{T.p=p;follow=true;expanded.clear();$('backNow').hidden=true;closeSheet();};
$('tPos').oninput=e=>jumpTo(+e.target.value/100000);
$('tripCtl').querySelectorAll('[data-j]').forEach(b=>b.onclick=()=>{const e=EV[+b.dataset.j];jumpTo(e.p+1e-7);});

/* ---------- frame ---------- */
let uiT=0,saveT=0;
window.Modes={
 frame(dt,now){if(playing&&T.p<1)T.p=Math.min(1,T.p+dt*(+V.tripSpeed||10)*KMH/KM/3600);
  if(mode==='map'){if(mc.width!==Math.round((mc.clientWidth||390)*Math.min(2,devicePixelRatio||1)))size();stepCam(dt);drawMap(now);updMapButtons();}
  if(mode!=='image')panel();updToast();if(mode==='text')updLog(dt);
  uiT-=dt;if(uiT<=0){uiT=.15;$('tPos').value=Math.round(T.p*100000);$('tRead').textContent=`km ${(T.p*KM).toFixed(1)} · ${fmtAge(T.p)}`;}
  saveT-=dt;if(saveT<=0){saveT=2;try{localStorage.setItem('tm-hud-trip',T.p);}catch(e){}}},
 onMode(m){panelKey='';logKey='';closeSheet();if(m==='text'){follow=true;expanded.clear();$('backNow').hidden=true;}else $('backNow').hidden=true;if(m==='map')size();},
 restart(){T.p=0;follow=true;expanded.clear();}
};
addEventListener('resize',()=>{size();camInit=false;});
setCamMode('follow');
})();
