### Not ready yet!!!###


from google.cloud import videointelligence_v1 as videointelligence
import io
import time


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
    start_time = time.time()
    result = operation.result(timeout=600)

    # Retrieve speech transcription result
    for annotation in result.annotation_results:
        with open(f'/home/borisg/Python/Kaleidoo/TestingOutputs/google_video_transcript.txt', 'w', encoding='utf-8') as transcript_file:
            transcript_file.write("Speech Transcription:\n")
            for speech_transcription in annotation.speech_transcriptions:
                    for alternative in speech_transcription.alternatives:
                        # Write the full transcript
                        transcript_file.write('Transcript: {}\n'.format(alternative.transcript))
                        transcript_file.write('Confidence: {}\n'.format(alternative.confidence))
                        
                        # Get start and end time for the whole transcript
                        if alternative.words:
                            start_time = alternative.words[0].start_time.total_seconds()
                            end_time = alternative.words[-1].end_time.total_seconds()
                            transcript_file.write(f"Transcript Start: {start_time}, End: {end_time}\n")
                
    print("Processing audio complete.")
    end_time = time.time()
    print(end_time-start_time)

if __name__ == '__main__':
    video_path = '/home/borisg/Python/Kaleidoo/TestingSamples/video_sample_1.mp4'  # Replace with your video file path'

    transcribe_video(video_path)
