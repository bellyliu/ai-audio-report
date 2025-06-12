import os
import shutil
import threading
import requests
import telebot
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from datetime import datetime
import io

# === Configurations ===
BOT_TOKEN = "7364547559:AAFUKuYmi6RbDu5XMyt21SWE9883VtUnkjw"
FASTAPI_UPLOAD_URL = "http://192.168.100.74:8000/upload/"
UPLOAD_DIR = "/home/haris/Documents/File_haris/Project_with_koh_bellyy/project-1/upload"
ALLOWED_AUDIO_EXTENSIONS = ('.mp3', '.m4a', '.aac', '.opus')
os.makedirs(UPLOAD_DIR, exist_ok=True)

# === FastAPI Server ===
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": f"File '{file.filename}' uploaded successfully!"}

def start_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=8000)

# === Telegram Bot ===
bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(content_types=['audio', 'voice', 'document'])
def handle_audio(message):
    try:
        # Get file info and extension
        if message.audio:  # Check if the message contains an audio file
            file_info = bot.get_file(message.audio.file_id)  # Get file info from Telegram servers
            original_name = message.audio.file_name or "audio"  # Get the original file name or use 'audio'
            ext = os.path.splitext(original_name)[1]  # Extract the file extension
        elif message.voice:  # Check if the message contains a voice message
            file_info = bot.get_file(message.voice.file_id)  # Get file info for the voice message
            original_name = "voice"  # Set a default name for voice messages
            ext = ".opus"  # Voice messages are in .opus format
        elif message.document:  # Check if the message contains a document
            file_info = bot.get_file(message.document.file_id)  # Get file info for the document
            original_name = message.document.file_name or "document"  # Get the document's file name or use 'document'
            ext = os.path.splitext(original_name)[1]  # Extract the file extension
        else:  # If the message does not contain a supported file type
            bot.reply_to(message, "❌ Unsupported file type.")  # Inform the user about unsupported file type
            return  # Exit the function

        if ext.lower() not in ALLOWED_AUDIO_EXTENSIONS:  # Check if the file extension is allowed
            bot.reply_to(message, "⚠️ Only MP3, M4A, AAC, or OPUS files are allowed.")  # Inform user about allowed types
            return  # Exit the function

        username = message.from_user.username or f"user{message.from_user.id}"  # Get the sender's username or fallback to user ID
        date_str = datetime.now().strftime("%Y%m%d")  # Get the current date in YYYYMMDD format
        original_name_wo_ext = os.path.splitext(original_name)[0]  # Remove the extension from the original file name
        file_name = f"{username}_{date_str}_{original_name_wo_ext}{ext}"  # Create a new file name with username and date

        downloaded_file = bot.download_file(file_info.file_path)  # Download the file from Telegram servers
        file_bytes = io.BytesIO(downloaded_file)  # Convert the downloaded file to a BytesIO object for upload
        files = {'file': (file_name, file_bytes)}  # Prepare the file for HTTP POST request
        response = requests.post(FASTAPI_UPLOAD_URL, files=files)  # Send the file to the FastAPI server

        if response.status_code == 200:  # Check if the upload was successful
            bot.reply_to(message, f"✅ File saved as: {file_name}")  # Inform the user of success
        else:  # If the upload failed
            bot.reply_to(message, f"❌ Upload failed. Server said: {response.text}")  # Inform the user of failure

    except Exception as e:  # Catch any exceptions during the process
        bot.reply_to(message, f"⚠️ Error: {e}")  # Inform the user about the error

# === Main Runner ===
if __name__ == "__main__":
    threading.Thread(target=start_fastapi, daemon=True).start()
    print("Bot and FastAPI server are running...")
    bot.polling()