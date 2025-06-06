import feedparser
import requests
import os
import time
import re
from datetime import datetime

RSS_URL = "https://feed.alternativeto.net/news/all"
GEMINI_API_KEY = "AIzaSyBWmO0VrIL5HbU3RFPRRMmlDFBisoSAt2s"  # ضع مفتاح API الخاص بك هنا
NEWS_FOLDER = "news"

def slugify(text):
    text = re.sub(r'[^\w\s-]', '', text, flags=re.UNICODE)
    text = re.sub(r'[-\s]+', '-', text).strip('-_')
    return text.lower()

def create_news_folder():
    os.makedirs(NEWS_FOLDER, exist_ok=True)

def file_exists(filename):
    return os.path.exists(filename)

def gemini_request(prompt, max_retries=10, wait_seconds=10):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
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

    for attempt in range(max_retries):
        response = requests.post(url, json=payload, headers=headers)
        try:
            data = response.json()
        except Exception:
            print("Response Text:", response.text)
            return None

        if response.status_code == 200:
            try:
                answer = data['candidates'][0]['content']['parts'][0]['text']
                return answer.strip()
            except Exception:
                print("لم يتم العثور على نص في الرد.")
                return None
        elif response.status_code == 503 or "overloaded" in response.text:
            print(f"محاولة {attempt+1} فشلت بسبب ازدحام الخدمة. إعادة المحاولة بعد {wait_seconds} ثانية...")
            time.sleep(wait_seconds)
        else:
            print("Response JSON:", data)
            print("حدث خطأ في الاتصال بـ Gemini.")
            return None
    print("فشلت كل المحاولات مع Gemini.")
    return None

def gemini_extract_title(article_text):
    prompt = (
        "استخرج عنوانًا احترافيًا بالعربية لهذا المقال، مختصر ومعبر، يتراوح طوله بين 7 إلى 12 كلمة، "
        "بدون استخدام علامات ترقيم مثل النقطتين أو الشرطتين. "
        "أعطني العنوان فقط بدون شرح أو خيارات إضافية:\n"
        f"{article_text}"
    )
    title = gemini_request(prompt)
    if title:
        title = title.replace(":", "").replace("–", "").replace("-", "").strip()
    return title

def gemini_paraphrase_article(article_text):
    prompt = (
        "أعد صياغة هذا المقال إلى العربية بتعبير مختلف واحترافي مع الحفاظ على المعنى، "
        "مع تقديم ملخص أطول وأكثر تفصيلاً، مناسب للنشر. "
        "أعطني نصًا واحدًا فقط بدون شرح أو خيارات إضافية:\n"
        f"{article_text}"
    )
    return gemini_request(prompt)

def save_markdown(title, image_url, category, date, content):
    file_slug = slugify(title)
    md_filename = f"{NEWS_FOLDER}/{date}-{file_slug}.md"
    if file_exists(md_filename):
        print(f"الملف موجود مسبقًا: {md_filename}")
        return None, None
    front_matter = f"""---
layout: default
title: {title}
image: {image_url}
category: {category}
date: {date}
permalink: /blog/news/{date}-{file_slug}/
---

{content}
"""
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(front_matter)
    print(f"تم إنشاء الملف: {md_filename}")
    url = f"https://bidjadraft.github.io/blog/news/{date}-{file_slug}/"
    return md_filename, url

def main():
    create_news_folder()
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries
    if not entries:
        print("لا توجد منشورات في الخلاصة.")
        return

    for entry in entries[:5]:  # عدّل العدد حسب رغبتك
        original_title = entry.get('title', '')
        description = entry.get('summary', '')
        pub_date_raw = entry.get('published', datetime.now().strftime('%a, %d %b %Y %H:%M:%S +0000'))
        try:
            pub_date = datetime.strptime(pub_date_raw, '%a, %d %b %Y %H:%M:%S %z').date().isoformat()
        except Exception:
            pub_date = datetime.now().date().isoformat()

        image_url = None
        if 'media_content' in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0]['url']
        elif 'enclosures' in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0]['url']
        if not image_url:
            image_url = "https://via.placeholder.com/600x400.png?text=No+Image"

        title_ar = gemini_extract_title(original_title)
        if not title_ar:
            print("فشل استخلاص العنوان، تجاهل المنشور.")
            continue

        article_ar = gemini_paraphrase_article(description)
        if not article_ar:
            print("فشل إعادة صياغة المقال، تجاهل المنشور.")
            continue

        category = "التقنية"  # التصنيف ثابت

        md_file, url = save_markdown(
            title=title_ar,
            image_url=image_url,
            category=category,
            date=pub_date,
            content=article_ar
        )
        if md_file:
            print(f"رابط المقال: {url}")
        else:
            print("تخطى المقال لأنه موجود مسبقًا.")

if __name__ == "__main__":
    main()
