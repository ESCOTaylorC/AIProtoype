import cv2
import numpy as np
import fitz #PyMuPDF
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


def convert_pdf_to_images(pdf_path):
    """Convert PDF to image for processing."""
    try:
        # Open the PDF file
        pdf_document = fitz.open(pdf_path)
        images = []
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
            print(f"Converted page {page_num} to image: {img.size}")
        return images
    except Exception as e:
        raise Exception(f"Error converting PDF: {str(e)}")


def preprocess_image(image):
    """Preprocess image for better symbol detection."""
    try:
        # Convert PIL Image to numpy array
        if isinstance(image, Image.Image):
            image = np.array(image)
        print(f"Image after conversion to numpy array: {image.shape}")

        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        else:
            gray = image
        print(f"Image after conversion to grayscale: {gray.shape}")
        
        #Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        print(f"Image after Gaussian blur: {blurred.shape}")
        print(f"Type of blurred image: {type(blurred)}")

        #Confirm Gaussian blur processed correctly
        if blurred is None or not isinstance(blurred,np.ndarray):
                raise Exception("Blurred image is not correctly processed")

        # Apply adaptive threshold
        try:
            thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
            print(f"Image after adaptive threshold: {thresh.shape}")
        except Exception as e:
            print(f"Error during adaptive threshold: {str(e)}")
            return None
        # Apply Canny edge detection
        #edges = cv2.Canny(thresh, 100, 200)
    
        #Apply morphological transformations
        try: 
            kernel = np.ones((3,3), np.uint8)
            dilated = cv2.dilate(thresh, kernel, iterations=1)
            eroded = cv2.erode(dilated, kernel, iterations=1)
            print(f"Image after morphological transformations: {eroded.shape}")
        except Exception as e:
            print(f"Error during morpholigical transform: {str(e)}")
            return None

        return eroded
        
    except Exception as e:
        raise Exception(f"Error preprocessing image: {str(e)}")


def image_to_base64(image):
    """Convert image to base64 string."""
    try:
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)

        buffered = BytesIO()
        try: 
            image.save(buffered, format="PNG")
        except AttributeError:
            raise Exception(f"Couldn't save image: {image}")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        raise Exception(f"Error converting image to base64: {str(e)}")


def analyze_image_with_ai(image):
    """Use OpenAI to analyze the image and detect equipment."""
    try:
        base64_image = image_to_base64(image)
        #print first 100 characters of base64 string
        print(f"Base64 image: {base64_image[:100]}...")

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
            images = convert_pdf_to_images(file_path)
        else:
            # Read image file
            try:
                image = Image.open(file_path)
                # Convert to RGB if needed
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                images = [image]
            except Exception as e:
                raise Exception(f"Failed to read image file: {str(e)}")

        equipment_list = []
        for image in images:
            #Preprocess image
            preprocessed_image = preprocess_image(image)
            print(f"Preprocessed image: {preprocessed_image}")

            equipment_list.extend(analyze_image_with_ai(preprocessed_image))

        return equipment_list
    except Exception as e:
        raise Exception(f"Error processing drawing: {str(e)}")
