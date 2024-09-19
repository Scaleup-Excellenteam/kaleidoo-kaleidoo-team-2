from google.cloud import speech_v1p1beta1 as speech
import os
import io
import time
from pathlib import Path


# Load JSON key into env var
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'kaleidoo-435715-96fdd3ef71f6.json' 

src_path = "audio_sample_1.mp3" 
dst_path = f"{Path(src_path).name}_transcript.txt"

def transcribe_audio(audio_path):

    start_time = time.time()
    print("Processing...")

    client = speech.SpeechClient()

    with io.open(audio_path, 'rb') as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,  
        sample_rate_hertz=44100,  
        language_code='he-IL', 
        enable_word_time_offsets=True,
        max_alternatives=1
    )

    response = client.recognize(config=config, audio=audio)
    
    current_start = 0
    duration = 10
    current_end = duration
    chunk = []
    with open(dst_path, 'w', encoding='utf-8') as file:
        for result in response.results:
            for alternative in result.alternatives:
                for word_info in alternative.words:
                    start_time = word_info.start_time.total_seconds()
                    word = word_info.word

                    if not (start_time >= current_start and start_time < current_end):
                        file.write(f'{current_start}-{current_end}\n')
                        file.write(' '.join(chunk))
                        file.write('\n')
                        current_start = current_end
                        current_end += duration
                        chunk = []
                    chunk.append(word)

                if len(chunk) > 0:
                    file.write(f'{current_end}-EOF\n')
                    file.write(' '.join(chunk))
                    file.write('\n')

    print("Transcription complete.")
    end_time = time.time()


if __name__ == '__main__':
    transcribe_audio(src_path)