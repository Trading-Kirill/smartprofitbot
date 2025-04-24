import openai
from tinydb import TinyDB, Query

# Генерация комментариев с помощью OpenAI
def generate_ai_comment(post_text, ticker_info, style):
    prompt = f"""
    Пост: {post_text}
    Данные по тикеру: {ticker_info}
    Стиль: {style}

    Сгенерируй содержательный комментарий от имени трейдера:
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Анализ тикера (заглушка)
def analyze_ticker(ticker):
    return f"Анализ тикера {ticker}: объёмы растут, возможен пробой уровня сопротивления."

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
    prompt = f"""
    Текст: {post_text}

    Сформулируй краткое резюме в одном-двух предложениях:
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=60
    )
    return response.choices[0].text.strip()

# Перевод на английский
def translate_post(post_text, target_lang="en"):
    prompt = f"""
    Переведи следующий текст на английский:
    {post_text}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100
    )
    return response.choices[0].text.strip()

# Прогноз движения рынка по тексту поста
def predict_market_sentiment(post_text):
    prompt = f"""
    Проанализируй следующий пост и сделай краткий прогноз движения рынка:
    {post_text}

    Ответь: рост, падение или нейтрально, и поясни почему.
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=80
    )
    return response.choices[0].text.strip()

# Генерация привлекательного заголовка
def generate_catchy_title(post_text):
    prompt = f"""
    Придумай краткий, броский заголовок к следующему посту трейдера:
    {post_text}
    """
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=15
    )
    return response.choices[0].text.strip()
