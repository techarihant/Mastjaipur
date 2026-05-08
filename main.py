import os
import requests
import textwrap
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from google import genai

# 1. Configuration
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_TOKEN = os.getenv("IG_TOKEN")
IMAGE_URL = "https://techarihant.github.io/Mastjaipur/final_post.jpg"

client = genai.Client(api_key=GEMINI_KEY)

def get_ai_content():
    """Fetches both the image text and the SEO-optimized Meta caption."""
    # Strict prompt for the image text and the social media caption
    prompt = (
        "Analyze the latest Jaipur news from TOI Jaipur. "
        "Provide the response in two parts:\n"
        "PART 1 (For Image): Line 1: 4-word headline. Line 2: 1-line Hinglish summary.\n"
        "PART 2 (For Meta Caption): Write a scroll-stopping caption following these rules: "
        "Line 1: Keyword-rich opening. Line 2-3: Value prop. Line 4: Urgency. Line 5: CTA. "
        "Include 8-12 hashtags and a final bracketed keyword list."
    )

    try:
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        if not response.text:
            raise ValueError("Empty AI response")
        return response.text.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return None

def create_image(image_text_block):
    """Renders high-contrast text onto the vibrant template."""
    try:
        # Split AI response to get image text (Part 1)
        lines = image_text_block.split('\n')
        headline = "".join(e for e in lines[0] if e.isalnum() or e.isspace()).strip()[:30]
        summary = "".join(e for e in lines[1] if e.isalnum() or e.isspace() or e in '.,!?').strip()[:100]

        img = Image.open("template.png").convert("RGBA")
        txt_layer = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)
        
        # Load fonts
        try:
            font_h = ImageFont.truetype("Montserrat-Bold.ttf", 90)
            font_s = ImageFont.truetype("Montserrat-Medium.ttf", 55)
        except:
            font_h = ImageFont.load_default()
            font_s = ImageFont.load_default()
            
        # High Contrast Colors
        headline_color = "#212121"
        summary_color = "#424242"
        
        # Wrapping
        headline_wrapped = textwrap.fill(headline.upper(), width=18)
        summary_wrapped = textwrap.fill(summary, width=35)

        # Draw Text
        draw.multiline_text((60, 420), headline_wrapped, font=font_h, fill=headline_color)
        draw.multiline_text((60, 580), summary_wrapped, font=font_s, fill=summary_color)
        
        final_img = Image.alpha_composite(img, txt_layer).convert("RGB")
        final_img.save("final_post.jpg", "JPEG", quality=95)
        print("Image created successfully.")
        return True
    except Exception as e:
        print(f"Design Error: {e}")
        return False

def publish_to_instagram(caption):
    """Sends the media and caption to Instagram API."""
    if not caption:
        return
    
    post_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media"
    payload = {
        'image_url': IMAGE_URL,
        'caption': caption,
        'access_token': IG_TOKEN
    }
    
    r = requests.post(post_url, data=payload).json()
    if 'id' in r:
        creation_id = r['id']
        publish_url = f"https://graph.facebook.com/v19.0/{IG_USER_ID}/media_publish"
        requests.post(publish_url, data={'creation_id': creation_id, 'access_token': IG_TOKEN})
        print("Instagram post successful!")
    else:
        print(f"Instagram Error: {r}")

if __name__ == "__main__":
    full_content = get_ai_content()
    if full_content:
        # Assuming AI separates Part 1 and Part 2 clearly
        parts = full_content.split("PART 2")
        image_text = parts[0].replace("PART 1", "").strip()
        social_caption = parts[1].strip() if len(parts) > 1 else image_text
        
        if create_image(image_text):
            publish_to_instagram(social_caption)