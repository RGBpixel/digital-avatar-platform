// Group greetings never associate a private conversation or disclose message bodies.
export class GroupArrival{
 constructor({clock=Date.now}={}){this.clock=clock;this.tracks=new Map();this.unknownFrames=0;this.unknownLast=0;}
 observe(result,{changed=true}={}){const now=this.clock(),counts=new Map(),fresh=[];for(const face of result.faces||[])if(face.status==='candidate')counts.set(face.personId,(counts.get(face.personId)||0)+1);for(const [id,t]of this.tracks)if(now-t.last>30000)this.tracks.delete(id);for(const f of result.faces||[]){if(f.status!=='candidate'||counts.get(f.personId)!==1)continue;let t=this.tracks.get(f.personId);if(!t||now-t.last>5000)t={first:now,frames:0,last:now,greetedAt:t?.greetedAt??null};if(changed)t.frames++;t.last=now;this.tracks.set(f.personId,t);if(result.count>1&&t.frames>=3&&now-t.first>=1200&&(t.greetedAt===null||now-t.greetedAt>=120000)){fresh.push({...f});}}
 const unknown=(result.faces||[]).filter(f=>f.status!=='candidate'||counts.get(f.personId)>1).length;this.unknownFrames=unknown&&changed?this.unknownFrames+1:unknown?this.unknownFrames:0;return {known:fresh,unknown:result.count>1&&this.unknownFrames>=3&&(!this.unknownLast||now-this.unknownLast>=120000)?unknown:0};}
 mark(batch){const now=this.clock();for(const f of batch.known){const t=this.tracks.get(f.personId);if(t)t.greetedAt=now;}if(batch.unknown)this.unknownLast=now;}
 reset(){this.tracks.clear();this.unknownFrames=0;this.unknownLast=0;}
}
export function groupGreeting(batch){const chunks=batch.known.map(f=>f.nickname+(f.affiliation==='internal'?'，欢迎回来！':'，您好，欢迎您！')+(f.pendingMessages?'您有待告知事项，方便单独交流时我优先转达。':''));if(batch.unknown)chunks.push(batch.unknown===1?'也欢迎这位朋友！':'也欢迎其他几位朋友！');return chunks.join(' ');}
