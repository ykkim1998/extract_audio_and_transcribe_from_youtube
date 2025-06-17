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
    print("\n===== YouTube Audio Transcription Tool =====\n")
    
    print("Loading Whisper model...")
    model = whisper.load_model("base")  # "tiny", "base", "small", "medium", "large"
    print("? Model loaded successfully!")
    
    os.makedirs("transcriptions", exist_ok=True)
    os.makedirs("audio", exist_ok=True)
    
    for title, url in youtube_list.items():
        print(f"\n? Processing: {title}")
        print(f"? URL: {url}")
        
        safe_title = re.sub(r'[\\/*?:"<>|]', "", title)
        audio_file = f"audio/{safe_title}.mp3"
        text_file = f"transcriptions/{safe_title}.txt"
        
        print("\n? Downloading audio...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': f"audio/{safe_title}",
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
        
        if not os.path.exists(audio_file):
            print(f"? Warning: Expected audio file not found at {audio_file}")
            possible_files = [f for f in os.listdir("audio") if f.startswith(safe_title)]
            if possible_files:
                print(f"? Found alternative file(s): {possible_files}")
                audio_file = f"audio/{possible_files[0]}"
                print(f"? Using: {audio_file}")
            else:
                print("? No suitable audio file found. Skipping transcription.")
                continue
        
        print("\n? Transcribing audio to text...")
        try:
            print("   ? Processing audio... (this may take a while)")
            result = model.transcribe(audio_file)
            transcript = result["text"]
            print(f"? Transcription completed: {len(transcript)} characters")
            
            print(f"? Saving transcription to {text_file}...")
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(f"{title}\n")
                f.write(f"{url}\n")
                f.write(f"{transcript}")
            
            print(f"? Transcription saved to: {text_file}")
            
            preview_length = min(200, len(transcript))
            print(f"\n? Transcript preview: {transcript[:preview_length]}...")
            
        except Exception as e:
            print(f"? Error transcribing audio: {e}")
            print(f"   Error details: {type(e).__name__}: {str(e)}")

if __name__ == "__main__":
    youtube_list = {
        "Strength of Gemini each5": "https://youtu.be/JrWlVKMnmPo?si=SiyNatdDtL2nEY52",
        "Claude 4 is here": "https://youtu.be/W5tBfYIhWok?si=yC_yMzkaHB3J0jfh",
        "Gemma 3n AI": "https://youtu.be/eJFJRyXEHZ0?si=51iP37VSLkKTiRZE",
    }
    
    extract_audio_and_transcribe(youtube_list)
    print("\n? All processing completed! ?")
