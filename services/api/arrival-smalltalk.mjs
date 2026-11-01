import {interestTopics} from './info-interests.mjs';
import {validateObservation,observationGreeting} from './local-vision.mjs';
export const greetings={internal:[
'，回来啦！今天想先忙正事，还是和我聊两句？','，见到您真好。今天过得顺不顺？','，欢迎回来！今天有没有什么开心的小事？','，来啦！需要我帮您捋一捋今天的安排吗？','，又碰面啦，今天想聊点轻松的，还是聊工作？','，欢迎回来！忙的时候我随时待命，不忙就聊两句。','，今天也给自己留点轻松的时间吧，有空聊两句吗？','，欢迎回来！今天有什么值得期待的事？','，来啦！想听个轻松的小段子，还是先忙您的？','，见到您我就来精神了！今天有什么想分享的？','，欢迎回来！要不要给今天定个小目标？','，回来啦！今天想从什么话题聊起？'
],external:[
'，您好，又见面啦！最近过得怎么样？','，欢迎您来！今天有什么需要我搭把手的？','，见到您很高兴，今天想聊点什么？','，欢迎回来！想先办正事，还是轻松聊两句？','，您好！今天一路过来顺利吗？','，又碰面啦！最近有没有什么开心的事？','，欢迎您！需要帮忙随时说，也可以陪您聊两句。','，您好！今天有什么新鲜事想分享吗？'
]};
export function chooseGreeting(person,history=[],random=Math.random,{memory,observation}={}){const bank=greetings[person.affiliation==='internal'?'internal':'external'].map((text,index)=>({text:person.nickname+text,index,kind:'general'}));
 const add=(index,kind,text)=>bank.push({index,kind,text:person.nickname+'，'+text});
 ['今天感觉怎么样，忙不忙？','最近有没有让您开心的小事？','今天想轻松聊聊，还是先忙手头的事？','今天有什么值得期待的安排吗？'].forEach((x,i)=>add(100+i,'wellbeing',x));
 if(memory&&person.personalizationConsent){const topicText={games:'最近有玩什么喜欢的游戏吗？',travel:'最近有没有想去走走的地方？',sports:'最近有关注喜欢的比赛，或者自己运动一下吗？',entertainment:'最近有没有觉得好看的电影或节目？',technology:'最近有什么感兴趣的科技话题？',humor:'要不要聊点轻松有趣的？',culture:'最近有没有读到喜欢的书，或看了什么展览？'};const keys=Object.keys(topicText);for(const key of interestTopics(person))if(topicText[key])add(200+keys.indexOf(key),'interest',topicText[key]);
 const topics=[[/旅游|旅行|出游/,'上次聊到旅行，最近有什么新想法吗？'],[/游戏|电竞/,'上次聊到游戏，最近有新的体验吗？'],[/电影|追剧|综艺/,'上次聊到影视，后来有看到喜欢的作品吗？'],[/足球|篮球|运动|健身/,'上次聊到运动，最近还想聊聊这个吗？'],[/读书|阅读|看书/,'上次聊到阅读，最近有新的发现吗？']];const questions=(memory.chatHistory||[]).filter(t=>!/(提醒|通知|转告|取消|不喜欢|别聊|不想聊)/.test(t.question)).map(t=>t.question);topics.forEach(([pattern,question],i)=>{if(questions.some(q=>pattern.test(q)))add(300+i,'memory',question);});}
 if(observation){const clean=validateObservation(observation),text=observationGreeting(clean);if(text)add(400+(clean.objects.length?1:0),'visual',text);}
 const recent=new Set(history.slice(-6));let available=bank.filter(x=>!recent.has(x.index));const last=history.at(-1),lastKind=last>=400?'visual':last>=300?'memory':last>=200?'interest':last>=100?'wellbeing':'general';const kinds=[...new Set(available.map(x=>x.kind))].filter(x=>x!==lastKind);const options=kinds.length?kinds:[...new Set(available.map(x=>x.kind))];const kind=options[Math.min(options.length-1,Math.floor(random()*options.length))];available=available.filter(x=>x.kind===kind);const chosen=available[Math.min(available.length-1,Math.floor(random()*available.length))]||bank[0];return chosen;}
