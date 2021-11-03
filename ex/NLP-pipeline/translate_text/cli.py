"""
Module that contains the command line app.
"""
import argparse
import os
import shutil
from google.cloud import storage
from googletrans import Translator

gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
text_paragraphs = "text_paragraphs"
text_translated = "text_translated"

def download():
    print("download")
    shutil.rmtree(text_paragraphs,ignore_errors=False, onerror=None)
    os.makedirs(text_paragraphs, exist_ok=True)
    os.makedirs(text_translated, exist_ok=True)

    
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=text_paragraphs+"/")
    for blob in blobs:

        if blob.name.endswith(".txt") and (blob.name.find('.mp3')==-1):
            blob.download_to_filename(blob.name)
            print(blob.name)


def translate():
    print("translate")
    
    os.makedirs(text_paragraphs, exist_ok=True)
    os.makedirs(text_translated, exist_ok=True)

    translator = Translator()
    text_files = os.listdir(text_paragraphs)
    for text_file in text_files:
        filename = text_file.replace('.txt','')
        text_path = os.path.join(text_paragraphs, filename+'.txt')
        translation_path = os.path.join(text_translated, filename+'.txt')
        with open(text_path, 'r') as f:
            input_text = f.read()
         

        if(len(input_text)!=0):
        
            input_text = input_text.replace('.','. ')
            results = translator.translate(input_text, src="en", dest="fr")
  
            with open(translation_path,'w') as f:
                f.write(results.text)

            

def upload():
    print("upload")
    os.makedirs(text_paragraphs, exist_ok=True)
    os.makedirs(text_translated, exist_ok=True)
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    text_files = os.listdir(text_paragraphs)

    for text_file in text_files:
        file_path = os.path.join(text_translated, text_file)

        blob = bucket.blob(file_path)
        blob.upload_from_filename(file_path)

def main(args=None):

    print("Args:", args)

    if args.download:
        download()
    if args.translate:
        translate()
    if args.upload:
        upload()

if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(
        description='Translate English to French')

    parser.add_argument("-d", "--download", action='store_true',
                        help="Download text paragraphs from GCS bucket")

    parser.add_argument("-t", "--translate", action='store_true',
                        help="Translate text")

    parser.add_argument("-u", "--upload", action='store_true',
                        help="Upload translated text to GCS bucket")

    args = parser.parse_args()

    main(args)
