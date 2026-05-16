# 落字 / DropText

屏幕上的字，落下来，留住。
Words on screen, dropped and kept.

通用聊天App网页端自动滚屏录制 + OCR提取工具。独立程序，不属于任何项目。

## 用途

你在任何聊天App（扣子/微信/飞书/Telegram...）正常浏览对话，工具自动滚屏+录屏，事后OCR提取成文字。

零权限、零适配、零封号风险。

## 两个阶段

### 阶段一：录制（Chrome扩展）

1. Chrome打开聊天网页
2. 点扩展图标 → 开始录制+滚屏
3. 工具自动向上匀速滚动并录屏
4. 到顶自动停止，下载webm视频

### 阶段二：提取（Python脚本）

```bash
pip install opencv-python pillow pytesseract
# 系统还需装 tesseract-ocr

python ocr_extract.py chat-record-xxx.webm -s 扣子 -o ./output
```

输出 `record.jsonl`（机器可读）+ `readable.md`（人可读）

## 文件结构

```
chrome-extension/     ← Chrome扩展，5个文件
  manifest.json
  popup.html
  popup.js
  background.js
  content.js
ocr_extract.py        ← 事后OCR提取脚本
需求清单.md            ← 完整需求文档
```

## 安装Chrome扩展

1. 打开 chrome://extensions/
2. 开启开发者模式
3. 加载已解压的扩展程序 → 选 chrome-extension 文件夹
4. 打开扣子/微信网页版，点扩展图标开始
