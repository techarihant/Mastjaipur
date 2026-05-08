import os
import requests
from PIL import Image, ImageDraw, ImageFont
from google import genai

# Configuration from GitHub Secrets
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_TOKEN = os.getenv("IG_TOKEN")

# Replace with your actual GitHub Pages URL
IMAGE_URL = "https://techarihant.github.io/Mastjaipur/final_post.jpg"

# Initialize the new Gemini 3 Client
client = genai.Client(api_key=GEMINI_KEY)

def get_news_and_design():
    # 1. Fetch and Summarize News
    news_url = "https://timesofindia.indiatimes.com/city/jaipur" 
    
    prompt = (
        f"Summarize this Jaipur news for a social media post: {news_url}. "
        "Give me exactly two lines: "
        "Line 1: A 4-word bold headline. "
        "Line 2: A 2-line Hinglish summary."
    )

    response = client.models.generate_content(
        model="gemini-3-flash",
        contents=prompt
    )
    
    # Split the response text
    content = response.text.strip().split('\n')
    headline = content[0] if len(content) > 0 else "JAIPUR NEWS UPDATE"
    summary = content[1] if len(content) > 1 else "Stay updated with MastJaipur for latest news."

    # 2. Draw on Template
    try:
        img = Image.open("template.png")
        draw = ImageDraw.Draw(img)
        
        # Ensure these .ttf files are in your repo root
        font_h = ImageFont.truetype("Montserrat-Bold.ttf", 70)
        font_s = ImageFont.truetype("Montserrat-Medium.ttf", 40)
        
        # Draw Headline and Summary
        draw.text((60, 400), headline.upper(), font=font_h, fill="white")
        draw.text((60, 520), summary, font=font_s, fill="white")
        
        img.save("final_post.jpg", "JPEG", quality=95)
        print("Graphic Created successfully.")
        return f"{headline}\n\n{summary} #Jaipur #MastJaipur #PinkCity"
    except Exception as e:
        print(f"Design Error: {e}")
        return None

def publish_to_instagram(caption):
    if not caption:
        return

    # Step A: Create Media Container
    post_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        'image_url': IMAGE_URL,
        'caption': caption,
        'access_token': IG_TOKEN
    }
    r = requests.post(post_url, data=payload)
    result = r.json()
    
    if 'id' in result:
        creation_id = result['id']
        # Step B: Publish the Container
        publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
        requests.post(publish_url, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("Successfully posted to Instagram!")
    else:
        print(f"Instagram API Error: {result}")

if __name__ == "__main__":
    caption_text = get_news_and_design()
    # Note: On first run, ignore Instagram error until GitHub Pages updates the URL
    publish_to_instagram(caption_text)