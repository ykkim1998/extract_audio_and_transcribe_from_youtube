"""
pip install yt_dlp tqdm openai-whisper
ffmpeg -version

"""
import os
import re
import yt_dlp
import whisper
import time
from tqdm import tqdm

def extract_audio_and_transcribe(youtube_list):
    """
    ��Ʃ�� URL���� ������� �����ϰ� �ؽ�Ʈ�� ��ȯ�ϴ� �Լ�
    
    Args:
        youtube_list (dict): ����� URL�� ��� ��ųʸ�
    """
    print("\n===== YouTube Audio Transcription Tool =====\n")
    
    # �� �ε� (ó�� �� ����)
    print("Loading Whisper model...")
    model = whisper.load_model("base")  # "tiny", "base", "small", "medium", "large"
    print("? Model loaded successfully!")
    
    # ��� ������ ���丮 ����
    os.makedirs("transcriptions", exist_ok=True)
    os.makedirs("audio", exist_ok=True)
    
    # youtube_list�� �׸� ó��
    for title, url in youtube_list.items():
        print(f"\n? Processing: {title}")
        print(f"? URL: {url}")
        
        # ���� �̸� ���� (������ ���ϸ����� ��ȯ)
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)  # ���� �̸��� ����� �� ���� ���� ����
        audio_file = f"audio/{safe_title}.mp3"  # .mp3 Ȯ���ڴ� �� ���� �߰�
        text_file = f"transcriptions/{safe_title}.txt"
        
        # 1�ܰ�: YouTube �������� ����� ����
        print("\n? Downloading audio...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"audio/{safe_title}",  # Ȯ���ڸ� ���⼭ �������� ����
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'progress_hooks': [lambda d: print(f"   ? {d['status']}: {d.get('_percent_str', '0%')}") 
                              if d['status'] == 'downloading' and '_percent_str' in d else None],
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            print(f"? Audio downloaded successfully: {audio_file}")
        except Exception as e:
            print(f"? Error downloading audio: {e}")
            continue
        
        # �ٿ�ε�� ���� Ȯ��
        if not os.path.exists(audio_file):
            print(f"? Warning: Expected audio file not found at {audio_file}")
            # Ȥ�� Ȯ���ڰ� �ٸ��� ����Ǿ����� Ȯ��
            possible_files = [f for f in os.listdir("audio") if f.startswith(safe_title)]
            if possible_files:
                print(f"? Found alternative file(s): {possible_files}")
                audio_file = f"audio/{possible_files[0]}"
                print(f"? Using: {audio_file}")
            else:
                print("? No suitable audio file found. Skipping transcription.")
                continue
        
        # 2�ܰ�: ������� �ؽ�Ʈ�� ��ȯ
        print("\n? Transcribing audio to text...")
        try:
            # ���� ��Ȳ �ð�ȭ
            print("   ? Processing audio... (this may take a while)")
            result = model.transcribe(audio_file)
            transcript = result["text"]
            print(f"? Transcription completed: {len(transcript)} characters")
            
            # 3�ܰ�: �ؽ�Ʈ ���Ϸ� ����
            print(f"? Saving transcription to {text_file}...")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n")  # ù ��° ��: ����
                f.write(f"{url}\n")    # �� ��° ��: URL
                f.write(f"{transcript}")  # �� ��° �ٺ���: ������ �ؽ�Ʈ
            
            print(f"? Transcription saved to: {text_file}")
            
            # �ؽ�Ʈ �Ϻ� �̸����� ���
            preview_length = min(200, len(transcript))
            print(f"\n? Transcript preview: {transcript[:preview_length]}...")
            
        except Exception as e:
            print(f"? Error transcribing audio: {e}")
            print(f"   Error details: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    # YouTube ������ ��� (����� URL)
    youtube_list = {
        "����1": "https://youtu.be/mCyY8pQDpJM?si=sd324t9fTg9EDZBM",
        "����2": "https://www.youtube.com/watch?v=4OY7ffmF9LA",
        "����3": "https://www.youtube.com/watch?v=UCI21Fmj6ts",
    }
    
    # ����
    extract_audio_and_transcribe(youtube_list)
    print("\n? All processing completed! ?")