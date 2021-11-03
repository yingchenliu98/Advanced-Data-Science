"""
Module that contains the command line app.
"""
import argparse
import os
import shutil
from google.cloud import storage
from google.cloud import texttospeech

gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
output_audios = "output_audios"
text_translated = "text_translated"



def download():
    print("download")
   # shutil.rmtree(text_translated,ignore_errors=False, onerror=None)
    os.makedirs(text_translated, exist_ok=True)
    os.makedirs(output_audios, exist_ok=True)

    
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=text_translated+"/")
    for blob in blobs:
        if blob.name.endswith(".txt") and (blob.name.find(".mp3")==-1):
            blob.download_to_filename(blob.name)
            print(blob.name)


def synthesis():
    print("synthesis")
    shutil.rmtree(output_audios,ignore_errors=False, onerror=None)
    os.makedirs(text_translated, exist_ok=True)
    os.makedirs(output_audios, exist_ok=True)

    # Instantiates a client
    client = texttospeech.TextToSpeechClient()
    text_files= os.listdir(text_translated)

    for text_file in text_files:
        
        filename = text_file.replace('.txt','')
        filename = filename.replace('.mp3','')
        text_file = filename + '.txt'
        
        audio_file = filename + '.mp3'
        text_path = os.path.join(text_translated, text_file)
        audio_path = os.path.join(output_audios, audio_file)
      
        with open(text_path, 'r') as f:
            input_text = f.read()
        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=input_text)
        # Build the voice request
        language_code = "fr-FR"
        voice = texttospeech.VoiceSelectionParams(
            language_code=language_code, ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )

        # Save the audio file
        with open(audio_path, "wb") as out:
            # Write the response to the output file.
            out.write(response.audio_content)



def upload():
    print("upload")
    os.makedirs(text_translated, exist_ok=True)
    os.makedirs(output_audios, exist_ok=True)

    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    audio_files = os.listdir(output_audios)

    for audio_file in audio_files:
        file_path = os.path.join(output_audios, audio_file)

        blob = bucket.blob(file_path)
        blob.upload_from_filename(file_path)


def main(args=None):

    print("Args:", args)

    if args.download:
        download()
    if args.synthesis:
        synthesis()
    if args.upload:
        upload()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(
        description='Synthesis audio from text')

    parser.add_argument("-d", "--download", action='store_true',
                        help="Download paragraph of text from GCS bucket")

    parser.add_argument("-s", "--synthesis", action='store_true',
                        help="Synthesis audio")

    parser.add_argument("-u", "--upload", action='store_true',
                        help="Upload audio file to GCS bucket")

    args = parser.parse_args()

    main(args)
