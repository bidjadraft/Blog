import asyncio
import feedparser
import requests
from telegram import Bot
import os

# إعدادات البوت والقناة
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

def summarize_with_gemini(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    prompt = f"لخص النص في فقرة قصيرة بالعربية:\n{text}"
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        try:
            return data['candidates'][0]['content']['parts'][0]['text']
        except Exception:
            return "حدث خطأ أثناء استخراج الملخص من Gemini."
    else:
        return f"حدث خطأ في الاتصال بـ Gemini: {response.text}"

async def send_photo_with_caption(bot, photo_url, caption):
    MAX_CAPTION_LENGTH = 1000
    if len(caption) > MAX_CAPTION_LENGTH:
        caption = caption[:MAX_CAPTION_LENGTH] + "..."
    await bot.send_photo(chat_id=CHANNEL_ID, photo=photo_url, caption=caption)

async def main():
    bot = Bot(token=TOKEN)
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries
    if not entries:
        print("لا توجد منشورات في الخلاصة.")
        return

    last_sent_id = read_last_sent_id()

    # ترتيب المنشورات من الأقدم للأحدث
    entries = sorted(entries, key=lambda e: e.get('published_parsed', 0))

    # إذا لا يوجد آخر معرف، نرسل فقط أحدث منشور
    if not last_sent_id:
        entries_to_send = [entries[-1]]
    else:
        # جمع المنشورات التي لم تُرسل بعد (بعد آخر معرف)
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

        # إذا لم نجد آخر معرف في الخلاصة (مثلاً تم حذف منشور قديم)، نرسل كل المنشورات
        if not found_last:
            entries_to_send = entries

    if not entries_to_send:
        print("لا توجد منشورات جديدة للإرسال.")
        return

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

        summary = summarize_with_gemini(description)
        print(f"إرسال منشور: {post_id}")
        print("الملخص:\n", summary)

        await send_photo_with_caption(bot, photo_url, summary)
        print("تم الإرسال.")

        # تحديث آخر معرف بعد نجاح الإرسال
        write_last_sent_id(post_id)

if __name__ == "__main__":
    asyncio.run(main())
