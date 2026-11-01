import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';
import {readFile} from 'node:fs/promises';
const source=await readFile(new URL('../apps/web/face-reception.js',import.meta.url),'utf8');
const poll=source.slice(source.indexOf(' async function poll('),source.indexOf(' window.onLocalCameraReady='));
const release=source.slice(source.indexOf(' function releaseCameraPerson('),source.indexOf(' function clearCandidate('));
function setup(){
 const nodes=new Map();const node=id=>{if(!nodes.has(id))nodes.set(id,{checked:true,srcObject:{},textContent:''});return nodes.get(id);};
 const calls=[];let result;
 const c=vm.createContext({window:{endVoiceConversation(){calls.push('end');},clearMessageIdentity(){calls.push('messages');}},el:node,site:'office',generation:1,inflight:false,previousFrame:null,unchangedFrames:0,last:null,stable:3,absent:0,present:true,lastGreet:Date.now(),candidate:{personId:'a'},confirmedPerson:{personId:'a'},personalSession:'session-a',guidedSession:'draft-a',autoEnrollment:null,unknownFrames:0,candidateFrames:3,candidateKey:'a',identityPrompt:false,lastVideoAttempt:0,groupMode:false,banner:{},timer:null,status(){},frame:()=>Math.random().toString(),api:async()=>result,cancelPresence(){calls.push('cancel');},stop(){calls.push('stop');},clearPersonalChat(){c.personalSession=null;c.guidedSession=null;calls.push('clear');},clearPhoto(){},clearCandidate(){c.candidate=null;c.candidateKey=null;c.candidateFrames=0;c.unknownFrames=0;},identityBanner(){},associateVideo(){},greetGroup(){},greet:async()=>calls.push('greet'),mode:()=> 'visitor',interactionBusy:false,arrivalBusy:false,clearGuided(){},setTimeout:()=>1,Date});
 vm.runInContext(release+poll,c);
 return {c,calls,async tick(out){result={elapsedMs:1,registeredCount:1,...out};await c.poll(c.generation);}};
}
test('连续无人画面清除旧身份、草稿并取消旧播报',async()=>{const f=setup();await f.tick({count:0,faces:[]});assert.equal(f.c.personalSession,null);await f.tick({count:0,faces:[]});assert.equal(f.c.personalSession,null);assert.equal(f.c.confirmedPerson,null);assert.equal(f.c.guidedSession,null);assert.equal(f.c.present,false);assert.ok(f.calls.includes('stop'));assert.equal(f.c.generation,2);});
test('已知人员直接被陌生人替换，绕过旧问候冷却并重新接待',async()=>{const f=setup();const out={count:1,faces:[{status:'unknown',reason:'low-score'}]};await f.tick(out);assert.equal(f.c.confirmedPerson.personId,'a');await f.tick(out);assert.equal(f.c.confirmedPerson,null);assert.equal(f.c.personalSession,null);assert.equal(f.c.guidedSession,null);assert.ok(f.calls.includes('greet'));});
test('陌生人短暂识别失败一帧不立即切断原会话',async()=>{const f=setup();await f.tick({count:1,faces:[{status:'unknown'}]});await f.tick({count:1,faces:[{status:'candidate',personId:'a'}]});assert.equal(f.c.confirmedPerson.personId,'a');assert.equal(f.c.personalSession,null);assert.ok(!f.calls.includes('stop'));});
test('已登记的新人员直接替换旧人员，立即解除旧会话',async()=>{const f=setup();await f.tick({count:1,faces:[{status:'candidate',personId:'b'}]});assert.equal(f.c.confirmedPerson,null);assert.equal(f.c.personalSession,null);assert.equal(f.c.candidate.personId,'b');assert.equal(f.c.lastGreet,0);});
