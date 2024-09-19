from google.cloud import videointelligence_v1 as videointelligence
from google.cloud import translate_v2 as translate
from pathlib import Path
from collections import defaultdict
from moviepy.editor import VideoFileClip
from audio import AudioParser


class VideoParser():

    def __init__(self):
        self.audioParser = AudioParser()




    def transcript_video_speech(self, video_path, audio_dir, audio_tmp_dir  ,dst_dir, format = 'mp3'):

        audio_path = f"{audio_dir}/{Path(src_path).stem}.mp3"

        self._mp4_to_mp3(video_path, audio_path)
        return self.audioParser.transcript_audio(audio_path, audio_tmp_dir, dst_dir)




    def transcript_video_text(self, src_path, dst_dir):
        client = videointelligence.VideoIntelligenceServiceClient()

        dst_path = f"{dst_dir}/{Path(src_path).name}_video_text_transcript.txt"


        with open(src_path, "rb") as video_file:
            input_content = video_file.read()

        features = [videointelligence.Feature.TEXT_DETECTION]

        operation = client.annotate_video(
            request={"features": features, "input_content": input_content}
        )

        result = operation.result()

        text_annotations = []
        for annotation_result in result.annotation_results:
            for text_annotation in annotation_result.text_annotations:
                for segment in text_annotation.segments:
                    start_time = segment.segment.start_time_offset.total_seconds()
                    end_time = segment.segment.end_time_offset.total_seconds()
                    text_annotations.append({
                        "start_time": start_time,
                        "end_time": end_time,
                        "text": text_annotation.text
                    })

        with open(dst_path, 'w', encoding='utf-8') as file:
            for annotation in text_annotations:
                file.write(f"{annotation['start_time']}-{annotation['end_time']}\n{self._translate_text(annotation['text'])}\n")

        return dst_path




    def transcript_video_objects(self, src_path, dst_dir):
        client = videointelligence.VideoIntelligenceServiceClient()

        dst_path = f"{dst_dir}/{Path(src_path).name}_video_objects_transcript.txt"

        with open(src_path, "rb") as video_file:
            input_content = video_file.read()

        features = [videointelligence.Feature.OBJECT_TRACKING]

        operation = client.annotate_video(
            request={"features": features, "input_content": input_content}
        )

        result = operation.result()

        object_annotations = []
        for annotation_result in result.annotation_results:
            for object_annotation in annotation_result.object_annotations:
                start_time = object_annotation.segment.start_time_offset.total_seconds()
                end_time = object_annotation.segment.end_time_offset.total_seconds()
                object_annotations.append({
                    "start_time": start_time,
                    "end_time": end_time,
                    "entity": object_annotation.entity.description,
                    "confidence": object_annotation.confidence
                })

        with open(dst_path, 'w', encoding='utf-8') as file:
            for annotation in object_annotations:
                file.write(f"{annotation['start_time']} {annotation['end_time']} {self._translate_text(annotation['entity'])}\n")

        self._group_by_name(dst_path)

        return dst_path




    def _translate_text(self, text, target_language='he'):
        client = translate.Client()

        translation = client.translate(text, target_language=target_language)
        return translation['translatedText']
    



    def _group_by_name(self, filepath):
        grouped_data = defaultdict(list)

        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                start_time, end_time, name = line.strip().split(' ', 2)
                grouped_data[name].append((float(start_time), float(end_time)))

        sorted_output = []
        for name, times in grouped_data.items():
            times_str = ' '.join(f"{start}-{end}" for start, end in times)
            sorted_output.append(f"{name} {times_str}")

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write('\n'.join(sorted_output) + '\n')




    def _mp4_to_mp3(self, mp4_path, mp3_path):
        video = VideoFileClip(mp4_path)
        audio = video.audio
        audio.write_audiofile(mp3_path, codec='mp3')
        audio.close()
        video.close()



