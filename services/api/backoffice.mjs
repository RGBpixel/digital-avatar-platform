export class BackofficeCards{
 constructor(reception,organization,faces){this.r=reception;this.org=organization;this.faces=faces;}
 async create(site,b){
  this.r.site(site);if(b.consent!==true)throw Error('请确认已告知本人并获得资料保存同意');if(!['internal','external'].includes(b.affiliation))throw Error('请选择内部或来访人员');
  const admin=b.admin===true,existing=this.org.site(site).admins.length;
  if(admin&&b.affiliation!=='internal')throw Error('管理员必须是内部人员');
  if(admin){if(b.simulationConfirmed!==true)throw Error('请明确确认本机模拟管理配置');if(existing>=3)throw Error('最多配置3位管理员');if(existing)this.org.auth(site,b.token,true);}
  const person=this.r.register(site,{nickname:b.nickname,category:b.affiliation==='internal'?'employee':'visitor',affiliation:b.affiliation,consent:true,retentionDays:b.retentionDays||30});
  try{this.r.update(site,person.id,{confirmed:true,profile:b.profile||{},selfRole:b.selfRole||'',preference:b.preference||'',personalizationConsent:b.personalizationConsent===true});
   if(admin){if(!existing)await this.org.bootstrap(site,{personId:person.id,simulationConfirmed:true});else{const card=await this.org.submit(site,person.id);await this.org.approve(site,{cardId:card.id,token:b.token,decision:'approve'});await this.org.manager(site,{personId:person.id,token:b.token,enabled:true});}}
   else if(b.affiliation==='internal')await this.org.submit(site,person.id);
   return {person:this.r.person(site,person.id),admin,mode:'mock-admin',verified:false,message:admin?'管理员卡片已在本机试用后台配置；未完成真实账号鉴权':'人员卡片已保存；内部人员需审核，来访人员没有单位权限'};
  }catch(e){await this.org.forget(site,person.id);this.r.remove(site,person.id);throw e;}
 }
 async remove(site,b){this.r.person(site,b.personId);if(b.confirmed!==true)throw Error('请明确确认删除当前卡片');if(this.org.site(site).admins.length)this.org.auth(site,b.token,true);await this.faces.forget(site,b.personId);await this.org.forget(site,b.personId);return this.r.remove(site,b.personId);}
}
