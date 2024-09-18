from google.cloud import speech_v1p1beta1 as speech
import io
import os
from pydub import AudioSegment
from pathlib import Path
import shutil


'''
This program takes a source of an audio file of MP3 format and save it's transcription into a file.
Make sure to load the google cloud API JSON key into the GOOGLE_APPLICATION_CREDENTIALS os env.
'''

def transcript_all(src_dir, format = 'mp3'):
    next_file_start_offset = 0
    for root, dirs, files in os.walk(src_dir):
        for file in files:
            if file.endswith(format):
                os.path.join(root, file)
                transcribe_audio(os.path.join(root, file), next_file_start_offset)
                next_file_start_offset += len(AudioSegment.from_mp3(os.path.join(root, file))) // 1000 
    



def transcribe_audio(src_path, dst_dir, start_offset = 0):

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    dst_path = f"{dst_dir}{Path(src_path).name}_transcript.txt"
    chunk_duration = 10

    client = speech.SpeechClient()

    with io.open(src_path, 'rb') as audio_file:
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
    duration = chunk_duration
    current_end = duration
    chunk = []
    end_time = 0
    with open(dst_path, 'w', encoding='utf-8') as file:
        for result in response.results:
            for alternative in result.alternatives:
                for word_info in alternative.words:
                    start_time = word_info.start_time.total_seconds()
                    word = word_info.word

                    if not (start_time >= current_start and start_time < current_end):
                        file.write(f'{current_start+start_offset}-{current_end+start_offset}\n')
                        file.write(' '.join(chunk))
                        file.write('\n')
                        current_start = current_end
                        current_end += duration
                        chunk = []
                    chunk.append(word)

                # for last chunk
                if len(chunk) > 0:
                    file.write(f'{current_end+start_offset}-EOF\n')
                    file.write(' '.join(chunk))
                    file.write('\n')




def split_audio(src_path, output_dir, segment_duration = 59):

    audio = AudioSegment.from_mp3(src_path)
    total_duration = len(audio) // 1000 

    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        

    for i in range(0, total_duration, segment_duration):
        start_time = i * 1000  
        end_time = min((i + segment_duration) * 1000, len(audio))

        segment = audio[start_time:end_time]
        segment_name = f"{Path(src_path).name}_segment_{i//segment_duration + 1}.mp3"
        segment.export(os.path.join(output_dir, segment_name), format="mp3")




def clear_directory(directory):

    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        
        if os.path.isdir(item_path):
            shutil.rmtree(item_path)
        else:
            os.remove(item_path)




if __name__ == '__main__':
    src_path = 'Parser/Research/TestingSamples/audio_sample_1.mp3'
    tmp_dir = 'Parser/dev/cloud/audio_files'
    clear_directory(tmp_dir)
