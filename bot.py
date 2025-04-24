import re
import random
import openai
import asyncio
from telethon import TelegramClient, events, functions, types
from textblob import TextBlob
from utils import (
    analyze_ticker,
    generate_ai_comment,
    update_feedback,
    summarize_post,
    translate_post,
    predict_market_sentiment,
    generate_catchy_title
)
from tinydb import TinyDB
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
openai_api_key = os.getenv("OPENAI_API_KEY")
bot_token = os.getenv("BOT_TOKEN")
channel_username = os.getenv("CHANNEL_USERNAME", "smartprofittrading").lstrip("@")

if not all([api_id, api_hash, openai_api_key, bot_token]):
    raise EnvironmentError("Не заданы переменные окружения: API_ID, API_HASH, OPENAI_API_KEY или BOT_TOKEN")

openai.api_key = openai_api_key

# Инициализируем клиента бота
client = TelegramClient('smartprofit_bot', int(api_id), api_hash).start(bot_token=bot_token)

db = TinyDB('storage.json')
reaction_emojis = ['👍', '🔥', '❤️', '👏']
TICKER_REGEX = r"[A-Z]{2,5}(USDT|USD|EUR|BTC)?"

# Обработчик личных сообщений
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    print(f"Start from {event.sender_id}")
    await event.respond("👋 Привет! Я SmartProfitBot. Отправь пост в канал или спроси меня здесь.")

# Обработчик новых сообщений в канале
@client.on(events.NewMessage(chats=channel_username))
async def handle_new_post(event):
    post = event.message.message
    print(f"Получено сообщение в канале: {post}")

    # Рассчитываем тональность
    polarity = TextBlob(post).sentiment.polarity
    print(f"Полярность: {polarity}")

    # Порог тональности — сейчас 0.0, чтобы бот отвечал на любые сообщения
    if polarity < 0.0:
        print("Сообщение проигнорировано из-за тональности")
        return

    # Поиск тикера
    ticker_match = re.search(TICKER_REGEX, post)
    ticker_info = analyze_ticker(ticker_match.group(0)) if ticker_match else ""

    # Задержка для имитации человека
    delay = random.randint(30, 90)
    print(f"Ждём {delay} сек...")
    await asyncio.sleep(delay)

    # Генерация основного комментария
    style = db.table('styles').get(doc_id=1) or {"mode": "default"}
    comment = generate_ai_comment(post, ticker_info, style.get("mode"))

    # Доп. функции
    summary = summarize_post(post)
    translation = translate_post(post, "en")
    prediction = predict_market_sentiment(post)
    catchy_title = generate_catchy_title(post)

    full_comment = (
        f"💡 *AI-резюме*: {summary}\n"
        f"🌐 *Перевод*: {translation}\n"
        f"📊 *Прогноз*: {prediction}\n"
        f"🧠 *Заголовок*: {catchy_title}\n\n"
        f"✍️ *Комментарий бота*: {comment}"
    )

    try:
        await client.send_message(
            entity=event.chat_id,
            message=full_comment,
            reply_to=event.message.id,
            parse_mode="markdown"
        )
        print("Комментарий отправлен")
    except Exception as e:
        print(f"Ошибка при отправке комментария: {e}")

    # Случайная реакция
    if random.random() < 0.5:
        try:
            await client(functions.messages.SendReactionRequest(
                peer=event.chat_id,
                msg_id=event.message.id,
                reaction=[types.ReactionEmoji(emoticon=random.choice(reaction_emojis))]
            ))
            print("Реакция отправлена")
        except Exception as e:
            print(f"Ошибка при отправке реакции: {e}")

    update_feedback(db, comment)

print("SmartProfitBot запущен...")
client.run_until_disconnected()
