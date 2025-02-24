import cv2
import numpy as np
#import fitz #PyMuPDF
from pdf2image import convert_from_path
import os
import openai
import base64
from io import BytesIO
from PIL import Image
import json


"Secret API key - OpenAI gpt-4o-mini"
# Retrieve the secret from environment variables
secretapi = os.getenv('OPENAI_FREEAPI')

if secretapi:
    print("Secret retrieved successfully!")
else:
    print("Failed to retrieve the secret.")

openai.api_key = secretapi


def convert_pdf_to_image(pdf_path):
    """Convert PDF to image for processing."""
    try:
        # Convert PDF to image using pdf2image
        pop_path = r"/workspaces/AIProtoype/Poppler/Release-24.08.0-0/poppler-24.08.0/Library/bin"
        images = convert_from_path(pdf_path, poppler_path = pop_path)
        if not images:
            raise Exception("No images extracted from PDF")
        return images[0]  # Return first page
    except Exception as e:
        raise Exception(f"Error converting PDF: {str(e)}")


def preprocess_image(image):
    """Preprocess image for better symbol detection."""
    try:
        # Convert PIL Image to numpy array
        if isinstance(image, Image.Image):
            image = np.array(image)

        #print(f"Image after conversion to numpy array: {image.shape}")

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        #print(f"Image after conversion to grayscale: {gray.shape}")
        
        # Apply adaptive threshold
        _, thresh = cv2.adaptiveThreshold(gray, 127, 255, cv2.THRESH_BINARY)
        return thresh
        #print(f"Image after adaptive threshold: {thresh.shape}")
    except Exception as e:
            print(f"Error preprocessing image: {str(e)}")
     

def image_to_base64(image):
    """Convert image to base64 string."""
    try:
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        buffered = BytesIO()
        image.save(buffered, format="PNG")
        
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        raise Exception(f"Error converting image to base64: {str(e)}")


def analyze_image_with_ai(image):
    """Use OpenAI to analyze the image and detect equipment."""
    try:
        base64_image = image_to_base64(image)
        #print first 100 characters of base64 string
        #print(f"Base64 image: {base64_image[:100]}...")

        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Updated to use the free tier model
            messages=[{
                "role":
                "system",
                "content":
                """Analyze this P&ID drawing and identify equipment symbols from the provided image.
                                Return a JSON array with the following structure:
                                {
                                    "equipment": [
                                        {
                                            "type": "string",
                                            "symbol": "string",
                                            "description": "string"
                                        }
                                    ]
                                }"""
            }, {
                "role":
                "user",
                "content": [{
                    "type":
                    "text",
                    "text":
                    "Identify and list all equipment symbols and labels in this P&ID drawing."
                }, {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64_image}"
                    }
                }]
            }],
            max_tokens=1000,
            response_format={"type": "json_object"})

        result = json.loads(response.choices[0].message.content)
        return result.get("equipment", [])
    except Exception as e:
        raise Exception(f"Error analyzing image with AI: {str(e)}")


def process_pid_drawing(file_path):
    """Process P&ID drawing and return equipment list."""
    try:
        if not os.path.exists(file_path):
            raise Exception("File does not exist")

        # Determine if file is PDF or image
        file_ext = os.path.splitext(file_path)[1].lower()

        if file_ext == '.pdf':
            images = convert_pdf_to_image(file_path)
        else:
            # Read image file
            try:
                image = Image.open(file_path)
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
            except Exception as e:
                raise Exception(f"Failed to read image file: {str(e)}")

        # Analyze with AI
        equipment_list = analyze_image_with_ai(image)
        return equipment_list
    except Exception as e:
        raise Exception(f"Error processing drawing: {str(e)}")
