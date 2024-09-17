from google.cloud import speech_v1p1beta1 as speech
import os
import io
import time
from pathlib import Path


os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'kaleidoo-435715-96fdd3ef71f6.json'

src_path = "audio_sample_1.mp3"
filename = src_path
dst_path = f"google_speech_{Path(filename).name}_transcript.txt"


def transcribe_audio(audio_path):

    print("Processing...")

    client = speech.SpeechClient()

    with io.open(audio_path, 'rb') as audio_file:
        content = audio_file.read()
    audio = speech.RecognitionAudio(content=content)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,
        sample_rate_hertz=16000,
        language_code='he-IL',
        enable_word_time_offsets=True
    )

    response = client.recognize(config=config, audio=audio)

    chunks = []
    current_chunk = []
    chunk_start_time = 0
    chunk_duration = 10 
    
    for result in response.results:
        for alternative in result.alternatives:
            for word_info in alternative.words:
                start_time = word_info.start_time.total_seconds()
                end_time = word_info.end_time.total_seconds()
                
                # Check if we need to start a new chunk
                if start_time >= chunk_start_time + chunk_duration:
                    chunks.append((chunk_start_time, chunk_end_time, ' '.join(current_chunk)))
                    current_chunk = []
                    chunk_start_time += chunk_duration
                
                current_chunk.append(word_info.word)
                chunk_end_time = end_time

    # Add the last chunk
    if current_chunk:
        chunks.append((chunk_start_time, chunk_end_time, ' '.join(current_chunk)))

    with open(dst_path, 'w') as output_file:
        for start, end, transcript in chunks:
            output_file.write(f"{start}-{end}\n")
            output_file.write(f"{transcript}\n")

    print("Transcription complete.")


if __name__ == '__main__':
    transcribe_audio(src_path)