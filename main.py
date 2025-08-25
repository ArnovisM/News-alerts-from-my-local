from bs4 import BeautifulSoup
import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

response = requests.get("https://zonacero.com/puerto-colombia")
yc_text = response.text

BASE_URL = "https://zonacero.com"

soup = BeautifulSoup(yc_text, "html.parser")

secondary_news = soup.select("span.field-content div.short-title-other-news h3 a")
news = []

# Noticia principal
most_recent_tag = soup.select_one("div.block-field-blocknodenewsfield-shorttitle h3 a")
most_recent_new = {
    "title": most_recent_tag.get_text(strip=True),
    "link": BASE_URL + most_recent_tag["href"] if most_recent_tag.has_attr("href") else ""
}
news.append(most_recent_new)

# Noticias secundarias
for new in secondary_news:
    news.append({
        "title": new.get_text(strip=True),
        "link": BASE_URL + new["href"] if new.has_attr("href") else ""
    })

# Cargar archivo existente
if os.path.exists("news_list.json"):
    with open("news_list.json", "r", encoding="utf-8") as f:
        news_list = json.load(f)
else:
    news_list = []

# Detectar noticias nuevas 
existing_set = {(n["title"], n["link"]) for n in news_list}
new_items = [n for n in news if (n["title"], n["link"]) not in existing_set]

# Agregar nuevas noticias al archivo
news_list.extend(new_items)
with open("news_list.json", "w", encoding="utf-8") as f:
    json.dump(news_list, f, ensure_ascii=False, indent=4)

# --- Enviar correo ---
load_dotenv(".env")
sender_email = os.getenv("email")
receiver_email = sender_email
password = os.getenv("password")

if new_items:
    subject = "Noticias nuevas de Puerto Colombia"
    body = "Nuevas noticias detectadas:\n\n" + "\n".join(
        f"- {n['title']} ({n['link']}).\n" for n in new_items
    )
else:
    subject = "Sin noticias nuevas hoy"
    body = "Hoy no se detectaron noticias nuevas en Puerto Colombia."

msg = MIMEMultipart()
msg["From"] = sender_email
msg["To"] = receiver_email
msg["Subject"] = subject
msg.attach(MIMEText(body, "plain", "utf-8"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(sender_email, password)
    server.send_message(msg)

print("Correo enviado correctamente.")