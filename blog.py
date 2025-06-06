import feedparser
import requests
import os
import time
import re
from datetime import datetime, timezone

RSS_URL = "https://feed.alternativeto.net/news/all"
GEMINI_API_KEY = "AIzaSyBWmO0VrIL5HbU3RFPRRMmlDFBisoSAt2s"  # استبدل بمفتاح API الخاص بك
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
                return data['candidates'][0]['content']['parts'][0]['text'].strip()
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

def gemini_generate_title_and_summary(article_text):
    prompt = (
        "اكتب عنوانًا احترافيًا ومختصرًا باللغة العربية لهذا المقال، "
        "ثم أكتب ملخصًا لا يتجاوز فقرتين فقط، يعبر بدقة عن محتوى المقال. "
        "ابدأ بالعنوان في السطر الأول، ثم ضع الملخص في السطر الثاني، بدون أي إضافات أو شرح.\n\n"
        f"{article_text}"
    )
    return gemini_request(prompt)

def clean_title(title):
    # إزالة علامات اقتباس وأي رموز غير الحروف والأرقام والمسافات والواصلات
    title = title.replace('"', '').replace("'", '')
    title = re.sub(r'[^\w\s\-ء-ي]', '', title, flags=re.UNICODE)
    return title.strip()

def time_ago(published_iso):
    try:
        published = datetime.fromisoformat(published_iso)
    except Exception:
        try:
            published = datetime.strptime(published_iso, '%a, %d %b %Y %H:%M:%S %z')
        except Exception:
            return "غير معروف"
    now = datetime.now(timezone.utc)
    if published.tzinfo is None:
        published = published.replace(tzinfo=timezone.utc)
    diff = now - published
    seconds = diff.total_seconds()
    minutes = seconds / 60
    hours = minutes / 60
    days = hours / 24
    weeks = days / 7
    months = days / 30
    years = days / 365

    if seconds < 10:
        return "الآن"
    elif seconds < 60:
        return f"قبل {int(seconds)} ثانية"
    elif minutes < 60:
        m = int(minutes)
        if m == 1:
            return "قبل دقيقة"
        elif 2 <= m <= 10:
            return f"قبل {m} دقائق"
        else:
            return f"قبل {m} دقيقة"
    elif hours < 24:
        h = int(hours)
        if h == 1:
            return "قبل ساعة"
        elif 2 <= h <= 10:
            return f"قبل {h} ساعات"
        else:
            return f"قبل {h} ساعة"
    elif days < 7:
        d = int(days)
        if d == 1:
            return "قبل يوم"
        elif d == 2:
            return "قبل يومين"
        elif 3 <= d <= 10:
            return f"قبل {d} أيام"
        else:
            return f"قبل {d} يوم"
    elif weeks < 5:
        w = int(weeks)
        if w == 1:
            return "قبل أسبوع"
        else:
            return f"قبل {w} أسابيع"
    elif months < 12:
        mo = int(months)
        if mo == 1:
            return "قبل شهر"
        else:
            return f"قبل {mo} أشهر"
    else:
        y = int(years)
        if y == 1:
            return "قبل سنة"
        else:
            return f"قبل {y} سنوات"

def save_markdown(title, image_url, category, time_relative, content):
    file_slug = slugify(title)
    md_filename = f"{NEWS_FOLDER}/{file_slug}.md"
    if file_exists(md_filename):
        print(f"الملف موجود مسبقًا: {md_filename}")
        return None, None
    front_matter = f"""---
layout: default
title: {title}
image: "{image_url}"
category: {category}
date: {time_relative}
---

{content}
"""
    with open(md_filename, "w", encoding="utf-8") as f:
        f.write(front_matter)
    print(f"تم إنشاء الملف: {md_filename}")
    url = f"https://bidjadraft.github.io/blog/{file_slug}.html"
    return md_filename, url

def main():
    create_news_folder()
    feed = feedparser.parse(RSS_URL)
    entries = feed.entries
    if not entries:
        print("لا توجد منشورات في الخلاصة.")
        return

    for entry in entries[:5]:  # عدّل العدد حسب رغبتك
        description = entry.get('summary', '')
        pub_date_raw = entry.get('published', datetime.now(timezone.utc).isoformat())

        time_relative = time_ago(pub_date_raw)

        image_url = None
        if 'media_content' in entry and len(entry.media_content) > 0:
            image_url = entry.media_content[0]['url']
        elif 'enclosures' in entry and len(entry.enclosures) > 0:
            image_url = entry.enclosures[0]['url']
        if not image_url:
            image_url = "https://via.placeholder.com/600x400.png?text=No+Image"

        result = gemini_generate_title_and_summary(description)
        if not result:
            print("فشل توليد العنوان والملخص، تجاهل المنشور.")
            continue

        lines = result.split('\n', 1)
        title = clean_title(lines[0]) if lines else "عنوان غير متوفر"
        summary = lines[1].strip() if len(lines) > 1 else ""

        category = "التقنية"

        md_file, url = save_markdown(
            title=title,
            image_url=image_url,
            category=category,
            time_relative=time_relative,
            content=summary
        )
        if md_file:
            print(f"رابط المقال: {url}")
        else:
            print("تخطى المقال لأنه موجود مسبقًا.")

if __name__ == "__main__":
    main()
