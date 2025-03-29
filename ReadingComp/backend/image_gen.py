from dotenv import load_dotenv
from google import genai
from google.genai import types
from backend.prompts import IMAGE_PROMPT
from PIL import Image
from io import BytesIO
import os
import base64

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise ValueError("GOOGLE_API_KEY not found in .env file or environment variables.")


def generate_sketch_cartoon(story_content: str):
    """
    Generates a black and white sketch cartoon image based on a given story content.

    Args:
    story_content: The text content of the story.
    api_key: Your Google Cloud API key.

    Returns:
    A PIL Image object representing the generated image.
    """
    # Craft a detailed prompt for the image generation model
    prompt = IMAGE_PROMPT.format(story_content=story_content)

    client = genai.Client(api_key=GOOGLE_API_KEY)

    response = client.models.generate_content(
        model="models/gemini-2.0-flash-exp-image-generation",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=['Text', 'Image']
        )
    )

    for part in response.candidates[0].content.parts:
        if part.text is not None:
          print(part.text)
        elif part.inline_data is not None:
            print(f"Mime type of image is {part.inline_data.mime_type}")
            # Try to decode the image data
            try:
                image_data = base64.b64decode(part.inline_data.data)
                return image_data
            except Exception as e:
                print(f"Error decoding image data: {e}")
                pass
            return part.inline_data.data

    print("Image not found in the response.")
    return None
