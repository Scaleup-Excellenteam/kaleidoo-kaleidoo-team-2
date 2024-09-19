from google.cloud import speech_v1p1beta1 as speech
import io
import os
from pydub import AudioSegment
from pathlib import Path
import shutil


class AudioParser():

    def __init__(self):
        self.suffix = '_audio_speech_transcript.txt"'

    def transcript_audio(self, filepath, tmp_dir, dst_dir):
        self._split_audio(filepath, tmp_dir)
        self._transcript_all(tmp_dir, dst_dir)
        self._clear_directory(tmp_dir)
        return f"{dst_dir}/{Path(filepath).name}{self.suffix}"




    def _transcript_all(self, tmp_dir, dst_dir, format = 'mp3'):
        next_file_start_offset = 0
        for root, dirs, files in os.walk(tmp_dir):
            for file in files:
                if file.endswith(format):
                    src_path = os.path.join(root, file)
                    self._transcript_audio_file(src_path, dst_dir, next_file_start_offset)
                    next_file_start_offset += len(AudioSegment.from_mp3(src_path)) // 1000 
        



    def _transcript_audio_file(self, filepath, dst_dir, offset = 0):

        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)

        dst_path = f"{dst_dir}/{Path(filepath).name}{self.suffix}"
        delim = '_segment'
        if delim in dst_path:
            dst_path = dst_path.split(delim)[0] + self.suffix

        chunk_duration = 10

        client = speech.SpeechClient()

        with io.open(filepath, 'rb') as audio_file:
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
        with open(dst_path, 'a', encoding='utf-8') as file:
            for result in response.results:
                for alternative in result.alternatives:
                    for word_info in alternative.words:
                        start_time = word_info.start_time.total_seconds()
                        word = word_info.word
                        end_word_time = word_info.end_time.total_seconds()

                        if not (start_time >= current_start and start_time < current_end):
                            file.write(f'{current_start+offset}-{current_end+offset}\n')
                            file.write(' '.join(chunk))
                            file.write('\n')
                            current_start = current_end
                            current_end += duration
                            chunk = []
                        chunk.append(word)

                    # for last chunk
                    if len(chunk) > 0:
                        file.write(f'{current_start+offset}-{current_end+offset}\n')
                        file.write(' '.join(chunk))
                        file.write('\n')




    def _split_audio(self, src_path, tmp_dir, segment_duration = 59):

        audio = AudioSegment.from_mp3(src_path)
        total_duration = len(audio) // 1000 

        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)
            
        for i in range(0, total_duration, segment_duration):
            start_time = i * 1000  
            end_time = min((i + segment_duration) * 1000, len(audio))

            segment = audio[start_time:end_time]
            segment_name = f"{Path(src_path).stem}_segment_{i//segment_duration + 1}.mp3"
            segment.export(os.path.join(tmp_dir, segment_name), format="mp3")




    def _clear_directory(self, tmp_dir):

        if not os.path.exists(tmp_dir):
            print(f"Directory {tmp_dir} does not exist.")
            return

        for item in os.listdir(tmp_dir):
            item_path = os.path.join(tmp_dir, item)
            
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)