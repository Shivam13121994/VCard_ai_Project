from flask import Flask, jsonify
import boto3
from PIL import Image
import os
import re


app = Flask(__name__)

# Initialize Textract client
def initialize_textract_client():
    return boto3.client('textract',
                        aws_access_key_id='',
                        aws_secret_access_key='',
                        region_name='')

# Function to detect text in an image
def detect_text(image_bytes):
    try:
        textract_client = initialize_textract_client()
        response = textract_client.detect_document_text(Document={'Bytes': image_bytes})
        return response
    except Exception as e:
        return {'error': str(e)}

def load_image_from_folder(image_name):
    try:
        image_path = os.path.join(image_name)
        with open(image_path, 'rb') as file:
            image_bytes = file.read()
        return image_bytes
    except Exception as e:
        return None

def extract_text_by_block_type(response, block_type):
    extracted_text = []
    for item in response['Blocks']:
        if item['BlockType'] == block_type:
            text = item['Text']
            lines = text.split('\n')
            extracted_text.extend(lines)
    return extracted_text


def extract_phone_numbers(text_list):
    phone_numbers = []
    for text in text_list:
        matches = re.findall(r'\+?\d{1,3}[-\s]?\d{3,4}[-\s]?\d{4,}', text)
        phone_numbers.extend(matches)
    return phone_numbers


def extract_names(text_list):
    names = []
    for text in text_list:
        words = text.split()
        if any(word.istitle() for word in words):
            names.append(text)
    return names

def extract_emails(text_list):
    emails = []
    for text in text_list:
        if '@' in text and '.' in text:
            emails.append(text)
    return emails
@app.route('/textract_text', methods=['POST'])
def read_text():
    image_name = "card1.jpeg"
    image_bytes = load_image_from_folder(image_name)
    if not image_bytes:
        return jsonify({'message': 'Failed to load image'})
    
    response = detect_text(image_bytes)
    
    if 'error' in response:
        return jsonify({'message': 'Text detection failed'})

    
    block_type = 'LINE'  
    extracted_text = extract_text_by_block_type(response, block_type)
    phone_numbers = extract_phone_numbers(extracted_text)
    names = extract_names(extracted_text)
    emails = extract_emails(extracted_text)


    print(" ")
    print("extracted_text: ",extracted_text)
    # print(" ")
    # print("Names:", names)
    # print(" ")
    # print("10-digit numbers:", phone_numbers)
    # print(" ")
    # print("Emails:", emails)
    # print(" ")

   
    return jsonify({'message': 'Text extracted successfully', 'text': extracted_text})

# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg'}

if __name__ == '__main__':
    app.run(debug=True)
