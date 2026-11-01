export function visualQuestionFocus(text){if(!/(?:手[里上].*(?:什么|啥|识别)|(?:我|你看我)拿的.*(?:什么|啥)|(?:衣服|衣着|这件).*(?:品牌|牌子|什么牌)|这是什么东西|你看到(?:了)?什么|识别.*(?:手机|物品)|看看.*(?:物品|手机))/.test(text))return null;return /品牌|牌子|什么牌/.test(text)?'brand':'objects';}

export function isVisionCapabilityQuestion(text){return /(?:能不能|能否|能|会不会|会|可以|不能|无法|没有|不具备|不是).{0,12}(?:识别|辨认|看懂|看见|看清).{0,8}(?:物品|东西|手机)|(?:识别|辨认).{0,8}(?:物品|东西).{0,8}(?:能力|功能)|(?:你|您).{0,6}(?:视觉能力|视觉功能)/.test(text);}
