# Start by making sure the `assemblyai` package is installed.
# If not, you can install it by running the following command:
# pip install -U assemblyai
#
# Note: Some macOS users may need to use `pip3` instead of `pip`.


# To configure: 
# - Timestamping and breakdown into portions.
# - Hebrew translation is shit btw..


import os
import assemblyai as aai
import time
from pathlib import Path


# ***Enter src audio filepath here***
src_path = "TestingSamples/audio_sample_1.mp3" 

dst_path = f"TestingOutputs/assembly_ai_{Path(src_path).name}_transcript.txt"
log_path = "TestingLogs/assembly_ai_testing_results.txt"

# Set your key as env var
os.environ['ASSEMBLYAI_API_KEY'] = '87f90576d4d3433d934be5e561fb2267' # remove this afterwards
api_key = os.getenv("ASSEMBLYAI_API_KEY")
if not api_key:
    raise ValueError("API key is not set in the environment variables")

aai.settings.api_key = api_key
aai.TranscriptionConfig(language_code="he")

# URL of the file to transcribe
#FILE_URL = "https://github.com/AssemblyAI-Community/audio-examples/raw/main/20230607_me_canadian_wildfires.mp3"

# You can also transcribe a local file by passing in a file path
FILE_URL = src_path

start_time = time.time()
print("Processing...")

config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano, language_code="he")
transcriber = aai.Transcriber(config=config)
transcript = transcriber.transcribe(FILE_URL)

with open(dst_path, 'w', encoding = 'utf-8') as file:
    if transcript.status == aai.TranscriptStatus.error:
        file.write(transcript.error) 
    else:
        file.write(transcript.text)

end_time = time.time()
print("Done Processing.")

with open(log_path, 'a', encoding = 'utf-8') as file:
        file.write(f"Time to process - {Path(src_path).name}: {end_time-start_time}\n")
