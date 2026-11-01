const wakeForms=s=>s.replace(/[寶貝謝見]/g,c=>({'寶':'宝','貝':'贝','謝':'谢','見':'见'}[c]));
export function matchWake(text,phrase){const clean=s=>String(s||'').normalize('NFKC').replace(/[\s\p{P}\p{S}]/gu,'').toLowerCase();const key=wakeForms(clean(phrase)),heard=wakeForms(clean(text));return key.length>=2&&heard.startsWith(key);}
export function idleSeconds(value){const n=Number(value);return Number.isFinite(n)?Math.min(60,Math.max(2,n)):5;}

export const wakeReplies=["我在，有什么事吗？", "听到啦，你说！", "有什么需要我帮忙的吗？", "在呢，今天想聊点什么？", "来啦来啦，我听着呢！", "嗯，我在，请说吧。", "收到呼唤，有什么安排？", "你一叫，我就来啦！", "在这儿呢，需要搭把手吗？", "耳朵准备好了，你说！", "今天有什么新鲜事呀？", "我在，慢慢说，不着急。", "有什么小任务交给我呀？", "你好呀，很高兴听到你。", "到！有什么可以帮你的？", "我上线啦，聊点什么？", "听见啦，等你开口呢。", "我在这儿，陪你聊一会儿。", "有什么问题，咱们一起想想？", "叫我啦？今天想做点什么？"];
export function wakeQuestion(text,phrase){if(!matchWake(text,phrase))return null;const clean=s=>s.normalize('NFKC').replace(/[\s\p{P}\p{S}]/gu,'').toLowerCase();const key=wakeForms(clean(phrase));let end=0;for(const character of text){end+=character.length;if(wakeForms(clean(text.slice(0,end)))===key)break;}return text.slice(end).replace(/^[\s\p{P}\p{S}]+/u,'').trim();}
export function chooseWakeReply(value,previous='',random=Math.random){const list=[...new Set(String(value||'').split(/\r?\n/).map(s=>s.trim()).filter(s=>s&&s.length<=80))].slice(0,40);const pool=list.length?list:wakeReplies;const choices=pool.length>1?pool.filter(s=>s!==previous):pool;return choices[Math.min(choices.length-1,Math.max(0,Math.floor(random()*choices.length)))];}

export function isEndSpeech(text,configured='谢谢\n再见\n谢谢再见'){const clean=s=>String(s||'').normalize('NFKC').replace(/[\s\p{P}\p{S}]/gu,'').toLowerCase();const heard=clean(text);return String(configured||'谢谢\n再见\n谢谢再见').split(/[\n,，]/).map(clean).filter(Boolean).some(word=>heard===word);}
export function sentencePause(value){const n=Number(value);return Number.isFinite(n)&&n>=400&&n<=1500?n:600;}
