import os
import requests
import time
from PIL import Image, ImageDraw, ImageFont
from google import genai

# Configuration
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_TOKEN = os.getenv("IG_TOKEN")
IMAGE_URL = "https://techarihant.github.io/Mastjaipur/final_post.jpg"

client = genai.Client(api_key=GEMINI_KEY)

def get_news_and_design():
    prompt = "Give me one major Jaipur news headline (4 words) and a 1-line summary in Hinglish."
    headline, summary = "JAIPUR CITY UPDATES", "Pink City ki latest khabrein yahan dekhiye!"

    try:
        # Using 1.5-flash for quota stability
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        if response.text:
            lines = response.text.strip().split('\n')
            headline = lines[0].replace('*', '').strip()[:30]
            summary = lines[-1].replace('*', '').strip()[:100]
    except Exception as e:
        print(f"AI Quota hit, using Safety Mode defaults: {e}")

    try:
        img = Image.open("template.png").convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # Load fonts - Ensure these .ttf files are in your GitHub repo!
        try:
            font_h = ImageFont.truetype("Montserrat-Bold.ttf", 80)
            font_s = ImageFont.truetype("Montserrat-Medium.ttf", 45)
        except:
            font_h = ImageFont.load_default()
            font_s = ImageFont.load_default()
            
        # Visible Text Color (Dark Pink/Berry) for light backgrounds
        text_color = "#D81B60" 
        
        # Headline and Summary Positioning
        draw.text((60, 450), headline.upper(), font=font_h, fill=text_color)
        draw.text((60, 560), summary, font=font_s, fill="#444444")
        
        img.save("final_post.jpg", "JPEG", quality=95)
        print("Success: final_post.jpg created with visible text.")
        return f"{headline}\n\n{summary}\n\n#Jaipur #MastJaipur #JaipurNews"
    except Exception as e:
        print(f"Design Error: {e}")
        return None

def publish_to_instagram(caption):
    if not caption: return
    
    post_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {'image_url': IMAGE_URL, 'caption': caption, 'access_token': IG_TOKEN}
    
    r = requests.post(post_url, data=payload).json()
    
    if 'id' in r:
        creation_id = r['id']
        publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
        requests.post(publish_url, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("Successfully posted to Instagram!")
    else:
        print(f"Instagram rejected the image URL. Error: {r}")

if __name__ == "__main__":
    caption_text = get_news_and_design()
    publish_to_instagram(caption_text)