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
    유튜브 URL에서 오디오를 추출하고 텍스트로 변환하는 함수
    
    Args:
        youtube_list (dict): 제목과 URL이 담긴 딕셔너리
    """
    print("\n===== YouTube Audio Transcription Tool =====\n")
    
    # 모델 로드 (처음 한 번만)
    print("Loading Whisper model...")
    model = whisper.load_model("base")  # "tiny", "base", "small", "medium", "large"
    print("? Model loaded successfully!")
    
    # 결과 저장할 디렉토리 생성
    os.makedirs("transcriptions", exist_ok=True)
    os.makedirs("audio", exist_ok=True)
    
    # youtube_list의 항목 처리
    for title, url in youtube_list.items():
        print(f"\n? Processing: {title}")
        print(f"? URL: {url}")
        
        # 파일 이름 설정 (안전한 파일명으로 변환)
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)  # 파일 이름에 사용할 수 없는 문자 제거
        audio_file = f"audio/{safe_title}.mp3"  # .mp3 확장자는 한 번만 추가
        text_file = f"transcriptions/{safe_title}.txt"
        
        # 1단계: YouTube 비디오에서 오디오 추출
        print("\n? Downloading audio...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"audio/{safe_title}",  # 확장자를 여기서 지정하지 않음
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
        
        # 다운로드된 파일 확인
        if not os.path.exists(audio_file):
            print(f"? Warning: Expected audio file not found at {audio_file}")
            # 혹시 확장자가 다르게 저장되었는지 확인
            possible_files = [f for f in os.listdir("audio") if f.startswith(safe_title)]
            if possible_files:
                print(f"? Found alternative file(s): {possible_files}")
                audio_file = f"audio/{possible_files[0]}"
                print(f"? Using: {audio_file}")
            else:
                print("? No suitable audio file found. Skipping transcription.")
                continue
        
        # 2단계: 오디오를 텍스트로 변환
        print("\n? Transcribing audio to text...")
        try:
            # 진행 상황 시각화
            print("   ? Processing audio... (this may take a while)")
            result = model.transcribe(audio_file)
            transcript = result["text"]
            print(f"? Transcription completed: {len(transcript)} characters")
            
            # 3단계: 텍스트 파일로 저장
            print(f"? Saving transcription to {text_file}...")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n")  # 첫 번째 줄: 제목
                f.write(f"{url}\n")    # 두 번째 줄: URL
                f.write(f"{transcript}")  # 세 번째 줄부터: 추출한 텍스트
            
            print(f"? Transcription saved to: {text_file}")
            
            # 텍스트 일부 미리보기 출력
            preview_length = min(200, len(transcript))
            print(f"\n? Transcript preview: {transcript[:preview_length]}...")
            
        except Exception as e:
            print(f"? Error transcribing audio: {e}")
            print(f"   Error details: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    # YouTube 동영상 목록 (제목과 URL)
    youtube_list = {
        "제목1": "https://youtu.be/mCyY8pQDpJM?si=sd324t9fTg9EDZBM",
        "제목2": "https://www.youtube.com/watch?v=4OY7ffmF9LA",
        "제목3": "https://www.youtube.com/watch?v=UCI21Fmj6ts",
    }
    
    # 실행
    extract_audio_and_transcribe(youtube_list)
    print("\n? All processing completed! ?")