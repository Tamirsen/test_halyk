import os
from PIL import Image
import numpy as np
from pdf2image import convert_from_path
from flask import url_for
from flask_login import login_user
from werkzeug.urls import url_parse
from .models import User
from pdf2image import convert_from_path
from PIL import Image
from .signature_extractor import extract_signature
from app import db
from app.models import Log


def login(username, password, remember_me):
    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return None
    login_user(user, remember=remember_me)
    return user

def get_redirect_page(next_page):
    if not next_page or url_parse(next_page).netloc != '':
        next_page = url_for('index')
    return next_page


def log_request_response(file_path, signatures):
    request_data = file_path
    response_data = signatures
    log_entry = Log(request=request_data, response=response_data)
    db.session.add(log_entry)
    db.session.commit()

def convert_and_extract_signature(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    pages = []

    if ext == '.pdf':
        pages = convert_from_path(file_path)
    elif ext == '.jpg':
        pages.append(Image.open(file_path))
    else:
        raise ValueError('Unsupported file format')
    
    response = []

    # Save each page as a PNG and extract signatures
    for i, page in enumerate(pages):
        # Save the image as PNG
        png_path = f"page_{i}.png"
        page.save(png_path, "PNG")

        # Load the image and convert to grayscale
        image = Image.open(png_path).convert("L")

        # Convert the image to a numpy array and extract signatures
        signature, num_signatures = extract_signature(np.array(image))

        # Save the extracted signatures as PNG
        signature_image = Image.fromarray(signature)
        extract_folder = os.getenv("EXTRACTED_SIGNATURES")
        filename = os.path.basename(file_path)  # Get the filename with extension
        filename_without_extension = os.path.splitext(filename)[0] 
        signature_path = os.path.join(extract_folder, f"{filename_without_extension}_signature_{i}.png")
        signature_image.save(signature_path)

        response.append(signature_path)
        response.append(num_signatures)
        log_request_response(file_path, response)

    return response