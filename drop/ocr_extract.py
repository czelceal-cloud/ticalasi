#!/usr/bin/env python3
"""
屏幕对话记录器 — OCR提取脚本
从录制的webm视频中逐帧提取文字，去重，输出jsonl+md

依赖：pip install opencv-python pillow pytesseract
系统依赖：tesseract-ocr (brew install tesseract / apt install tesseract-ocr)
"""

import cv2
import json
import hashlib
import sys
import argparse
from pathlib import Path
from datetime import datetime

try:
    import pytesseract
except ImportError:
    print("错误: 需要 pytesseract，运行 pip install pytesseract")
    sys.exit(1)

TESSERACT_CONFIG = '--oem 3 --psm 6 -l chi_sim+eng'


def extract_frames(video_path, fps=1):
    cap = cv2.VideoCapture(str(video_path))
    video_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(video_fps / fps) if video_fps > 0 else 30
    frame_idx = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        if frame_idx % frame_interval == 0:
            yield frame_idx, frame
        frame_idx += 1
    cap.release()


def ocr_frame(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    text = pytesseract.image_to_string(binary, config=TESSERACT_CONFIG)
    return text.strip()


def text_hash(text):
    cleaned = ''.join(text.split())
    return hashlib.sha256(cleaned.encode('utf-8')).hexdigest()[:16]


def extract_sliding_new(old_lines, new_lines):
    if not old_lines:
        return new_lines
    overlap = 0
    for i in range(1, min(len(old_lines), len(new_lines)) + 1):
        if old_lines[-i:] == new_lines[:i]:
            overlap = i
    return new_lines[overlap:] if overlap > 0 else new_lines


def process_video(video_path, output_dir, source_name="未知", fps=1):
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    jsonl_path = output_dir / "record.jsonl"
    md_path = output_dir / "readable.md"

    seen_hashes = set()
    last_lines = []
    total_messages = 0

    print(f"开始处理: {video_path}")
    print(f"帧率: {fps}帧/秒, 来源: {source_name}")

    with open(jsonl_path, 'w', encoding='utf-8') as jf, \
         open(md_path, 'w', encoding='utf-8') as mf:

        mf.write(f"# 屏幕记录 {datetime.now().strftime('%Y-%m-%d')}\n\n")
        mf.write(f"## {source_name}\n\n")

        for frame_idx, frame in extract_frames(video_path, fps):
            text = ocr_frame(frame)
            if not text:
                continue

            h = text_hash(text)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)

            current_lines = [l for l in text.split('\n') if l.strip()]
            new_lines = extract_sliding_new(last_lines, current_lines)
            last_lines = current_lines

            for line in new_lines:
                line = line.strip()
                if not line:
                    continue

                record = {
                    "ts": datetime.now().isoformat(),
                    "src": source_name,
                    "text": line,
                    "frame": frame_idx,
                    "hash": text_hash(line)
                }
                jf.write(json.dumps(record, ensure_ascii=False) + '\n')
                mf.write(f"{line}\n\n")
                total_messages += 1

            if frame_idx % 50 == 0:
                print(f"  已处理帧 {frame_idx}, 已提取 {total_messages} 条消息")

    print(f"\n完成！共提取 {total_messages} 条消息")
    print(f"  JSONL: {jsonl_path}")
    print(f"  MD:    {md_path}")


def main():
    parser = argparse.ArgumentParser(description='从录屏视频提取聊天文字')
    parser.add_argument('video', help='录屏视频文件路径 (.webm)')
    parser.add_argument('-o', '--output', default='./screen-record', help='输出目录')
    parser.add_argument('-s', '--source', default='未知', help='来源App名称')
    parser.add_argument('-f', '--fps', type=int, default=1, help='每秒提取帧数 (默认1)')
    args = parser.parse_args()

    process_video(args.video, args.output, args.source, args.fps)


if __name__ == '__main__':
    main()
