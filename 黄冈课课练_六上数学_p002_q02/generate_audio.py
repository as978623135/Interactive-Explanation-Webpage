# -*- coding: utf-8 -*-
"""
批量生成题目音频
读取 script.json，逐段调用火山引擎语音合成
"""
import json
import os
import subprocess
import shutil
import sys

# 配置
QUESTION_DIR = r'D:\Interactive course webpage\黄冈课课练_六上数学_第1-7页_互动课程\互动课程\p002_q02'
TTS_SCRIPT = r'C:\Users\RH_ChenFang\Doubao\chats\2026-08-24\new-chat-2\tools\volc_tts\volc_tts.py'
VOICE = 'zh_male_m191_uranus_bigtts'  # 有声阅读男声（m191）

# 多音字替换字典（仅用于音频合成，json和html中保留正确文字）
POLYPHONE_REPLACE = {
    '先列后行': '先列后航',  # 行(háng) → 航
}

def main():
    # 读取script.json
    script_path = os.path.join(QUESTION_DIR, 'script.json')
    with open(script_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    segments = data['segments']
    audio_dir = os.path.join(QUESTION_DIR, 'audio')
    
    # 备份原音频
    backup_dir = os.path.join(QUESTION_DIR, 'audio_backup_old')
    if os.path.exists(audio_dir) and not os.path.exists(backup_dir):
        shutil.copytree(audio_dir, backup_dir)
        print('✅ 已备份原音频到 audio_backup_old/')
    elif os.path.exists(audio_dir):
        print('⚠️  备份目录已存在，跳过备份')
    
    # 确保audio目录存在
    os.makedirs(audio_dir, exist_ok=True)
    
    print('=' * 60)
    print('开始批量生成音频')
    print('题目:', data['title'])
    print('发音人:', VOICE)
    print('段数:', len(segments))
    print('=' * 60)
    
    success_count = 0
    fail_count = 0
    
    for seg in segments:
        seg_id = seg['id']
        seg_name = seg['name']
        text = seg['text']
        
        # 多音字替换
        audio_text = text
        replaced = []
        for original, replacement in POLYPHONE_REPLACE.items():
            if original in audio_text:
                audio_text = audio_text.replace(original, replacement)
                replaced.append('{} → {}'.format(original, replacement))
        
        output_file = os.path.join(audio_dir, 'segment{}.mp3'.format(seg_id))
        
        print()
        print('[{}/{}] 生成: {} ({})'.format(seg_id, len(segments), seg_name, seg_id))
        print('文本长度:', len(text), '字符')
        print('文本预览:', text[:60] + '...' if len(text) > 60 else text)
        if replaced:
            print('多音字替换:', ', '.join(replaced))
        
        # 调用语音合成
        cmd = [
            sys.executable, TTS_SCRIPT,
            '--text', audio_text,
            '--output', output_file,
            '--speaker', VOICE
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', timeout=60)
            
            if result.returncode == 0 and os.path.exists(output_file):
                file_size = os.path.getsize(output_file)
                print('✅ 成功! 文件大小: {:.1f} KB'.format(file_size / 1024))
                success_count += 1
            else:
                print('❌ 失败!')
                print('stderr:', result.stderr[-500:] if result.stderr else '无')
                fail_count += 1
        except subprocess.TimeoutExpired:
            print('❌ 超时! (60秒)')
            fail_count += 1
        except Exception as e:
            print('❌ 异常:', e)
            fail_count += 1
    
    print()
    print('=' * 60)
    print('生成完成!')
    print('成功: {} 段'.format(success_count))
    print('失败: {} 段'.format(fail_count))
    print('=' * 60)
    
    if fail_count > 0:
        sys.exit(1)

if __name__ == '__main__':
    main()
