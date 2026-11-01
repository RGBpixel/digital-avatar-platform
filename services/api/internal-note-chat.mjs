import {randomUUID} from 'node:crypto';
export class InternalNoteChat {
 constructor(organization){this.org=organization;this.sessions=new Map();}
 result(s,text){return {sessionId:s.id,state:s.state,mode:'guided',kind:'note',text};}
 start(site,b){this.org.auth(site,b.token);for(const [id,s]of this.sessions)if(s.expiresAt<Date.now())this.sessions.delete(id);if(this.sessions.size>=100)throw Error('留言会话过多');const s={id:randomUUID(),site,token:b.token,state:'note-recipient',expiresAt:Date.now()+300000};this.sessions.set(s.id,s);return this.result(s,'您想给哪位内部人员留言？请说他的称呼。重名时我会请您确认具体对象。');}
 async turn(site,b){const s=this.sessions.get(b.sessionId);if(!s||s.site!==site||s.expiresAt<Date.now())throw Error('留言会话已失效');this.org.auth(site,s.token);if(typeof b.text!=='string'||!b.text.trim()||b.text.length>1000)throw Error('留言输入须为1–1000字');const text=b.text.trim().replace(/[。！!]+$/,'');if(s.state==='done'||s.state==='cancelled')return this.result(s,'本轮留言已结束。');if(text==='取消'){s.state='cancelled';return this.result(s,'本轮留言未发送。');}
 if(s.state==='note-recipient'){const matches=this.org.dashboard(site).employees.map(e=>this.org.r.person(site,e.personId)).filter(p=>p.nickname===text);if(!matches.length)return this.result(s,'没有找到审批通过的内部人员，请核对称呼。');if(matches.length>1){s.candidates=matches.map(p=>p.id);s.state='note-choice';return this.result(s,'有重名人员，请回复序号：'+matches.map((p,i)=>(i+1)+'：'+p.nickname+'（'+(p.selfRole||'岗位未说明')+'，档案末尾'+p.id.slice(-6)+'）').join('；'));}s.recipientId=matches[0].id;s.state='note-text';return this.result(s,'想给'+text+'留言什么内容？');}
 if(s.state==='note-choice'){const i=Number(text)-1;if(!Number.isInteger(i)||!s.candidates[i])return this.result(s,'请回复列表中的序号。');s.recipientId=s.candidates[i];this.org.staff(site,s.recipientId);s.state='note-text';return this.result(s,'请说出留言内容。');}
 if(s.state==='note-text'){this.org.staff(site,s.recipientId);s.text=b.text.trim();s.state='note-confirm';return this.result(s,'给“'+this.org.r.person(site,s.recipientId).nickname+'”的留言：“'+s.text+'”。回复“确认发送”才保存到内部收件箱，或回复“取消”。不会向飞书/钉钉发送。');}
 if(s.state==='note-confirm'){if(text!=='确认发送')return this.result(s,'请核对后回复“确认发送”，或回复“取消”。');await this.org.note(site,{token:s.token,recipientId:s.recipientId,text:s.text,requestId:s.id});s.state='done';s.text='';return this.result(s,'内部留言已保存，接收人可查看并标记已读；未发送外部通知。');}
 }
}
