from google.cloud import vision
import io
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "key.json"

def detect_text(path, dynamic_image=None):
    """Detects text in the file."""
    # pass API_KEY to client
    client = vision.ImageAnnotatorClient()

    if dynamic_image:
        content = path
    else:
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

    image = vision.Image(content=content)

    response = client.text_detection(image=image)
    return response.text_annotations[0].description
