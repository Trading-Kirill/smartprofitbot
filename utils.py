import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import openai as openai_module
from tinydb import TinyDB, Query

# Явно загружаем .env из папки с этим файлом
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Проверяем, что ключ задан
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise EnvironmentError("OPENAI_API_KEY не задана в .env")

# Инициализация клиента OpenAI
client = OpenAI(api_key=api_key)

def generate_ai_comment(post_text: str, ticker_info: str, style: str) -> str:
    prompt = (
        f"Пост: {post_text}\n"
        f"Данные по тикеру: {ticker_info}\n"
        f"Стиль: {style}\n\n"
        "Сгенерируй краткий профессиональный комментарий для трейдеров."
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful financial trading assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150
        )
        return resp.choices[0].message.content.strip()
    except openai_module.error.RateLimitError:
        return "⚠️ Извините, временно превышен лимит запросов. Попробуйте позже."
    except openai_module.error.OpenAIError as e:
        return f"⚠️ Ошибка OpenAI API: {e}"

def analyze_ticker(ticker: str) -> str:
    return f"Анализ тикера {ticker}: объёмы растут, возможен разворот."

def update_feedback(db: TinyDB, comment: str, reaction: int = None) -> None:
    styles_table = db.table("styles")
    reactions_table = db.table("reactions")
    entry = reactions_table.get(Query().comment == comment)
    if entry:
        reactions_table.update({"count": entry["count"] + 1}, Query().comment == comment)
    else:
        reactions_table.insert({"comment": comment, "count": 1})
    all_reacts = reactions_table.all()
    avg = sum(r["count"] for r in all_reacts) / len(all_reacts) if all_reacts else 0
    new_mode = "analytical" if avg > 5 else "motivational"
    styles_table.upsert({"mode": new_mode}, Query().doc_id == 1)

def summarize_post(post_text: str) -> str:
    prompt = f"Сформулируй краткое резюме в 1–2 предложениях для текста:\n{post_text}"
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=60
        )
        return resp.choices[0].message.content.strip()
    except openai_module.error.RateLimitError:
        return "⚠️ Нельзя сейчас сделать резюме — квота исчерпана."
    except openai_module.error.OpenAIError as e:
        return f"⚠️ Ошибка при резюме: {e}"

def translate_post(post_text: str, target_lang: str = "en") -> str:
    prompt = f"Переведи следующий текст на {target_lang}:\n{post_text}"
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100
        )
        return resp.choices[0].message.content.strip()
    except openai_module.error.RateLimitError:
        return "⚠️ Нельзя сейчас перевести — квота исчерпана."
    except openai_module.error.OpenAIError as e:
        return f"⚠️ Ошибка при переводе: {e}"

def predict_market_sentiment(post_text: str) -> str:
    prompt = (
        "Проанализируй торговый пост и дай прогноз движения рынка "
        "(рост, падение или нейтрально) с кратким объяснением:\n" + post_text
    )
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=80
        )
        return resp.choices[0].message.content.strip()
    except openai_module.error.RateLimitError:
        return "⚠️ Нельзя сейчас дать прогноз — квота исчерпана."
    except openai_module.error.OpenAIError as e:
        return f"⚠️ Ошибка при прогнозе: {e}"

def generate_catchy_title(post_text: str) -> str:
    prompt = f"Придумай короткий, броский заголовок для поста трейдера:\n{post_text}"
    try:
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=15
        )
        return resp.choices[0].message.content.strip()
    except openai_module.error.RateLimitError:
        return "⚠️ Нельзя сейчас создать заголовок — квота исчерпана."
    except openai_module.error.OpenAIError as e:
        return f"⚠️ Ошибка при заголовке: {e}"
