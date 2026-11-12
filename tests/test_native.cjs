"use strict";
const assert=require("node:assert/strict");
const {Net,RELAY}=require("../v27.js");
function truth(a,b,w0,w1){
 const n=new Net([RELAY,RELAY,RELAY],[[0,2,w0,0],[1,2,w1,0]]).settle(1500);
 const ev=[[],[],[]],prev=[true,true,true];
 for(let t=0;t<44;t++){
  const own=n.step(null,new Float64Array([a&&t<2?-10:0,b&&t<2?-10:0,0]));
  own.forEach((v,i)=>{const loud=v>3;if(loud&&!prev[i])ev[i].push(t);prev[i]=loud;});
 }
 return ev[2];
}
for(const [w0,w1,expected] of [
 [-4.5,-4.5,[0,1,1,0]],
 [-2.5,-2.5,[0,0,0,1]],
 [-5,+5,[0,1,0,0]],
 [+5,-5,[0,0,1,0]]
]){
 const actual=[[0,0],[1,0],[0,1],[1,1]].map(([a,b])=>Number(truth(a,b,w0,w1).length>0));
 assert.deepEqual(actual,expected);
}
function pattern(name,lap){
 switch(name){
 case "empty_two":return [0,16];
 case "stop_after_5":return lap<5?[0]:[];
 case "omit_at_5":return lap===5?[]:[0];
 case "extra_at_5":return lap===5?[0,16]:[0];
 case "add_second_at_5":return lap<5?[0]:[0,16];
 default:return [0];
 }
}
function run(name,write=true,erase=true){
 const edges=Array.from({length:8},(_,i)=>[i+1,1+(i+1)%8,-6,0]);
 edges.push([0,9,-5,0],[1,9,5,0],[0,10,5,0],[1,10,-5,0]);
 if(write)edges.push([9,3,-6,0]);
 if(erase)edges.push([10,3,6,0]);
 const n=new Net(Array(11).fill(RELAY),edges).settle(1500);
 const ev=Array.from({length:11},()=>[]),prev=Array(11).fill(true);
 for(let t=0;t<640;t++){
  const sp=new Float64Array(11),slot=t%32;
  if(pattern(name,Math.floor(t/32)).some(p=>slot>=p&&slot<p+2))sp[0]=-10;
  const own=n.step(null,sp);
  own.forEach((v,i)=>{const loud=v>3;if(loud&&!prev[i])ev[i].push(t);prev[i]=loud;});
 }
 return ev;
}
let e=run("empty_single");
assert.deepEqual(e[9],[8]);assert.deepEqual(e[10],[]);
assert.deepEqual(e[1].slice(0,4),[36,68,100,132]);
e=run("empty_two");
assert.deepEqual(e[9],[8,24]);
assert.deepEqual(e[1].slice(0,4),[36,52,68,84]);
e=run("stop_after_5");assert.deepEqual(e[10],[168]);assert.equal(e[1].at(-1),164);
e=run("omit_at_5");assert.deepEqual(e[10],[168]);assert.deepEqual(e[9],[8,200]);
e=run("extra_at_5");assert.deepEqual(e[9],[8,184]);assert.deepEqual(e[10],[216]);
e=run("empty_single",false,false);assert.deepEqual(e[1],[]);assert(e[9].length>10);
console.log("JS native gates, signed write/erase and no-feedback controls passed");
