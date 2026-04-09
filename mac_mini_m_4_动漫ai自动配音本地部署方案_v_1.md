# Mac mini M4 动漫 AI 自动配音本地部署方案 v1.0

## 一、目标

构建一个可在 **Mac mini M4（32GB 内存）** 本地运行的自动动漫跨语言配音系统，实现：

输入：日漫视频（含日语原声）
输出：中文配音版本（尽量保留声优音色与情绪）

系统能力包括：

- 自动人声分离
- 自动语音识别
- 自动翻译
- 声纹迁移
- 中文语音生成
- 自动口型同步
- 视频重新合成

该方案适用于：

- MAD制作
- 二创视频
- 自动字幕组系统
- 视频多语言本地化实验

---

# 二、整体系统架构

完整 pipeline：

```
输入视频
↓
Demucs（分离人声）
↓
faster-whisper（语音识别）
↓
翻译模型（GPT / NLLB）
↓
OpenVoice（声纹迁移）
↓
XTTS v2（中文语音生成）
↓
SadTalker（口型同步）
↓
FFmpeg（视频重建）
↓
输出中文配音视频
```

推荐运行模式：

批处理流水线 + 半自动调优

---

# 三、系统环境准备

推荐系统版本：

macOS Sonoma 或更新版本

推荐 Python：

Python 3.10

安装方式：

```
brew install python@3.10
```

创建虚拟环境：

```
python3.10 -m venv anime_dubbing_env
source anime_dubbing_env/bin/activate
```

---

# 四、基础依赖安装

安装核心工具：

```
brew install ffmpeg git cmake
```

安装 PyTorch（Metal 加速）：

```
pip install torch torchvision torchaudio
```

验证 Metal 可用：

```
python -c "import torch; print(torch.backends.mps.is_available())"
```

输出 True 即表示可用

---

# 五、模块部署顺序（推荐按顺序执行）

## Step1 安装 Demucs（人声分离）

```
pip install demucs
```

使用方式：

```
demucs input.mp4
```

输出：

```
vocals.wav
```

---

## Step2 安装 faster-whisper（语音识别）

```
pip install faster-whisper
```

推荐模型：

```
large-v3
```

示例代码：

```
from faster_whisper import WhisperModel

model = WhisperModel("large-v3", device="auto")
segments, info = model.transcribe("vocals.wav")
```

输出：

时间轴字幕文本

---

## Step3 翻译模块

推荐方案一（简单稳定）：

调用 GPT API

推荐方案二（完全本地）：

```
facebook/nllb-200-distilled-600M
```

安装：

```
pip install transformers sentencepiece
```

---

## Step4 安装 OpenVoice（声纹迁移核心模块）

下载：

```
git clone https://github.com/myshell-ai/OpenVoice
cd OpenVoice
pip install -r requirements.txt
```

测试：

```
python demo.py
```

作用：

保留原声优音色特征

---

## Step5 安装 XTTS v2（跨语言语音生成）

安装：

```
pip install TTS
```

加载模型：

```
tts_models/multilingual/multi-dataset/xtts_v2
```

作用：

生成中文语音并保持角色风格

---

## Step6 安装 SadTalker（口型同步）

下载：

```
git clone https://github.com/OpenTalker/SadTalker
cd SadTalker
pip install -r requirements.txt
```

作用：

自动匹配嘴型动画

Mac M4 推荐参数：

```
--cpu_mode
```

或

```
--mps
```

---

## Step7 视频重新合成（FFmpeg）

示例命令：

```
ffmpeg -i video.mp4 -i chinese_voice.wav -c:v copy -map 0:v:0 -map 1:a:0 output.mp4
```

输出最终视频

---

# 六、推荐目录结构

建议目录布局：

```
anime_dubbing_project

models/
input/
output/
cache/
logs/
scripts/
```

推荐模型目录：

```
models/
  whisper/
  xtts/
  openvoice/
  sadtalker/
```

---

# 七、推荐自动化脚本流程

推荐执行顺序：

```
step1_split_audio.py
step2_transcribe.py
step3_translate.py
step4_voice_clone.py
step5_generate_cn_audio.py
step6_lipsync.py
step7_merge_video.py
```

建议统一入口脚本：

```
run_pipeline.py
```

实现：

```
python run_pipeline.py input.mp4
```

自动输出：

```
output_cn.mp4
```

---

# 八、推荐运行参数（Mac mini M4 优化）

Whisper：

```
compute_type="float16"
```

XTTS：

```
use_deepspeed=False
```

SadTalker：

```
--enhancer gfpgan
```

Demucs：

```
-hd
```

---

# 九、性能预估

Mac mini M4 处理速度参考：

任务 | 时间

5分钟视频完整处理 | 约6–12分钟

25分钟单集动画 | 约40–70分钟

整季动画 | 可批量运行

---

# 十、系统升级路径（推荐未来增强）

可选增强模块：

VoiceFixer

提高音质

VideoReTalking

替代 SadTalker

RVC v2

增强声优音色拟合

WhisperX

提高字幕时间轴精度

---

# 十一、最终系统能力总结

该系统可实现：

- 自动分离原声
- 自动字幕生成
- 自动翻译
- 声纹迁移
- 中文语音生成
- 自动口型同步
- 视频自动输出

适用于：

个人级动漫 AI 自动配音工作站部署

推荐长期作为：

本地视频多语言生成基础设施

