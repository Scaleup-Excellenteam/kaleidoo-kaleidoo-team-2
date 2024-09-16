from google.cloud import storage, speech_v1p1beta1 as speech
import io
import os
import time
from pathlib import Path


# Load JSON key into env var
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'kaleidoo-435715-96fdd3ef71f6.json' 

# ***Enter src audio filepaths here***
src_path = "TestingSamples/audio_sample_1.mp3" 
gcs_uri = f'gs://kaleidoo_bucket/audio_sample_2.mp3'   # For files longer that 1 min                      

dst_path = f"TestingOutputs/gogole_speech_{Path(src_path).name}_transcript.txt"
log_path = "TestingLogs/google_speech_testing_results.txt"

def transcribe_audio(audio_path):

    start_time = time.time()
    print("Processing...")

    client = speech.SpeechClient()

    # For local audio files
    #    with io.open(audio_path, 'rb') as audio_file:
    #        content = audio_file.read()
    #    audio = speech.RecognitionAudio(content=content)

    # For cloud audio files
    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.MP3,  # Change based on your audio format
        sample_rate_hertz=16000,  # Adjust based on your audio file's sample rate
        language_code='he-IL'  # Set the language code (Hebrew in this case)
    )

    # For local audio files
    # operation = client.recognize(config=config, audio=audio)

    # For cloud files
    operation = client.long_running_recognize(config=config, audio=audio)

    print("Waiting for operation to complete...")
    response = operation.result(timeout=600)  # Adjust timeout as needed

    with open(dst_path, 'w', encoding='utf-8') as file:
        for result in response.results:
            for alternative in result.alternatives:
                file.write('Transcript: {}\n'.format(alternative.transcript))

    print("Transcription complete.")
    end_time = time.time()


    # Set filename for output (local or cloud)
    filename = gcs_uri

    with open(log_path, 'a', encoding = 'utf-8') as file:
        file.write(f"Time to process - {Path(filename).name}: {end_time-start_time}\n")
        file.write('Confidence: {}\n\n'.format(alternative.confidence))


if __name__ == '__main__':
    transcribe_audio(gcs_uri)