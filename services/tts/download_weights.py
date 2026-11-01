"""下载官方公开模型文件，写入项目内，不发送任何用户样音。"""
import hashlib, json, time, urllib.request
from pathlib import Path, PurePosixPath
root = Path(__file__).resolve().parents[2]
repo = 'Qwen/Qwen3-TTS-12Hz-0.6B-Base'
target = root / 'models' / 'Qwen3-TTS-12Hz-0.6B-Base'
entries = json.load(urllib.request.urlopen('https://huggingface.co/api/models/' + repo + '/tree/main?recursive=true&limit=1000', timeout=30))
files = [e for e in entries if e.get('type') == 'file']
print('官方模型文件:', len(files), '总计 MB:', round(sum(e.get('size', 0) for e in files) / 1024 ** 2), flush=True)
for entry in files:
    name = PurePosixPath(entry['path'])
    if name.is_absolute() or '..' in name.parts or any(':' in p or '\\' in p for p in name.parts):
        raise ValueError('模型文件路径无效')
    dest = target / Path(*name.parts)
    dest.parent.mkdir(parents=True, exist_ok=True)
    expected = entry.get('size')
    digest = entry.get('lfs', {}).get('oid')
    if dest.exists() and dest.stat().st_size == expected:
        if not digest or hashlib.sha256(dest.read_bytes()).hexdigest() == digest:
            continue
    partial = dest.with_name(dest.name + '.partial')
    offset = partial.stat().st_size if partial.exists() else 0
    request = urllib.request.Request('https://huggingface.co/' + repo + '/resolve/main/' + str(name), headers={'Range': 'bytes=' + str(offset) + '-'} if offset else {})
    response = urllib.request.urlopen(request, timeout=60)
    append = offset and response.status == 206
    read = offset if append else 0
    checkpoint = read
    with partial.open('ab' if append else 'wb') as stream:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            stream.write(chunk)
            read += len(chunk)
            if read - checkpoint >= 50 * 1024 ** 2:
                print(entry['path'], round(read / 1024 ** 2), '/', round(expected / 1024 ** 2), 'MB', flush=True)
                checkpoint = read
    if expected is not None and read != expected:
        raise RuntimeError('模型文件大小不匹配: ' + str(name))
    if digest and hashlib.sha256(partial.read_bytes()).hexdigest() != digest:
        raise RuntimeError('模型文件 SHA256 不匹配')
    partial.replace(dest)
    print('已完成:', entry['path'], flush=True)
print('公开模型文件下载与检查完成；实际推理仍需验收。', flush=True)
