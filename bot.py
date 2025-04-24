import re
import random
import openai
import asyncio
from telethon import TelegramClient, events, functions, types
from textblob import TextBlob
from utils import analyze_ticker, generate_ai_comment, update_feedback
from tinydb import TinyDB, Query
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Получаем переменные окружения
api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Проверка наличия переменных окружения
if not api_id or not api_hash or not openai_api_key:
    raise EnvironmentError("Отсутствуют переменные окружения: API_ID, API_HASH или OPENAI_API_KEY")

# Устанавливаем ключ для OpenAI
openai.api_key = openai_api_key

# Создаем клиента Telegram
client = TelegramClient('smartprofit_bot', api_id, api_hash)
channel_username = 'smartprofittrading'

# Создаем базу данных TinyDB
db = TinyDB('storage.json')

# Эмодзи для реакции
reaction_emojis = ['👍', '🔥', '❤️', '👏']

# Регулярное выражение для поиска тикеров
TICKER_REGEX = r"[A-Z]{2,5}(USDT|USD|EUR|BTC)?"

@client.on(events.NewMessage(chats=channel_username))
async def handle_new_post(event):
    post = event.message.message
    if not post:
        return

    # Оценка тональности сообщения
    if TextBlob(post).sentiment.polarity < 0.1:
        return

    # Поиск тикера
    ticker_match = re.search(TICKER_REGEX, post)
    ticker_info = ""
    if ticker_match:
        ticker = ticker_match.group(0)
        ticker_info = analyze_ticker(ticker)

    # Случайная задержка перед ответом
    await asyncio.sleep(random.randint(30, 90))

    # Генерация комментария
    style = db.table('styles').get(doc_id=1) or {"mode": "default"}
    comment = generate_ai_comment(post, ticker_info, style.get("mode", "default"))

    try:
        # Отправка сгенерированного комментария
        await client.send_message(
            entity=event.message.to_id,
            message=comment,
            reply_to=event.message.id
        )
    except Exception as e:
        print(f"Ошибка при отправке сообщения: {e}")

    # Реакция на пост с вероятностью 50%
    if random.random() < 0.5:
        try:
            await client(functions.messages.SendReactionRequest(
                peer=event.message.to_id,
                msg_id=event.message.id,
                reaction=[types.ReactionEmoji(emoticon=random.choice(reaction_emojis))]
            ))
        except Exception as e:
            print(f"Ошибка при отправке реакции: {e}")

    # Обновление обратной связи в базе данных
    update_feedback(db, comment)

# Запуск бота
with client:
    print("SmartProfitBot запущен...")
    client.run_until_disconnected()
