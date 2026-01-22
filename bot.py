import os
import sqlite3
import yt_dlp
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.environ.get("TOKEN", "8318468441:AAG3XbsGlSHeH5KraJkiW8j0HIuVRozaW1g")

conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
cur = conn.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS playlist (user_id INTEGER, song TEXT)")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎧 Salam! Peşəkar Musiqi Botuna xoş gəlmisiniz.\n"
        "🔹 Mahnı axtarmaq: /search <ad>\n"
        "🔹 Playlist: /playlist\n"
        "🔹 YouTube linkini göndərərək mp3 yükləyin"
    )

def search_song(query):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        results = ydl.extract_info(f"ytsearch5:{query}", download=False)
        return results['entries']

async def search_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    if not query:
        await update.message.reply_text("❌ Mahnı adını yaz: /search <ad>")
        return
    results = search_song(query)
    msg = "🔹 Nəticələr:\n"
    for i, song in enumerate(results, 1):
        msg += f"{i}. {song['title']} ({song['duration']}s)\n"
        msg += f"Link: {song['webpage_url']}\n\n"
    await update.message.reply_text(msg)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    await update.message.reply_text("⏳ Mahnı yüklənir...")

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': 'song.%(ext)s',
        'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3'}]
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        await update.message.reply_audio(audio=open("song.mp3","rb"))
        os.remove("song.mp3")
    except Exception as e:
        await update.message.reply_text(f"❌ Xəta baş verdi: {e}")

async def show_playlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    cur.execute("SELECT song FROM playlist WHERE user_id=?", (user_id,))
    songs = cur.fetchall()
    if not songs:
        await update.message.reply_text("🎵 Playlist boşdur")
    else:
        msg = "🎵 Sənin playlist:\n"
        for i, song in enumerate(songs, 1):
            msg += f"{i}. {song[0]}\n"
        await update.message.reply_text(msg)

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("search", search_command))
app.add_handler(CommandHandler("playlist", show_playlist))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))

print("🎵 Bot işləyir...")
app.run_polling()
