import os
from PIL import Image
from io import BytesIO
import requests
import http.client
import mimetypes
import uuid
from dotenv import load_dotenv
load_dotenv('.env')

photoroom_api_key = os.environ.get("PHOTOROOM_API_KEY")
bg_change_url = "https://beta-sdk.photoroom.com/v1/instant-backgrounds"

def remove_image_background(input_image_path, output_image_path):
    boundary = '----------{}'.format(uuid.uuid4().hex)
    
    content_type, _ = mimetypes.guess_type(input_image_path)
    if content_type is None:
        content_type = 'application/octet-stream'

    with open(input_image_path, 'rb') as f:
        image_data = f.read()
    filename = os.path.basename(input_image_path)

    body = (
    f"--{boundary}\r\n"
    f"Content-Disposition: form-data; name=\"image_file\"; filename=\"{filename}\"\r\n"
    f"Content-Type: {content_type}\r\n\r\n"
    ).encode('utf-8') + image_data + f"\r\n--{boundary}--\r\n".encode('utf-8')
    
    conn = http.client.HTTPSConnection('sdk.photoroom.com')

    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'x-api-key': photoroom_api_key
    }

    conn.request('POST', '/v1/segment', body=body, headers=headers)
    response = conn.getresponse()

    if response.status == 200:
        response_data = response.read()
        with open(output_image_path, 'wb') as out_f:
            out_f.write(response_data)
        print("Image saved to", output_image_path)
    else:
        print(f"Error: {response.status} - {response.reason}")
        print(response.read())

    conn.close()

def generate_background(img, file_path, prompt):
    headers = {
        "Accept": "image/png, application/json",
        "x-api-key": photoroom_api_key
    }
    
    files = { "imageFile": open(img, 'rb') }
    payload = { "prompt": prompt }
    
    response = requests.post(bg_change_url, data=payload, files=files, headers=headers)
    if response.ok:
        im = Image.open(BytesIO(response.content))
        im.save(file_path, format='JPEG')
   