"""
Module that contains the command line app.
"""
import argparse
import os
import io
from google.cloud import storage
from google.cloud import speech
from tempfile import TemporaryDirectory
import ffmpeg
import shutil

gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
input_audios = "input_audios"
text_prompts = "text_prompts"

def download():
    print("download")
    shutil.rmtree(input_audios,ignore_errors=False, onerror=None)
    os.makedirs(input_audios, exist_ok=True)
    os.makedirs(text_prompts, exist_ok=True)

    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=input_audios+"/")
    for blob in blobs:
        if blob.name.endswith(".mp3"):
            blob.download_to_filename(blob.name)
            print(blob.name)

def transcribe():
    print("transcribe")
    # Instantiates a client
    shutil.rmtree(text_prompts,ignore_errors=False, onerror=None)
    os.makedirs(input_audios, exist_ok=True)
    os.makedirs(text_prompts, exist_ok=True)
    client = speech.SpeechClient()

    audio_files= os.listdir(input_audios)
    for audio_file in audio_files:
        file = audio_file.replace('.mp3','')
        text_file = file+'.txt'
        audio_path = os.path.join(input_audios, audio_file)
        text_path = os.path.join(text_prompts, text_file)

        with TemporaryDirectory() as audio_dir:
            flac_path = os.path.join(audio_dir,"audio.flac")
            stream = ffmpeg.input(audio_path)
            stream = ffmpeg.output(stream, flac_path)
            ffmpeg.run(stream, quiet=True)
            
            with io.open(flac_path, "rb") as audio_file:
                content = audio_file.read()
            # Transcribe
            audio = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                language_code="en-US"
            )
            operation = client.long_running_recognize(
                config=config, audio=audio)
            response = operation.result(timeout=90)
            # print(response)
            for result in response.results:
                text = result.alternatives[0].transcript
                #print("Transcript: {}".format(text))

                with open(text_path, 'w') as f:
                    f.write(text)

def upload():
    print("upload")
    os.makedirs(input_audios, exist_ok=True)
    os.makedirs(text_prompts, exist_ok=True)

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    text_files = os.listdir(text_prompts)

    for text_file in text_files:
        file_path = os.path.join(text_prompts, text_file)

        blob = bucket.blob(file_path)
        blob.upload_from_filename(file_path)


def main(args=None):

    print("Args:", args)

    if args.download:
        download()
    if args.transcribe:
      
        transcribe()
    if args.upload:
        upload()

if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(
        description='Transcribe audio file to text')

    parser.add_argument("-d", "--download", action='store_true',
                        help="Download audio files from GCS bucket")

    parser.add_argument("-t", "--transcribe", action='store_true',
                        help="Transcribe audio files to text")

    parser.add_argument("-u", "--upload", action='store_true',
                        help="Upload transcribed text to GCS bucket")

    args = parser.parse_args()

    main(args)
