import base64
import datetime
from io import BytesIO
import os
import numpy as np
from PIL import Image
import uuid
import json
from pathlib import Path
from PIL.PngImagePlugin import PngInfo
import boto3


output_dir = os.path.abspath(os.path.join(
    os.path.dirname(__file__), '..', 'outputs', 'files'))
os.makedirs(output_dir, exist_ok=True)

def save_output_file(img: np.ndarray, image_meta: dict = None,
                     image_name: str = '', extension: str = 'png') -> str:
    """
    Save np image to file
    Args:
        img: np.ndarray image to save
        image_meta: dict of image metadata
        image_name: str of image name
        extension: str of image extension
    Returns:
        str of file name
    """
    current_time = datetime.datetime.now()
    date_string = current_time.strftime("%Y-%m-%d")

    image_name = str(uuid.uuid4()) if image_name == '' else image_name

    filename = os.path.join(date_string, image_name + '.' + extension)
    file_path = os.path.join(output_dir, filename)

    if extension not in ['png', 'jpg', 'webp']:
        extension = 'png'

    if image_meta is None:
        image_meta = {}

    meta = None
    if extension == 'png':
        meta = PngInfo()
        meta.add_text("params", json.dumps(image_meta))

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    Image.fromarray(img).save(file_path, format=extension,
                              pnginfo=meta, optimize=True)
    return Path(filename).as_posix()


def delete_output_file(filename: str):
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return
    try:
        os.remove(file_path)
    except OSError:
        print(f"Delete output file failed: {filename}")


def output_file_to_base64img(filename: str | None) -> str | None:
    if filename is None:
        return None
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return None

    img = Image.open(file_path)
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    base64_str = base64.b64encode(byte_data)
    return base64_str


def output_file_to_bytesimg(filename: str | None) -> bytes | None:
    if filename is None:
        return None
    file_path = os.path.join(output_dir, filename)
    if not os.path.exists(file_path) or not os.path.isfile(file_path):
        return None

    img = Image.open(file_path)
    output_buffer = BytesIO()
    img.save(output_buffer, format='PNG')
    byte_data = output_buffer.getvalue()
    return byte_data


def get_file_serve_url(filename: str | None) -> str | None:
    if filename is None:
        return None
    s3_client = boto3.client('s3', aws_access_key_id="", aws_secret_access_key="")
    BUCKET_NAME = ''
    FOLDER_NAME = ''
    file_path = os.path.join(output_dir, filename)
    image_name = f"generated_image_{os.urandom(4).hex()}.webp"
    s3_client.upload_file(file_path , BUCKET_NAME,FOLDER_NAME+image_name)
    static_serve_base_url = 's3-bucket-url'
    print(static_serve_base_url)
    print(file_path)
    return static_serve_base_url + image_name
