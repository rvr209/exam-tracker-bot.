import os
import requests
from bs4 import BeautifulSoup
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ✅ Use environment variable for your token (Render secret)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Safety check — stops the app if token is missing
if not BOT_TOKEN:
    raise ValueError("⚠️ BOT_TOKEN environment variable not set on Render.")

EXAM_SITES = {
    "IIT JAM": "https://jam.iitm.ac.in/",
    "CUET PG": "https://pgcuet.samarth.ac.in/",
    "GATE": "https://gate.iitkgp.ac.in/",
    "CSIR NET": "https://csirnet.nta.ac.in/",
    "DBT BET": "https://dbt.nta.ac.in/",
    "BITSAT": "https://bitsadmission.com/",
    "ICAR AIEEA PG": "https://icar.nta.ac.in/",
    "NEST": "https://www.nestexam.in/"
}

def get_latest_updates(url, limit=5):
    try:
        res = requests.get(url, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")
        links = soup.find_all("a", href=True)
        updates = []
        for link in links:
            text = link.get_text(strip=True)
            href = link["href"]
            if text and any(k in text.lower() for k in
                            ["notice", "result", "admit", "announcement", "notification"]):
                if not href.startswith("http"):
                    href = url.rstrip("/") + "/" + href.lstrip("/")
                updates.append(f"📢 *{text}*\n🔗 [View Notice]({href})")
            if len(updates) >= limit:
                break
        return updates if updates else ["No recent updates found."]
    except Exception as e:
        return [f"⚠️ Error fetching data: {e}"]

async def check_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != "@Coockmeth":  # only you can use it
        await update.message.reply_text("⛔ Access denied.")
        return

    await update.message.reply_text("🔍 *Checking latest exam updates...*", parse_mode="Markdown")

    messages = []
    for exam, link in EXAM_SITES.items():
        updates = get_latest_updates(link)
        formatted = "\n\n".join(updates)
        msg = f"🎓 *{exam}*\n🗓️ {datetime.now().strftime('%d %b %Y')}\n\n{formatted}"
        messages.append(msg)

    reply_text = "\n\n━━━━━━━━━━━━━━━\n\n".join(messages)
    await update.message.reply_text(reply_text, parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("check", check_command))
    print("✅ Bot is running. Type /check in Telegram.")
    app.run_polling()

if __name__ == "__main__":
    main()
