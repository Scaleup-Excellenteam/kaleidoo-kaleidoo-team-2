from google.cloud import videointelligence_v1 as videointelligence
import io


def transcribe_video(video_path):
    # Initialize the Video Intelligence client
    video_client = videointelligence.VideoIntelligenceServiceClient()

    # Read the video file
    with io.open(video_path, 'rb') as video_file:
        input_content = video_file.read()

    # Request video analysis with speech transcription and text detection
    features = [
        videointelligence.Feature.SPEECH_TRANSCRIPTION,  # For audio transcription
        videointelligence.Feature.TEXT_DETECTION  # For on-screen text detection (OCR)
    ]

    # Configure speech transcription
    config = videointelligence.SpeechTranscriptionConfig(
        language_code='he-IL',  # Ensure the correct language code for the video
        enable_automatic_punctuation=True  # Enable punctuation in the transcript
    )
    video_context = videointelligence.VideoContext(speech_transcription_config=config)

    # Perform the video analysis
    operation = video_client.annotate_video(
        request={
            'features': features,
            'input_content': input_content,
            'video_context': video_context,
        }
    )

    print('Processing...')
    result = operation.result(timeout=600)

    # Retrieve OCR (text detection) results
    for annotation in result.annotation_results:
        with open(f'Kaleidoo/ORC/google_video_ocr.txt', 'w', encoding='utf-8') as ocr_file:
            ocr_file.write("On-screen Text (OCR):\n")
            for text_annotation in annotation.text_annotations:
                text_segment = text_annotation.segments[0]
                start_time = text_segment.segment.start_time_offset.total_seconds()
                end_time = text_segment.segment.end_time_offset.total_seconds()
                ocr_file.write(f"Text: {text_annotation.text}, Start: {start_time}, End: {end_time}\n")

    print("Processing ORC complete.")


if __name__ == '__main__':
    video_path = '/home/borisg/Python/Kaleidoo/sample.mp4'  # Replace with your video file path
    transcribe_video(video_path)




