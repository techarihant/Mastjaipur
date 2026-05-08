import os
import requests
from PIL import Image, ImageDraw, ImageFont
from google import genai

# 1. Load Environment Variables from GitHub Secrets
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_TOKEN = os.getenv("IG_TOKEN")

# Update your GitHub details here
GITHUB_USERNAME = "techarihant"
REPO_NAME = "Mastjaipur"
IMAGE_URL = f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/final_post.jpg"

# Initialize the Google GenAI Client
client = genai.Client(api_key=GEMINI_KEY)

def get_news_and_design():
    # news_url can be updated to any Jaipur news source
    news_url = "https://timesofindia.indiatimes.com/city/jaipur" 
    
    prompt = (
        f"Summarize this Jaipur news for a social media post: {news_url}. "
        "Give me exactly two lines: "
        "Line 1: A 4-word bold headline in English. "
        "Line 2: A 2-line summary in Hinglish."
    )

    try:
        # Using gemini-2.0-flash to avoid 404 versioning errors
        response = client.models.generate_content(
            model="gemini-2.0-flash", 
            contents=prompt
        )
        
        text_output = response.text.strip().split('\n')
        headline = text_output[0]
        summary = text_output[1] if len(text_output) > 1 else ""
    except Exception as e:
        print(f"AI Generation Error: {e}")
        return None

    # Design Image
    try:
        img = Image.open("template.png")
        draw = ImageDraw.Draw(img)
        
        # Ensure these .ttf files are in your repository root
        font_h = ImageFont.truetype("Montserrat-Bold.ttf", 70)
        font_s = ImageFont.truetype("Montserrat-Medium.ttf", 40)
        
        # Draw text onto the template
        draw.text((60, 400), headline.upper(), font=font_h, fill="white")
        draw.text((60, 520), summary, font=font_s, fill="white")
        
        img.save("final_post.jpg", "JPEG", quality=95)
        print("Image saved successfully.")
        return f"{headline}\n\n{summary}\n\n#Jaipur #MastJaipur #PinkCity"
    except Exception as e:
        print(f"Drawing Error: {e}")
        return None

def publish_to_instagram(caption):
    if not caption:
        return

    # Create the media container on Instagram
    post_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        'image_url': IMAGE_URL,
        'caption': caption,
        'access_token': IG_TOKEN
    }
    r = requests.post(post_url, data=payload).json()
    
    if 'id' in r:
        creation_id = r['id']
        # Publish the container to the live feed
        publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
        requests.post(publish_url, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("Successfully posted to Instagram!")
    else:
        print(f"Instagram Error: {r}")

if __name__ == "__main__":
    caption_text = get_news_and_design()
    publish_to_instagram(caption_text)