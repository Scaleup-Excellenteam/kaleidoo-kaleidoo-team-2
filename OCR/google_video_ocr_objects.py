from google.cloud import videointelligence_v1 as videointelligence
from google.cloud import translate_v2 as translate
import os
import time
from pathlib import Path

src_path = "TestingSamples/cats.mp4"
dst_path = "TestingOutputs/google_video_to_objects.txt"
log_path = "TestingLogs/google_video_to_objects_testing_results.txt"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'kaleidoo-435715-96fdd3ef71f6.json'

def detect_objects(video_path):
    client = videointelligence.VideoIntelligenceServiceClient()

    with open(video_path, "rb") as video_file:
        input_content = video_file.read()

    features = [videointelligence.Feature.OBJECT_TRACKING]

    operation = client.annotate_video(
        request={"features": features, "input_content": input_content}
    )

    print("Processing video for object detection...")
    result = operation.result(timeout=300)

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

    return object_annotations

def translate_text(text, target_language='he'):
    client = translate.Client()

    translation = client.translate(text, target_language=target_language)
    return translation['translatedText']

def main():
    start_time = time.time()

    video_path = src_path
    object_annotations = detect_objects(video_path)

    with open(dst_path, 'w', encoding='utf-8') as file:
        for annotation in object_annotations:
            file.write(f"Detected object: {annotation['entity']} (from {annotation['start_time']}s to {annotation['end_time']}s, confidence: {annotation['confidence']})\n")
            translated_text = translate_text(annotation['entity'])
            file.write(f"Translated text: {translated_text}\n")

    end_time = time.time()

    print("Done processing.")
    print(f"Time to process = {end_time-start_time}")

    with open(log_path, 'a', encoding='utf-8') as file:
        file.write(f"Time to process - {Path(src_path).name}: {end_time-start_time}\n")

if __name__ == "__main__":
    main()
