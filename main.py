import os
import requests
from PIL import Image, ImageDraw, ImageFont
import google.generativeai as genai

# Load environment variables (from GitHub Secrets)
GEMINI_KEY = os.getenv("GEMINI_KEY")
IG_USER_ID = os.getenv("IG_USER_ID") # Your Instagram Business Account ID
IG_TOKEN = os.getenv("IG_TOKEN")

# Setup AI
genai.configure(api_key=GEMINI_KEY)
ai_model = genai.GenerativeModel('gemini-1.5-flash')

def get_news_and_design():
    # 1. AI reads the news link you provide
    news_url = "https://example-jaipur-news.com/today" 
    prompt = f"Summarize this Jaipur news for a social media post: {news_url}. Give me: 1. A 4-word bold headline. 2. A 2-line Hinglish summary."
    response = ai_model.generate_content(prompt)
    content = response.text.split("\n")
    headline, summary = content[0], content[1]

    # 2. Draw on Template
    img = Image.open("template.png")
    draw = ImageDraw.Draw(img)
    font_h = ImageFont.truetype("Montserrat-Bold.ttf", 70)
    font_s = ImageFont.truetype("Montserrat-Medium.ttf", 40)
    
    # Draw Headline (White text)
    draw.text((60, 400), headline.upper(), font=font_h, fill="white")
    # Draw Summary
    draw.text((60, 520), summary, font=font_s, fill="white")
    
    img.save("final_post.jpg")
    print("Graphic Created successfully.")

if __name__ == "__main__":
    get_news_and_design()