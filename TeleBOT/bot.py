import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from yt_video import fetch_video_formats, download_video_with_audio
from thumbnail import fetch_thumbnail
import os
import requests
import subprocess

API_TOKEN = '7727845115:AAGt3cl-b-YHFGn0lFPfgzoYk8J6Yq_k7Ts'
bot = telebot.TeleBot(API_TOKEN)

user_choices = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    commands = """
Welcome! Here are the commands you can use:
/start - Start the bot and see this menu
/yt_video - Download YouTube videos (with audio)
/thumbnail - Download YouTube video thumbnails
/help - Get help on how to use the bot
"""
    bot.reply_to(message, commands)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(
        message,
        "This bot can assist you with downloading YouTube videos (with audio) and thumbnails. Use /start to see all commands."
    )


@bot.message_handler(commands=['yt_video'])
def request_video_url(message):
    msg = bot.reply_to(
        message,
        "Please send the YouTube video link to fetch available formats.")
    bot.register_next_step_handler(msg, handle_video_url)


@bot.message_handler(commands=['thumbnail'])
def request_thumbnail_url(message):
    msg = bot.reply_to(
        message, "Please send the YouTube video link to fetch the thumbnail.")
    bot.register_next_step_handler(msg, handle_thumbnail_request)


def handle_thumbnail_request(message):
    try:
        url = message.text.strip()
        thumbnail_url = fetch_thumbnail(url)
        response = requests.get(thumbnail_url)
        if response.status_code == 200:
            file_path = "thumbnail.jpg"
            with open(file_path, 'wb') as file:
                file.write(response.content)
            with open(file_path, 'rb') as img:
                bot.send_photo(message.chat.id, img)
            os.remove(file_path)
            bot.reply_to(
                message,
                "Thumbnail sent successfully! Use /thumbnail to fetch another."
            )
        else:
            bot.reply_to(message, "Failed to download thumbnail.")
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


def handle_video_url(message):
    try:
        url = message.text.strip()
        video_formats = fetch_video_formats(url)
        if not video_formats:
            bot.reply_to(message,
                         "No downloadable video formats found for this link.")
            return
        user_choices[message.chat.id] = {'url': url, 'formats': video_formats}
        markup = InlineKeyboardMarkup()
        for fmt in video_formats:
            format_text = f"{fmt['format_note']} - {fmt['filesize']}"
            markup.add(
                InlineKeyboardButton(format_text,
                                     callback_data=fmt['format_id']))
        bot.reply_to(message,
                     "Select a video quality to download (with audio):",
                     reply_markup=markup)
    except Exception as e:
        bot.reply_to(message, f"An error occurred: {str(e)}")


@bot.callback_query_handler(func=lambda call: True)
def handle_format_selection(call):
    try:
        chat_id = call.message.chat.id
        format_id = call.data
        user_data = user_choices.get(chat_id)
        if not user_data:
            bot.send_message(chat_id, "An error occurred. Please try again.")
            return
        url = user_data['url']
        bot.send_message(chat_id,
                         "Downloading the video (with audio), please wait...")
        file_path = download_video_with_audio(url, format_id)
        with open(file_path, 'rb') as video:
            bot.send_video(chat_id, video)
        bot.send_message(
            chat_id,
            "Download complete! Do you want to download another video? Use /yt_video."
        )
        os.remove(file_path)
        del user_choices[chat_id]  # Clean up user choice
    except Exception as e:
        bot.send_message(call.message.chat.id, f"An error occurred: {str(e)}")

def download_video(video_url):
    cookies_path = '/Users/PC/Documents/cookies.txt' 
    command = ['yt-dlp', '--cookies', cookies_path, video_url]
    subprocess.run(command)

print("Bot is running...")
bot.infinity_polling()
