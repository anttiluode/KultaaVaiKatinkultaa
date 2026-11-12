"use strict";
(() => {
 const {Net,RELAY}=globalThis.GN27;
 const $=id=>document.getElementById(id);
 const colors=["#65b9ff","#d8b46f","#5ce1bb","#ff7ea3"];
 const scenarioText={
  empty_single:"Empty memory acquires a single beat and then predicts it.",
  empty_two:"Two phases, 0 and 16, are acquired in one 32-tick ring.",
  add_second_at_5:"One new event appears at phase 16 after lap 5.",
  remove_second_at_8:"Second event disappears after lap 8; omission should erase it.",
  switch_0_to_16:"The world changes from phase 0 to phase 16 after lap 8.",
  stop_after_5:"The world stops; the ring should erase the obsolete beat.",
  omit_at_5:"One missed world event is erased and then rewritten.",
  extra_at_5:"One unexpected event is written and then erased.",
  phase_1:"A fixed phase shift of one tick; new empty memory learns the shifted pattern."
 };
 let scenario="empty_single",events=[],time=0,write=true,erase=true,timer=null;
 const schedule=lap=>{
  if(scenario==="empty_two")return [0,16];
  if(scenario==="add_second_at_5")return lap>=5?[0,16]:[0];
  if(scenario==="remove_second_at_8")return lap>=8?[0]:[0,16];
  if(scenario==="switch_0_to_16")return lap>=8?[16]:[0];
  if(scenario==="stop_after_5")return lap>=5?[]:[0];
  if(scenario==="omit_at_5")return lap===5?[]:[0];
  if(scenario==="extra_at_5")return lap===5?[0,16]:[0];
  if(scenario==="phase_1")return [1];
  return [0];
 };
 function simulate(){
  const edges=Array.from({length:8},(_,i)=>[i+1,1+(i+1)%8,-6,0]);
  edges.push([0,9,-5,0],[1,9,5,0],[0,10,5,0],[1,10,-5,0]);
  if(write)edges.push([9,3,-6,0]);
  if(erase)edges.push([10,3,6,0]);
  const net=new Net(Array(11).fill(RELAY),edges).settle(1500);
  const e=Array.from({length:11},()=>[]),last=Array(11).fill(true);
  for(let t=0;t<640;t++){
   const sp=new Float64Array(11),phase=t%32;
   if(schedule(Math.floor(t/32)).some(p=>phase>=p&&phase<p+2))sp[0]=-10;
   const own=net.step(null,sp);
   for(let i=0;i<11;i++){
    const loud=own[i]>3;
    if(loud&&!last[i])e[i].push(t);
    last[i]=loud;
   }
  }
  return e;
 }
 function gates(weights){
  const output=[];
  for(const [a,b] of [[0,0],[1,0],[0,1],[1,1]]){
   const net=new Net([RELAY,RELAY,RELAY],[[0,2,weights[0],0],[1,2,weights[1],0]]).settle(1500);
   let last=true,count=0;
   for(let t=0;t<44;t++){
    const own=net.step(null,new Float64Array([a&&t<2?-10:0,b&&t<2?-10:0,0]));
    const loud=own[2]>3;
    if(loud&&!last)count++;
    last=loud;
   }
   output.push(count);
  }
  return output;
 }
 function table(){
  const circuits=[[-4.5,-4.5],[-2.5,-2.5],[-5,5],[5,-5]].map(gates);
  const rows=["0 / 0","1 / 0","0 / 1","1 / 1"],body=$("truth").querySelector("tbody");
  body.replaceChildren();
  for(let i=0;i<4;i++){
   const tr=document.createElement("tr");
   const values=[rows[i]].concat(circuits.map(a=>a[i]?"BEAT":"quiet"));
   for(const value of values){
    const td=document.createElement("td");td.textContent=value;
    if(value==="BEAT")td.style.color="#69ecc4";
    tr.append(td);
   }
   body.append(tr);
  }
 }
 const now=(e,t)=>e.some(z=>Math.abs(z-t)<=1);
 function ring(){
  const ctx=$("orbit").getContext("2d"),cx=215,cy=193,r=132;
  ctx.clearRect(0,0,430,440);ctx.strokeStyle="#34576a";ctx.lineWidth=12;
  ctx.beginPath();ctx.arc(cx,cy,r,0,Math.PI*2);ctx.stroke();
  for(let i=0;i<8;i++){
   const theta=-Math.PI/2+i*Math.PI/4,x=cx+r*Math.cos(theta),y=cy+r*Math.sin(theta);
   const lit=now(events[i+1],time);
   ctx.beginPath();ctx.arc(x,y,lit?23:17,0,2*Math.PI);
   ctx.fillStyle=lit?colors[1]:"#246e6a";ctx.strokeStyle=lit?"#fff1cc":"#88e3ca";
   ctx.lineWidth=lit?3:1.5;ctx.fill();ctx.stroke();
   ctx.fillStyle=lit?"#142331":"#e8fffa";ctx.textAlign="center";ctx.textBaseline="middle";
   ctx.font="bold 13px system-ui";ctx.fillText(i+1,x,y);
  }
  ctx.fillStyle="#c7e8ed";ctx.font="bold 17px system-ui";ctx.fillText("MEMORY",cx,cy-15);
  ctx.fillStyle="#a9bdce";ctx.font="13px system-ui";ctx.fillText("8 relays · 32 ticks",cx,cy+13);
  for(const [x,i,label,c] of [[65,0,"WORLD",colors[0]],[215,9,"WRITE",colors[2]],[365,10,"ERASE",colors[3]]]){
   const flash=now(events[i],time);
   ctx.beginPath();ctx.arc(x,375,flash?14:10,0,Math.PI*2);
   ctx.fillStyle=flash?c:"#4a6174";ctx.fill();
   ctx.fillStyle="#d0dfeb";ctx.font="12px system-ui";ctx.fillText(label,x,408);
  }
 }
 function plot(){
  const c=$("raster"),ctx=c.getContext("2d"),w=c.width;
  ctx.clearRect(0,0,w,c.height);ctx.fillStyle="#0c1827";ctx.fillRect(0,0,w,c.height);
  const left=110,dx=(w-133)/640,x=t=>left+dx*t;
  ctx.font="12px system-ui";
  for(let lap=0;lap<=20;lap++){
   const px=x(lap*32);ctx.strokeStyle=lap%5===0?"#46617a":"#25394d";ctx.lineWidth=1;
   ctx.beginPath();ctx.moveTo(px,10);ctx.lineTo(px,242);ctx.stroke();
   if(lap%2===0){ctx.fillStyle="#9ab1c4";ctx.fillText(lap,px-3,265);}
  }
  ctx.fillStyle="#9ab1c4";ctx.fillText("Laps",12,265);
  const tracks=[[0,"World",colors[0]],[1,"Prediction",colors[1]],[9,"Innovation",colors[2]],[10,"Omission",colors[3]]];
  tracks.forEach(([idx,label,color],i)=>{
   const y=51+i*52;ctx.fillStyle="#d4e0ef";ctx.fillText(label,10,y+2);
   ctx.strokeStyle="#35506a";ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(w-20,y);ctx.stroke();
   for(const tick of events[idx]){
    const xx=x(tick);ctx.strokeStyle=color;ctx.lineWidth=3;
    ctx.beginPath();ctx.moveTo(xx,y);ctx.lineTo(xx,y-22);ctx.stroke();
   }
  });
  ctx.strokeStyle="#fafafa";ctx.lineWidth=1.5;ctx.setLineDash([5,5]);
  ctx.beginPath();ctx.moveTo(x(time),12);ctx.lineTo(x(time),244);ctx.stroke();ctx.setLineDash([]);
 }
 function display(){
  $("tick").textContent=time+" / 640";$("scrub").value=time;
  ring();plot();
 }
 function recompute(){
  events=simulate();
  [["worldCount",0],["predictionCount",1],["writeCount",9],["eraseCount",10]]
   .forEach(([id,i])=>$(id).textContent=String(events[i].length));
  $("description").textContent=scenarioText[scenario]+"  Innovation: "+
   (events[9].join(", ")||"none")+". Omission: "+(events[10].join(", ")||"none")+".";
  display();
 }
 function stop(){
  if(timer!==null)clearInterval(timer);
  timer=null;$("run").textContent="▶ Play";
 }
 $("run").addEventListener("click",()=>{
  if(timer!==null){stop();return}
  $("run").textContent="❚❚ Pause";
  timer=setInterval(()=>{time=(time+Number($("speed").value))%640;display();},70);
 });
 $("restart").addEventListener("click",()=>{stop();time=0;display()});
 $("scenario").addEventListener("change",()=>{stop();scenario=$("scenario").value;time=0;recompute()});
 $("write").addEventListener("change",()=>{stop();write=$("write").checked;recompute()});
 $("erase").addEventListener("change",()=>{stop();erase=$("erase").checked;recompute()});
 $("scrub").addEventListener("input",()=>{time=Number($("scrub").value);display()});
 $("speed").addEventListener("input",()=>{$("speedLabel").textContent=$("speed").value});
 table();recompute();
})();
