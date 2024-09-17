from google.cloud import videointelligence_v1 as videointelligence
from google.cloud import translate_v2 as translate
import os
import time
from pathlib import Path


src_path = "TestingSamples/video_sample_3.mp4"
dst_path = "TestingOutputs/video_sample_3.txt"
log_path = "TestingLogs/google_video_to_text_testing_results.txt"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'kaleidoo-435715-96fdd3ef71f6.json'

def detect_text(video_path):
    client = videointelligence.VideoIntelligenceServiceClient()

    with open(video_path, "rb") as video_file:
        input_content = video_file.read()

    features = [videointelligence.Feature.TEXT_DETECTION]

    operation = client.annotate_video(
        request={"features": features, "input_content": input_content}
    )

    print("Processing video for text detection...")
    result = operation.result(timeout=300)

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

    return text_annotations

def translate_text(text, target_language='he'):
    client = translate.Client()

    translation = client.translate(text, target_language=target_language)
    return translation['translatedText']

def main():

    start_time = time.time()

    video_path = src_path
    text_annotations = detect_text(video_path)

    with open(dst_path, 'w', encoding='utf-8') as file:
        for annotation in text_annotations:
            file.write(f"Detected text: {annotation['text']} (from {annotation['start_time']}s to {annotation['end_time']}s)\n")
            translated_text = translate_text(annotation['text'])
            file.write(f"Translated text: {translated_text}\n")

    end_time = time.time()

    print("Done processing.")
    print(f"Time to process = {end_time-start_time}")

    with open(log_path, 'a', encoding = 'utf-8') as file:
        file.write(f"Time to process - {Path(src_path).name}: {end_time-start_time}\n")

if __name__ == "__main__":
    main()