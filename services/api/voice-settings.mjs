import {mkdir,readFile,writeFile,rename} from 'node:fs/promises';import {dirname} from 'node:path';
const characters=['human','host','concierge','astronaut','robot','panda','fox','cat'];
export class VoiceSettingsStore{
 constructor(file,workspaces,samples){this.file=file;this.workspaces=workspaces;this.samples=samples;this.items=new Map();this.queue=Promise.resolve();}
 key(site,character){this.workspaces.get(site);if(!characters.includes(character))throw Error('角色无效');return JSON.stringify([site,character]);}
 async load(){try{this.items=new Map(JSON.parse(await readFile(this.file,'utf8')));}catch(e){if(e.code!=='ENOENT')throw e;}}
 get(site,character){return structuredClone(this.items.get(this.key(site,character))||null);}
 async save(site,character,c){const key=this.key(site,character);if(!['system','reference'].includes(c.source)||!['calm','lively','warm','storytelling'].includes(c.personality)||!['neutral','happy','rich','sad'].includes(c.emotion)||!Number.isFinite(c.intensity)||c.intensity<0||c.intensity>1||!Number.isFinite(c.rate)||c.rate<.5||c.rate>1.6||typeof c.autoNarrate!=='boolean'||typeof c.voiceURI!=='string'||c.voiceURI.length>500||typeof c.sampleId!=='string')throw Error('声音配置无效');if(c.source==='reference')await this.samples.get(site,c.sampleId);const out=Object.fromEntries(['source','voiceURI','sampleId','personality','emotion','intensity','rate','autoNarrate'].map(k=>[k,c[k]]));const operation=this.queue.then(async()=>{const next=new Map(this.items);next.set(key,out);await mkdir(dirname(this.file),{recursive:true});await writeFile(this.file+'.tmp',JSON.stringify([...next],null,2));await rename(this.file+'.tmp',this.file);this.items=next;return structuredClone(out);});this.queue=operation.catch(()=>{});return operation;}
}
