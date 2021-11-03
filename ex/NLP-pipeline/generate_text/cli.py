"""
Module that contains the command line app.
"""
import argparse
import argparse
import os

from google.cloud import storage
from transformers import TFGPT2LMHeadModel,  GPT2Tokenizer
import shutil


gcp_project = "ac215-project"
bucket_name = "mega-pipeline-bucket"
text_prompts = "text_prompts"
text_paragraphs = "text_paragraphs"

def download():
    print("download")
    shutil.rmtree(text_prompts,ignore_errors=False, onerror=None)
    os.makedirs(text_prompts, exist_ok=True)
    os.makedirs(text_paragraphs, exist_ok=True)

    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=text_prompts+"/")
    for blob in blobs:
        if blob.name.endswith(".txt") and (blob.name.find('.mp3')==-1):
            blob.download_to_filename(blob.name)
            print(blob.name)

def generate_text(tokenizer, model, input_text):
    inputs = tokenizer.encode(input_text, return_tensors='tf')
    outputs = model.generate(inputs, max_length=100, do_sample=True, top_k=50)
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return text

def generate():
    print("generate")
    shutil.rmtree(text_paragraphs,ignore_errors=False, onerror=None)
    os.makedirs(text_prompts, exist_ok=True)
    os.makedirs(text_paragraphs, exist_ok=True)
    # # initialize tokenizer and model from pretrained GPT2 model
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = TFGPT2LMHeadModel.from_pretrained("gpt2",pad_token_id=tokenizer.eos_token_id)
    
    prompt_files = os.listdir(text_prompts)
    for prompt_file in prompt_files:
        filename = prompt_file
        print(filename)
        prompt_path = os.path.join(text_prompts, filename)
        paragraph_path = os.path.join(text_paragraphs, filename)
     
        with open(prompt_path, 'r') as f:
            input_text = f.read()
            
        if len(input_text)!=0:
            paragraph = generate_text(tokenizer, model, input_text)
            print(paragraph)
            with open(paragraph_path,'w') as f:
                f.write(paragraph)

def upload():
    print("upload")
    os.makedirs(text_prompts, exist_ok=True)
    os.makedirs(text_paragraphs, exist_ok=True)
    storage_client = storage.Client()

    bucket = storage_client.bucket(bucket_name)

    text_files = os.listdir(text_paragraphs)

    for text_file in text_files:
        file_path = os.path.join(text_paragraphs, text_file)

        blob = bucket.blob(file_path)
        blob.upload_from_filename(file_path)


def main(args=None):

    print("Args:", args)

    if args.download:
        download()
    if args.generate:
        generate()
    if args.upload:
        upload()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(
        description='Generate text from prompt')

    parser.add_argument("-d", "--download", action='store_true',
                        help="Download text prompts from GCS bucket")

    parser.add_argument("-g", "--generate", action='store_true',
                        help="Generate a text paragraph")

    parser.add_argument("-u", "--upload", action='store_true',
                        help="Upload paragraph text to GCS bucket")

    args = parser.parse_args()

    main(args)
