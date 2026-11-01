// Relative endpoint threshold affects recording boundaries, never speaker acceptance.
export function speechThreshold(base,peak,adaptive=true){base=Number(base)||.002;if(!adaptive||peak<base*6)return base;return Math.max(base,Math.min(.03,peak*.3));}
