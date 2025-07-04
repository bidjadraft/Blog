import asyncio
import feedparser
import requests
import os
import time
from telegram import Bot
from pyppeteer import launch
import json

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))
RSS_URL = "https://feed.alternativeto.net/news/all"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
LAST_ID_FILE = "last_sent_id.txt"

def read_last_sent_id():
    if not os.path.exists(LAST_ID_FILE):
        return None
    with open(LAST_ID_FILE, "r") as f:
        return f.read().strip()

def write_last_sent_id(post_id):
    with open(LAST_ID_FILE, "w") as f:
        f.write(post_id)

def classify_and_summarize_with_gemini(text, max_retries=5, wait_seconds=10):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""
صنف النص التالي إلى واحدة من الفئات التالية فقط: تطبيقات، ذكاء اصطناعي، أنظمة تشغيل، تواصل اجتماعي.
ثم لخص المقال في فقرة قصيرة وبسيطة بالعربية لا تتجاوز 30 كلمة.

النص:
{text}

أرجو أن تعيد النتيجة بهذا الشكل (JSON):
{{
  "category": "التصنيف هنا",
  "summary": "الملخص هنا"
}}
"""
    payload = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}

    for attempt in range(max_retries):
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            try:
                text_response = data['candidates'][0]['content']['parts'][0]['text']
                # محاولة استخراج JSON من النص
                result = json.loads(text_response)
                return result.get("category", "تطبيقات"), result.get("summary", "")
            except Exception as e:
                print("خطأ في تحليل JSON من Gemini:", e)
                return "تطبيقات", ""  # قيمة افتراضية
        else:
            if response.status_code == 503 or "overloaded" in response.text:
                print(f"محاولة {attempt+1} فشلت بسبب ازدحام الخدمة. إعادة المحاولة بعد {wait_seconds} ثانية...")
                time.sleep(wait_seconds)
            else:
                print(f"خطأ في الاتصال بـ Gemini: {response.text}")
                return "تطبيقات", ""
    print("فشلت كل المحاولات مع Gemini.")
    return "تطبيقات", ""

def load_html_template(path='card.html'):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def render_html(template, category, summary, image_url):
    html = template.replace('{{category}}', category)
    html = html.replace('{{summary}}', summary)
    html = html.replace('{{image_url}}', image_url)
    return html

async def html_to_image(html_content, output_path='Images/1.png'):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    browser = await launch(headless=True, args=['--no-sandbox'])
    page = await browser.newPage()
    await page.setContent(html_content, waitUntil='networkidle0')
    element = await page.querySelector('.image-box')
    await element.screenshot({'path': output_path})
    await browser.close()

async def main():
    bot = Bot(token=TOKEN)
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries
    if not entries:
        print("لا توجد منشورات في الخلاصة.")
        return

    last_sent_id = read_last_sent_id()
    entries = sorted(entries, key=lambda e: e.get('published_parsed', 0))

    if not last_sent_id:
        entries_to_send = [entries[-1]]
    else:
        entries_to_send = []
        found_last = False
        for entry in entries:
            post_id = entry.get('id') or entry.get('link')
            if not post_id:
                continue
            if found_last:
                entries_to_send.append(entry)
            elif post_id == last_sent_id:
                found_last = True
        if not found_last:
            entries_to_send = entries

    if not entries_to_send:
        print("لا توجد منشورات جديدة للإرسال.")
        return

    template = load_html_template('card.html')

    for entry in entries_to_send:
        post_id = entry.get('id') or entry.get('link')
        description = entry.get('summary', '')

        photo_url = None
        if 'media_content' in entry and len(entry.media_content) > 0:
            photo_url = entry.media_content[0]['url']
        elif 'enclosures' in entry and len(entry.enclosures) > 0:
            photo_url = entry.enclosures[0]['url']
        if not photo_url:
            photo_url = "https://via.placeholder.com/600x400.png?text=No+Image"

        category, summary = classify_and_summarize_with_gemini(description)
        if not summary:
            print("فشل التلخيص، تخطي المنشور.")
            continue

        html = render_html(template, category, summary, photo_url)
        await html_to_image(html, output_path=f'Images/{post_id}.png')

        print(f"إرسال منشور: {post_id}")
        with open(f'Images/{post_id}.png', 'rb') as img_file:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=img_file)
        print("تم الإرسال.")

        write_last_sent_id(post_id)

if __name__ == "__main__":
    asyncio.run(main())
