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
    """SDK FIX: Use the simple string 'gemini-1.5-flash'"""
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
        # The SDK adds 'models/' automatically; don't add it yourself
        response = client.models.generate_content(model=model_id, contents=prompt)
        if response and response.text:
            return response.text.strip()
        return default_content
    except Exception as e:
        print(f"AI Error: {e}. Using fallback news.")
        return default_content

def create_image(image_text_block):
    """Creates final_post.jpg with LARGE, BOLD, HIGH-CONTRAST text."""
    try:
        lines = [l.strip() for l in image_text_block.split('\n') if l.strip()]
        content_lines = [line for line in lines if "PART" not in line.upper()]
        
        headline = content_lines[0] if len(content_lines) > 0 else "JAIPUR UPDATES"
        summary = content_lines[1] if len(content_lines) > 1 else "Latest city news."

        # Load your template.png
        img = Image.open("template.png").convert("RGB")
        draw = ImageDraw.Draw(img)
        
        # LARGE FONT SIZES FOR VISIBILITY
        try:
            font_h = ImageFont.truetype("Montserrat-Bold.ttf", 95)
            font_s = ImageFont.truetype("Montserrat-Medium.ttf", 55)
        except:
            font_h = ImageFont.load_default()
            font_s = ImageFont.load_default()
            
        # Draw high-contrast charcoal text (#212121)
        draw.text((60, 420), headline.upper()[:30], font=font_h, fill="#212121")
        draw.text((60, 580), textwrap.fill(summary[:100], width=32), font=font_s, fill="#424242")
        
        img.save("final_post.jpg", "JPEG", quality=95)
        
        # Verify the file exists
        if os.path.exists("final_post.jpg"):
            print("Successfully saved final_post.jpg")
            return True
        return False
    except Exception as e:
        print(f"Design Error: {e}")
        return False

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
        print(f"Instagram Error: {r}")

if __name__ == "__main__":
    full_content = get_ai_content()
    parts = full_content.split("PART 2")
    img_text = parts[0]
    social_cap = parts[1].strip() if len(parts) > 1 else img_text
    
    if create_image(img_text):
        # We only try to post if the image was actually created
        publish_to_instagram(social_cap)