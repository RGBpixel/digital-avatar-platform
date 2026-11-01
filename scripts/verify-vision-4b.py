from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[1]
for item in json.loads((root/'data/vision-comparison/4B-download-manifest.json').read_text()):
 p=root/'models/vision-4b'/item['name'];h=hashlib.sha256()
 with p.open('rb') as f:
  for part in iter(lambda:f.read(4*1024*1024),b''):h.update(part)
 if p.stat().st_size!=item['size'] or h.hexdigest()!=item['sha256']:raise RuntimeError('Checksum mismatch: '+p.name)
 print('Verified',p.name,flush=True)
