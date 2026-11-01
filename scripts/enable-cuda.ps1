$ErrorActionPreference='Stop'
$taskRoot=Split-Path $PSScriptRoot -Parent
$taskPython=Join-Path $taskRoot '.venv-tts\Scripts\python.exe'
& $taskPython -m pip install 'torch==2.14.1+cu130' --index-url https://download.pytorch.org/whl/cu130
if ($LASTEXITCODE -ne 0) {throw 'CUDA版PyTorch安装失败'}
& $taskPython -c "import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0)); print((torch.ones(4,device='cuda')*2).cpu())"
if ($LASTEXITCODE -ne 0) {throw 'CUDA运行测试失败'}
