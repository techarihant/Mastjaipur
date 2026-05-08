import os
import requests
import textwrap
from PIL import Image, ImageDraw, ImageFont
from google import genai

# 1. Configuration
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_TOKEN = os.getenv("IG_TOKEN")
IMAGE_URL = "https://techarihant.github.io/Mastjaipur/final_post.jpg"

client = genai.Client(api_key=GEMINI_KEY)

def get_ai_content():
    """Fetches text with a fallback to ensure the script never fails empty."""
    prompt = (
        "PART 1 (For Image): Line 1: 4-word headline. Line 2: 1-line Hinglish summary. "
        "PART 2 (For Meta Caption): Write an SEO optimized caption with 8-12 hashtags."
    )
    
    # Default safety content if API fails
    default_content = (
        "PART 1\nJAIPUR CITY DAILY UPDATES\nPink City ki sabse tez khabrein yahan dekhiye!\n"
        "PART 2\n[SEO OPTIMIZATION]\nJaipur news updates today: Pink City ki latest khabrein yahan dekhiye!\n"
        "Stay informed with trending stories. #Jaipur #PinkCity [Jaipur, News]"
    )

    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        return response.text.strip() if response.text else default_content
    except Exception as e:
        print(f"AI Error (using fallback): {e}")
        return default_content

def create_image(image_text_block):
    """Guarantees the creation of final_post.jpg."""
    try:
        lines = [line for line in image_text_block.split('\n') if line.strip()]
        # Extracting safety-cleaned text
        headline = "".join(e for e in lines[0] if e.isalnum() or e.isspace()).replace("PART 1", "").strip()[:30]
        summary = "".join(e for e in lines[1] if e.isalnum() or e.isspace() or e in '.,!?').strip()[:100]

        img = Image.open("template.png").convert("RGB")
        draw = ImageDraw.Draw(img)
        
        try:
            font_h = ImageFont.truetype("Montserrat-Bold.ttf", 80)
            font_s = ImageFont.truetype("Montserrat-Medium.ttf", 45)
        except:
            font_h = ImageFont.load_default()
            font_s = ImageFont.load_default()
            
        # Draw high-contrast text
        draw.text((60, 450), headline.upper(), font=font_h, fill="#212121")
        draw.text((60, 560), textwrap.fill(summary, width=35), font=font_s, fill="#424242")
        
        img.save("final_post.jpg", "JPEG", quality=95)
        print("File verified: final_post.jpg created.")
        return True
    except Exception as e:
        print(f"Design Error: {e}")
        return False

def publish_to_instagram(caption):
    if not caption: return
    post_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {'image_url': IMAGE_URL, 'caption': caption, 'access_token': IG_TOKEN}
    r = requests.post(post_url, data=payload).json()
    print(f"Instagram Response: {r}")

if __name__ == "__main__":
    full_content = get_ai_content()
    parts = full_content.split("PART 2")
    img_text = parts[0]
    social_cap = parts[1] if len(parts) > 1 else img_text
    
    if create_image(img_text):
        publish_to_instagram(social_cap)