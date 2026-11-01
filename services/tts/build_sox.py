"""针对受限 Windows 安装环境，安全解包 PyPI 官方 sox 源码以构建 wheel。"""
import hashlib, json, tarfile, urllib.request, subprocess, sys
from pathlib import Path, PurePosixPath
root = Path(__file__).resolve().parents[2]
info = json.load(urllib.request.urlopen('https://pypi.org/pypi/sox/1.5.0/json', timeout=30))
release = next(item for item in info['urls'] if item['packagetype'] == 'sdist')
raw = urllib.request.urlopen(release['url'], timeout=60).read()
if hashlib.sha256(raw).hexdigest() != release['digests']['sha256']:
    raise RuntimeError('PyPI 文件校验失败')
folder = root / '.tts-tmp' / 'sox-source'
folder.mkdir(parents=True, exist_ok=True)
archive = root / '.tts-tmp' / 'sox-source.tar.gz'
archive.write_bytes(raw)
with tarfile.open(archive) as package:
    for member in package.getmembers():
        name = PurePosixPath(member.name)
        if name.is_absolute() or '..' in name.parts or any(':' in p or '\\' in p for p in name.parts):
            raise RuntimeError('源码文件路径无效')
        if not member.isfile():
            continue
        relative = Path(*name.parts[1:])
        target = folder / relative
        if not target.resolve().is_relative_to(folder.resolve()):
            raise RuntimeError('源码路径越界')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(package.extractfile(member).read())
subprocess.run([sys.executable, '-m', 'pip', 'install', 'wheel', '--cache-dir', str(root / '.tts-tmp' / 'pip-cache')], check=True)
subprocess.run([sys.executable, 'setup.py', 'bdist_wheel'], cwd=folder, check=True)
wheel = next((folder / 'dist').glob('sox-*.whl'))
subprocess.run([sys.executable, '-m', 'pip', 'install', str(wheel)], check=True)
