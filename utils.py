import openai
from tinydb import TinyDB, Query

# Генерация комментариев с помощью OpenAI ChatCompletion
def generate_ai_comment(post_text, ticker_info, style):
    prompt = f"Post: {post_text}\nTicker: {ticker_info}\nStyle: {style}\nGenerate a concise trading comment."
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful financial trading assistant."},
            {"role": "user",   "content": prompt}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content.strip()

# Анализ тикера (заглушка)
def analyze_ticker(ticker):
    return f"Info about {ticker}"

# Обновление данных о реакции
def update_feedback(db, comment, reaction=None):
    styles_table = db.table('styles')
    reactions_table = db.table('reactions')

    reaction_entry = reactions_table.get(Query().comment == comment)
    if reaction_entry:
        reactions_table.update({"count": reaction_entry["count"] + 1}, Query().comment == comment)
    else:
        reactions_table.insert({"comment": comment, "count": 1})

    all_reactions = reactions_table.all()
    avg_reaction = sum(r["count"] for r in all_reactions) / len(all_reactions) if all_reactions else 0
    new_mode = "analytical" if avg_reaction > 5 else "motivational"
    styles_table.upsert({"mode": new_mode}, Query().doc_id == 1)

# Суммаризация поста
def summarize_post(post_text):
    prompt = f"Сформулируй краткое резюме в 1-2 предложениях для текста:\n{post_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=60
    )
    return response.choices[0].message.content.strip()

# Перевод на английский
def translate_post(post_text, target_lang="en"):
    prompt = f"Переведи следующий текст на {target_lang}:\n{post_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=100
    )
    return response.choices[0].message.content.strip()

# Прогноз движения рынка по тексту поста
def predict_market_sentiment(post_text):
    prompt = (
        f"Проанализируй пост торговой тематики и дай прогноз движения рынка "
        f"(рост, падение или нейтрально) с кратким объяснением:\n{post_text}"
    )
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=80
    )
    return response.choices[0].message.content.strip()

# Генерация привлекательного заголовка
def generate_catchy_title(post_text):
    prompt = f"Придумай короткий и цепляющий заголовок для поста трейдера:\n{post_text}"
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=15
    )
    return response.choices[0].message.content.strip()
