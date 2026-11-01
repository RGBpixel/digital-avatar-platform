export const topicLabels={general:'综合',humor:'幽默趣闻',sports:'体育',games:'游戏',travel:'旅游',entertainment:'娱乐',technology:'科技',culture:'文化'};
const patterns={humor:/幽默|搞笑|趣闻|趣事|笑话|段子|有趣|萌宠|啼笑皆非/,games:/游戏|电竞|电玩|主机|任天堂|Steam|PS5|Xbox|王者荣耀|原神|黑神话|塞尔达|英雄联盟/i,sports:/体育|足球|篮球|网球|乒乓|羽毛球|奥运|比赛|联赛|世界杯|NBA|跑步|游泳|骑行/i,travel:/旅游|旅行|景区|文旅|露营|徒步|度假|自驾|游玩|出游/,entertainment:/娱乐|电影|电视剧|综艺|演唱会|音乐|明星|追剧|影视/,technology:/科技|人工智能|机器人|编程|数码|航天|芯片/,culture:/文化|展览|博物馆|阅读|非遗|书法|美术/};
export function classifyTopic(text){return Object.entries(patterns).find(([,p])=>p.test(text))?.[0]||'general';}
export function interestTopics(person){if(!person?.personalizationConsent||person.preferences?.source!=='user-confirmed')return [];const text=person.preferences.taste||'';return Object.entries(patterns).filter(([,p])=>text.split(/[，,。；;、]/).some(part=>p.test(part)&&!/(不喜欢|不爱|不感兴趣|讨厌|别聊|不要聊)/.test(part))).map(([key])=>key);}
export function rankItems(items,topics=[]){return items.map((item,index)=>({item,index,score:topics.includes(item.topic)?10:0})).sort((a,b)=>b.score-a.score||a.index-b.index).map(x=>x.item);}
export const lightEnough=text=>!/(死亡|遇难|爆炸|袭击|诈骗|战争|灾难|伤亡|性侵|自杀|病逝)/.test(text);
