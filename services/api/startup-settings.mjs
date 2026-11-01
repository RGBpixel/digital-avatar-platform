import {mkdir,readFile,writeFile,rename} from 'node:fs/promises';
import {dirname} from 'node:path';
const fixed=['avatar-real-person','avatar-wake-settings','avatar-interaction-mode','avatar-screen','avatar-character','avatar-scene','avatar-auto-greet','avatar-input-preferences','avatar-camera-reception','avatar-camera-device','avatar-face-voice'];
export function validateSnapshot(value){
 if(!value||typeof value!=='object'||Array.isArray(value))throw Error('启动配置格式无效');
 const out={};for(const [key,v] of Object.entries(value)){
  if(!fixed.includes(key)&&!/^avatar-voice:[a-z0-9-]+:(human|host|concierge|astronaut|robot|panda|fox|cat)$/.test(key))throw Error('不允许保存此配置项');
  if(typeof v!=='string'||v.length>6000)throw Error('配置内容过长');out[key]=v;
 }if(JSON.stringify(out).length>14000)throw Error('配置总量过大');return out;
}
export class StartupSettings {
 constructor(file){this.file=file;this.value=null;this.queue=Promise.resolve();}
 async load(){try{this.value=validateSnapshot(JSON.parse(await readFile(this.file,'utf8')));}catch(e){if(e.code!=='ENOENT')throw e;}}
 get(){return structuredClone(this.value);}
 save(value){const clean=validateSnapshot(value);const op=this.queue.then(async()=>{await mkdir(dirname(this.file),{recursive:true});await writeFile(this.file+'.tmp',JSON.stringify(clean,null,2));await rename(this.file+'.tmp',this.file);this.value=clean;return this.get();});this.queue=op.catch(()=>{});return op;}
}
