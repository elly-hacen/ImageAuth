import os
import piexif
import numpy as np
from PIL import Image, ImageChops, ImageEnhance, ExifTags, ImageFilter
import cv2
from django.conf import settings
from keras.models import load_model
from django.core.files.storage import default_storage
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64


def detect_blur(image_path):
    image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    variance = cv2.Laplacian(image, cv2.CV_64F).var()
    return variance

def analyze_histogram(image_path):
    img = cv2.imread(image_path)
    chans = cv2.split(img)
    colors = ("b", "g", "r")
    hist_features = []

    for chan in chans:
        hist = cv2.calcHist([chan], [0], None, [256], [0, 256])
        hist = hist / hist.sum()  # normalize
        hist_features.append(hist.flatten())

    # histograms to calculate variance/entropy
    flat_hist = np.concatenate(hist_features)
    entropy = -np.sum(flat_hist * np.log2(flat_hist + 1e-7))
    
    return entropy  # higher = more diverse colors


def handle_uploaded_file(f):
    media_root = settings.MEDIA_ROOT
    os.makedirs(media_root, exist_ok=True)  

    filename = f.name.replace(" ", "_")
    upload_path = os.path.join(media_root, filename)

    with open(upload_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)
    
    return upload_path

def convert_to_ela_image(path, quality=90):
    temp_filename = os.path.join(settings.MEDIA_ROOT, f'ela_{os.path.basename(path)}.jpg')
    image = Image.open(path).convert('RGB')
    image.save(temp_filename, 'JPEG', quality=quality)
    temp_image = Image.open(temp_filename)
    ela_image = ImageChops.difference(image, temp_image)
    max_diff = max([ex[1] for ex in ela_image.getextrema()])
    if max_diff == 0: max_diff = 1
    scale = 255.0 / max_diff
    ela_image = ImageEnhance.Brightness(ela_image).enhance(scale)

    ela_combined = edge_detection(ela_image)
    ela_image.save(os.path.join(settings.MEDIA_ROOT, 'ela.jpg'))
    ela_combined.save(os.path.join(settings.MEDIA_ROOT, 'ela_canny.jpg'))

    return 'ela.jpg', 'ela_canny.jpg'

def edge_detection(image):
    image_cv = np.array(image)
    image_gray = cv2.cvtColor(image_cv, cv2.COLOR_RGB2GRAY)
    edges = cv2.Canny(image_gray, 100, 200)
    edges_rgb = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
    return Image.fromarray(edges_rgb)

def perform_ela(image_path):
    original = Image.open(image_path)
    resaved = os.path.join(settings.MEDIA_ROOT, "resaved.jpg")
    original.save(resaved, quality=95)
    resaved_img = Image.open(resaved)
    ela = ImageChops.difference(original, resaved_img)
    max_diff = max([ex[1] for ex in ela.getextrema()])
    if max_diff == 0: max_diff = 1
    scale = 255.0 / max_diff
    ela = ImageEnhance.Brightness(ela).enhance(scale)
    return np.array(ela)

def predict_image(image_path):
    from keras.models import load_model  
    import tensorflow as tf         

    model_path = os.path.join(settings.BASE_DIR, 'forgery_detection/assets/image_forgery_detection_model.keras')
    model = load_model(model_path)

    ela_array = perform_ela(image_path)
    ela_array = cv2.resize(ela_array, (128, 128))
    ela_array = ela_array / 255.0
    ela_array = np.expand_dims(ela_array, axis=0)

    prediction = model.predict(ela_array)
    return "Fake" if prediction > 0.5 else "Authentic"



def noise_analysis_process(image_path):
    image = Image.open(image_path).convert('L')
    blurred = image.filter(ImageFilter.GaussianBlur(2))
    noise_image = ImageChops.difference(image, blurred)
    noise_path = os.path.join(settings.MEDIA_ROOT, 'noise.jpg')
    noise_image.save(noise_path)
    return 'noise.jpg'

def combined_analysis(image_path):
    ela_result = predict_image(image_path)
    meta_data = extract_metadata(image_path)
    noise_path = noise_analysis_process(image_path)

    histogram_score = analyze_histogram(image_path)
    blur_score = detect_blur(image_path)


    if ela_result == "Fake" and histogram_score < 0.3 and blur_score < 50:
        return "Highly Suspicious"
    elif ela_result == "Fake":
        return "Suspicious"
    else:
        return "Likely Authentic"

def generate_heatmap(image_path):
    original = Image.open(image_path).convert('RGB')
    resaved_path = os.path.join(settings.MEDIA_ROOT, "resaved.jpg")
    original.save(resaved_path, quality=95)
    resaved = Image.open(resaved_path).convert('RGB')

    diff = ImageChops.difference(original, resaved)
    diff_np = np.array(diff.convert("L"))

    
    width, height = original.size
    dpi = 100
    figsize = (width / dpi, height / dpi)

    plt.figure(figsize=figsize, dpi=dpi)
    sns.heatmap(diff_np, cmap='inferno', cbar=True, xticklabels=False, yticklabels=False)

    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', pad_inches=0)
    plt.close()

    buffer.seek(0)
    image_png = buffer.getvalue()
    heatmap_b64 = base64.b64encode(image_png).decode('utf-8')

    return f"data:image/png;base64,{heatmap_b64}"


def extract_metadata(image_path):
    metadata = {}

    try:
        img = Image.open(image_path)
        metadata.update(img.info)

        if 'exif' in metadata:
            del metadata['exif']

        for unwanted_key in ['icc_profile', 'xmp']:
            if unwanted_key in metadata:
                del metadata[unwanted_key]

        try:
            exif_data = img._getexif()
            if exif_data:
                for tag, value in exif_data.items():
                    tag_name = ExifTags.TAGS.get(tag, tag)
                    metadata[tag_name] = value
        except Exception:
            pass

        if not metadata:
            metadata['Note'] = 'No metadata found in image.'

    except Exception as e:
        metadata['Error'] = str(e)

    return metadata
