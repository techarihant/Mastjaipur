import os
import requests
from PIL import Image, ImageDraw, ImageFont
from google import genai

# Configuration
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_TOKEN = os.getenv("IG_TOKEN")
IMAGE_URL = f"https://techarihant.github.io/Mastjaipur/final_post.jpg"

client = genai.Client(api_key=GEMINI_KEY)

def get_news_and_design():
    news_url = "https://timesofindia.indiatimes.com/city/jaipur" 
    prompt = "Summarize Jaipur news in 4 words for a headline and 1 sentence in Hinglish."

    headline, summary = "JAIPUR NEWS UPDATE", "Check out the latest updates from the Pink City!"

    try:
        # Using 1.5-flash as it has a more reliable free quota
        response = client.models.generate_content(model="gemini-1.5-flash", contents=prompt)
        if response.text:
            text_output = response.text.strip().split('\n')
            headline = text_output[0][:30] # Limit length
            summary = text_output[1] if len(text_output) > 1 else summary
    except Exception as e:
        print(f"AI Quota hit, using Safety Mode defaults. Error: {e}")

    try:
        img = Image.open("template.png")
        draw = ImageDraw.Draw(img)
        # Fallback to default font if Montserrat is missing
        try:
            font_h = ImageFont.truetype("Montserrat-Bold.ttf", 70)
            font_s = ImageFont.truetype("Montserrat-Medium.ttf", 40)
        except:
            font_h = ImageFont.load_default()
            font_s = ImageFont.load_default()
            
        draw.text((60, 400), headline.upper(), font=font_h, fill="white")
        draw.text((60, 520), summary, font=font_s, fill="white")
        
        img.save("final_post.jpg", "JPEG", quality=95)
        print("Success: final_post.jpg created.")
        return f"{headline}\n\n{summary}\n\n#Jaipur #MastJaipur"
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
        print(f"Instagram Error: {r}")

if __name__ == "__main__":
    caption_text = get_news_and_design()
    publish_to_instagram(caption_text)