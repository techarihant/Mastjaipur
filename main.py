import os
import requests
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai

# Load environment variables
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID")
IG_TOKEN = os.getenv("IG_TOKEN")

# Public URL where GitHub Pages will host your image
# Replace <your-username> and <repo-name> with your actual GitHub details
IMAGE_URL = "https://techarihant.github.io/Mastjaipur/final_post.jpg"

genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

def get_news_and_design():
    # 1. AI reads news (Replace with your actual Jaipur news link)
    news_url = "https://timesofindia.indiatimes.com/city/jaipur" 
    prompt = f"Summarize this Jaipur news for a social media post: {news_url}. Give me: 1. A 4-word bold headline. 2. A 2-line Hinglish summary."
    response = ai_model.generate_content(prompt)
    content = response.text.split("\n")
    headline, summary = content[0], content[1]

    # 2. Draw on Template
    img = Image.open("template.png")
    draw = ImageDraw.Draw(img)
    font_h = ImageFont.truetype("Montserrat-Bold.ttf", 70)
    font_s = ImageFont.truetype("Montserrat-Medium.ttf", 40)
    
    draw.text((60, 400), headline.upper(), font=font_h, fill="white")
    draw.text((60, 520), summary, font=font_s, fill="white")
    
    img.save("final_post.jpg")
    print("Graphic Created successfully.")
    return f"{headline}\n\n{summary} #Jaipur #MastJaipur"

def publish_to_instagram(caption):
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
        print(f"Error creating container: {result}")

if __name__ == "__main__":
    caption_text = get_news_and_design()
    # Note: In a real workflow, you need to push the image to GitHub first 
    # so the IMAGE_URL is valid before calling this.
    publish_to_instagram(caption_text)