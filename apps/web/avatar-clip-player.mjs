// Pre-recorded action playback only; never claims generated lip sync.
export class AvatarClipPlayer {
 constructor(video,clips,{onChange=()=>{},onError=()=>{}}={}){Object.assign(this,{video,clips,onChange,onError});this.current=null;this.phase='idle';this.version=0;this.enabled=true;this.handlers=[];video.addEventListener('timeupdate',()=>this.tick());video.addEventListener('ended',()=>{if(this.phase==='playing')this.finish();});}
 clear(){for(const [name,fn]of this.handlers)this.video.removeEventListener(name,fn);this.handlers=[];}
 listen(name,fn){this.video.addEventListener(name,fn);this.handlers.push([name,fn]);}
 play(id,{restart=false}={}){if(!this.enabled||!Object.hasOwn(this.clips,id))return;if(!restart&&this.current===id&&['loading','seeking','playing'].includes(this.phase))return;this.clear();const token=++this.version,v=this.video,c=this.clips[id];this.phase='loading';this.current=id;v.pause();this.onChange(id);const start=()=>{if(token!==this.version||!this.enabled)return;this.phase='playing';this.clear();Promise.resolve(v.play()).catch(e=>{if(token===this.version){this.phase='error';this.onError(e);}});};this.listen('error',()=>{if(token===this.version){this.phase='error';this.clear();this.onError(Error('视频读取失败'));}});this.listen('loadedmetadata',()=>{if(token!==this.version)return;this.phase='seeking';if(Math.abs(v.currentTime-c.start)<.04){start();return;}this.listen('seeked',start);try{v.currentTime=c.start;}catch(e){this.phase='error';this.onError(e);}});v.src='/avatar-media/'+id;v.load();}
 tick(){if(!this.enabled||this.phase!=='playing'||this.video.seeking)return;const c=this.clips[this.current];if(c&&this.video.currentTime>=c.end)this.finish();}
 finish(){if(this.current==='idle')this.play('idle',{restart:true});else this.play('idle');}
 stop(){this.enabled=false;this.version++;this.clear();this.phase='idle';this.current=null;this.video.pause();}
}
