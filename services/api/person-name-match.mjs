import {pinyin} from 'pinyin-pro';
const clean=s=>s.normalize('NFKC').replace(/[\s，,:：。！？!?]/g,'');
const sounds=s=>pinyin(clean(s),{toneType:'none',type:'array',mode:'surname'}).join('|');
export function matchRecipient(people,text){
 const normalized=text.trim().replace(/^(?:请)?(?:你)?(?:帮我)?(?:在)?(?:下次)?(?:看到|见到)/,'').replace(/^(?:请)?(?:你)?(?:帮我)?(?:转告|通知|告诉|给)/,'').trim();
 const matches=[];for(const person of people){const names=[person.nickname,person.profile?.realName].filter(Boolean);let best=null;for(const name of names){const candidate=normalized.slice(0,name.length);if(clean(candidate).length!==clean(name).length)continue;const exact=candidate===name;const phonetic=!exact&&/^[\u3400-\u9fff]{2,12}$/.test(candidate)&&sounds(candidate)===sounds(name);if(!exact&&!phonetic)continue;const rest=normalized.slice(name.length);if(rest&&!/^[，,:：\s]|^(?:有|说|明天|今天|后天|的时候|时|要|请)/.test(rest))continue;const item={person,exact,name,tail:rest.replace(/^(?:的时候|时)?(?:请|要)?(?:通知|告诉|转告)?(?:他|她)?[，,:：\s]*/,'').replace(/^[，,:：说]+/,'').trim()};if(!best||exact)best=item;}if(best)matches.push(best);}
 const exact=matches.filter(x=>x.exact);return exact.length?exact:matches;
}
