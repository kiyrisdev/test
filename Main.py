import os
import yt_dlp
import telebot
from telebot.types import Message

BOT_TOKEN = "8491539656:AAFPl6JuNJ9w9dJTydm7s8WIZ-B7sZFRvMA"
bot = telebot.TeleBot(BOT_TOKEN)

TEMP_DIR = "downloads"
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@bot.message_handler(commands=['start'])
def send_welcome(message: Message):
    bot.reply_to(
        message, 
        "Send me a url",
        parse_mode='Markdown'
    )

@bot.message_handler(func=lambda message: True)
def handle_link(message: Message):
    url = message.text.strip()
    
    # Validasi URL YouTube
    if not ('youtube.com' in url or 'youtu.be' in url):
        bot.reply_to(message, "Invalid YouTube link!* Please send a valid URL.", parse_mode='Markdown')
        return
    
    status_msg = bot.reply_to(message, "⏳*Processing...*", parse_mode='Markdown')
    
    # Opsi download TANPA FFmpeg
    ydl_opts = {
        'format': 'bestaudio/best',  # Ambil audio terbaik yang tersedia
        'outtmpl': os.path.join(TEMP_DIR, '%(title)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'extract_flat': False,
    }
    
    try:
        bot.edit_message_text(" *Downloading audio...*", message.chat.id, status_msg.message_id, parse_mode='Markdown')
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'audio')
            ext = info.get('ext', 'webm')
            
            # Cari file yang sudah didownload
            downloaded_file = None
            expected_filename = f"{title}.{ext}"
            expected_path = os.path.join(TEMP_DIR, expected_filename)
            
            if os.path.exists(expected_path):
                downloaded_file = expected_path
            else:
                # Fallback: cari file terbaru di folder
                files = [os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR) if os.path.isfile(os.path.join(TEMP_DIR, f))]
                if files:
                    downloaded_file = max(files, key=os.path.getctime)
            
            if downloaded_file and os.path.exists(downloaded_file):
                bot.edit_message_text("*Sending audio...*", message.chat.id, status_msg.message_id, parse_mode='Markdown')
                
                # Kirim file apa adanya (bisa .webm, .m4a, .opus)
                with open(downloaded_file, 'rb') as audio:
                    bot.send_audio(
                        message.chat.id,
                        audio,
                        title=title[:100],
                        performer="YT Music Downolader",
                        caption=f"*{title[:50]}*",
                        parse_mode='Markdown'
                    )
                
                # Hapus file
                os.remove(downloaded_file)
                bot.delete_message(message.chat.id, status_msg.message_id)
            else:
                raise Exception("File not found")
                
    except Exception as e:
        error_msg = f"ownload failed!*\n\n```\n{str(e)[:150]}\n```"
        bot.edit_message_text(error_msg, message.chat.id, status_msg.message_id, parse_mode='Markdown')

if __name__ == "__main__":
    print("Bot started (NO FFmpeg mode)...")
    print("Ready to download YouTube audio directly!")
    bot.infinity_polling()
