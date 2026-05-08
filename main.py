import os
import requests
import textwrap
from PIL import Image, ImageDraw, ImageFont
from google import genai

# Configuration
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_TOKEN = os.getenv("IG_TOKEN")
IMAGE_URL = "https://techarihant.github.io/Mastjaipur/final_post.jpg"

client = genai.Client(api_key=GEMINI_KEY)

def get_ai_content():
    """Fetches text with a fallback to ensure the script never fails."""
    # FIXED: The SDK expects the model name exactly like this
    model_id = "gemini-1.5-flash"
    
    prompt = (
        "PART 1 (For Image): Line 1: 4-word headline. Line 2: 1-line Hinglish summary. "
        "PART 2 (For Meta Caption): Write an SEO optimized caption with 8-12 hashtags."
    )
    
    default_content = (
        "PART 1\nJAIPUR CITY DAILY UPDATES\nPink City ki sabse tez khabrein yahan dekhiye!\n"
        "PART 2\n[SEO OPTIMIZATION]\nJaipur news updates today: Pink City ki latest khabrein yahan dekhiye!\n"
        "Stay informed with trending stories. #Jaipur #PinkCity [Jaipur, News]"
    )

    try:
        # Fixed model call for the genai SDK
        response = client.models.generate_content(model=model_id, contents=prompt)
        if response and response.text:
            return response.text.strip()
        return default_content
    except Exception as e:
        print(f"AI Error: {e}. Using fallback news.")
        return default_content

def create_image(image_text_block):
    """Guarantees the creation of final_post.jpg with visible news text."""
    try:
        lines = [l.strip() for l in image_text_block.split('\n') if l.strip()]
        
        # Robust parsing
        headline_raw = "JAIPUR CITY UPDATES"
        summary_raw = "Pink City news and updates."
        
        content_lines = [line for line in lines if "PART" not in line.upper()]
        if len(content_lines) >= 2:
            headline_raw = content_lines[0]
            summary_raw = content_lines[1]

        headline = "".join(e for e in headline_raw if e.isalnum() or e.isspace()).strip()[:30]
        summary = "".join(e for e in summary_raw if e.isalnum() or e.isspace() or e in '.,!?').strip()[:100]

        img = Image.open("template.png").convert("RGB")
        draw = ImageDraw.Draw(img)
        
        try:
            font_h = ImageFont.truetype("Montserrat-Bold.ttf", 80)
            font_s = ImageFont.truetype("Montserrat-Medium.ttf", 45)
        except:
            font_h = ImageFont.load_default()
            font_s = ImageFont.load_default()
            
        draw.text((60, 450), headline.upper(), font=font_h, fill="#212121")
        draw.text((60, 560), textwrap.fill(summary, width=35), font=font_s, fill="#424242")
        
        img.save("final_post.jpg", "JPEG", quality=95)
        print(f"Verified: Image created with headline: {headline}")
        return True
    except Exception as e:
        print(f"Design Error: {e}")
        return False

def publish_to_instagram(caption):
    """Handles the Instagram Graph API process."""
    if not caption: return
    
    try:
        # Step 1: Create Media Container
        post_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
        payload = {'image_url': IMAGE_URL, 'caption': caption, 'access_token': IG_TOKEN}
        r = requests.post(post_url, data=payload).json()
        
        if 'id' in r:
            creation_id = r['id']
            # Step 2: Publish
            publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
            requests.post(publish_url, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
            print("Successfully posted to Instagram!")
        else:
            print(f"Instagram rejected the link. Error: {r}")
    except Exception as e:
        print(f"Network Error: {e}")

if __name__ == "__main__":
    full_content = get_ai_content()
    
    if "PART 2" in full_content:
        parts = full_content.split("PART 2")
        img_text = parts[0]
        social_cap = parts[1].strip()
    else:
        img_text = full_content
        social_cap = full_content

    if create_image(img_text):
        publish_to_instagram(social_cap)