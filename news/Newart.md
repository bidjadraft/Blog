<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ page.title }}</title>
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css"/>
  <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;700&display=swap" rel="stylesheet"/>
  <style>
    body {
      margin: 0;
      background: #18181b;
      color: #e5e7eb;
      font-family: "Cairo", "Segoe UI", "Arial", sans-serif;
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }
    header {
      background: #18181b;
      padding: 16px 18px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid #23232a;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: 0 2px 8px #0008;
    }
    .profile {
      display: flex;
      align-items: center;
      gap: 12px;
    }
    .profile-img {
      width: 44px;
      height: 44px;
      border-radius: 50%;
      object-fit: cover;
      border: 2px solid #23232a;
      box-shadow: 0 2px 8px #0003;
      transition: transform 0.3s ease;
    }
    .profile-img:hover {
      transform: scale(1.1);
      box-shadow: 0 4px 16px #2563ebaa;
    }
    .username {
      font-size: 1.1em;
      color: #e5e7eb;
      font-weight: 700;
      margin-left: 10px;
      font-family: "Cairo", "Segoe UI", "Arial", sans-serif;
      display: flex;
      align-items: center;
      gap: 6px;
      user-select: none;
    }
    .username .blue {
      color: #60a5fa;
      font-weight: 700;
      letter-spacing: 0.05em;
    }
    .socials {
      display: flex;
      gap: 16px;
    }
    .socials a {
      color: #a1a1aa;
      font-size: 1.6em;
      transition: color 0.3s, transform 0.3s;
      display: flex;
      align-items: center;
      justify-content: center;
      text-decoration: none;
    }
    .socials a:hover,
    .socials a:focus {
      color: #60a5fa;
      transform: scale(1.2);
      outline: none;
    }
    .article-container {
      max-width: 700px;
      width: 98vw;
      margin: 24px auto 0 auto;
      background: #23232a;
      border-radius: 18px;
      box-shadow: 0 8px 24px #0008;
      overflow: hidden;
      display: flex;
      flex-direction: column;
    }
    .article-image-wrap {
      width: 100%;
      aspect-ratio: 16/9;
      background: #23232a;
      position: relative;
      overflow: hidden;
    }
    .article-image {
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }
    .article-content {
      padding: 22px 16px 18px 16px;
      display: flex;
      flex-direction: column;
      gap: 18px;
    }
    .article-title {
      font-size: 1.35em;
      font-weight: 800;
      color: #fff;
      margin: 0 0 10px 0;
      line-height: 1.6;
      word-break: break-word;
    }
    .article-meta-row {
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 6px;
    }
    .article-meta {
      color: #60a5fa;
      font-size: 1em;
      font-weight: 600;
      text-decoration: none;
      margin-left: 2px;
      margin-right: 2px;
      user-select: none;
    }
    .article-date {
      color: #a1a1aa;
      font-size: 0.98em;
      font-weight: 400;
      user-select: none;
    }
    .article-body {
      font-size: 1.08em;
      line-height: 2;
      color: #e5e7eb;
      margin-top: 8px;
      word-break: break-word;
    }
    code {
      background: #18181b;
      color: #60a5fa;
      padding: 2px 6px;
      border-radius: 6px;
      font-family: "Fira Mono", "Consolas", "monospace";
      font-size: 0.98em;
    }
    pre {
      background: #18181b;
      color: #60a5fa;
      border-radius: 10px;
      padding: 16px;
      overflow-x: auto;
      margin: 18px 0;
      font-family: "Fira Mono", "Consolas", "monospace";
      font-size: 1em;
      direction: ltr;
      text-align: left;
      white-space: pre-wrap;
      word-break: break-word;
    }
    blockquote {
      border-right: 5px solid #2563eb;
      background: #22223a;
      color: #b3c6ff;
      margin: 18px 0;
      padding: 14px 18px;
      border-radius: 10px;
      font-style: italic;
      font-size: 1.08em;
      position: relative;
      overflow-wrap: break-word;
      word-break: break-word;
    }
    ul, ol {
      margin: 18px 0 18px 24px;
      padding: 0 20px;
      max-width: 100%;
      overflow-wrap: break-word;
      word-break: break-word;
    }
    li {
      margin-bottom: 8px;
      line-height: 2;
      word-break: break-word;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      margin: 22px 0;
      background: #23232a;
      color: #e5e7eb;
      table-layout: auto;
      word-wrap: break-word;
      overflow-x: auto;
      display: block;
    }
    th, td {
      border: 1px solid #30304a;
      padding: 10px 8px;
      text-align: center;
      vertical-align: middle;
      word-break: break-word;
    }
    th {
      background: #18181b;
      color: #60a5fa;
    }
    a {
      color: #60a5fa;
      text-decoration: underline;
      transition: color 0.2s;
      word-break: break-word;
    }
    a:hover {
      color: #fff;
    }
    hr {
      border: none;
      border-top: 1px solid #30304a;
      margin: 28px 0;
    }
    @media (max-width: 600px) {
      .article-container {
        max-width: 100vw;
        border-radius: 12px;
      }
      .article-image-wrap {
        aspect-ratio: 16/9;
      }
      .article-content {
        padding: 14px 8px 12px 8px;
        gap: 12px;
      }
      .article-title {
        font-size: 1.13em;
      }
      .article-meta {
        font-size: 0.97em;
      }
      .article-date {
        font-size: 0.9em;
      }
      pre {
        font-size: 0.93em;
        padding: 10px;
      }
    }
  </style>
</head>
<body>
  <header>
    <div class="profile">
      <img
        class="profile-img"
        src="https://randomuser.me/api/portraits/men/32.jpg"
        alt="صورة المستخدم"
      />
      <div class="username"><span>بجاد</span> <span class="blue">الأثري</span></div>
    </div>
    <nav aria-label="روابط التواصل الاجتماعي" class="socials">
      <a href="#" title="GitHub" aria-label="GitHub"><i class="fab fa-github"></i></a>
      <a href="#" title="يوتيوب" aria-label="يوتيوب"><i class="fab fa-youtube"></i></a>
      <a href="#" title="تلغرام" aria-label="تلغرام"><i class="fab fa-telegram"></i></a>
    </nav>
  </header>

  <div class="article-container">
    <div class="article-image-wrap">
      <img class="article-image" src="{{ page.image }}" alt="صورة المقال" />
    </div>
    <div class="article-content">
      <div class="article-title">{{ page.title }}</div>
      <div class="article-meta-row">
        <span class="article-meta">{{ page.category }}</span>
        <span class="article-date">{{ page.date | date: "%Y-%m-%d" }}</span>
      </div>
      <div class="article-body">
        {{ content }}
      </div>
    </div>
  </div>
</body>
</html>
