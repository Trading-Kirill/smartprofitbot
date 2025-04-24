import openai
from tinydb import TinyDB, Query

# Генерация комментариев с помощью OpenAI
def generate_ai_comment(post_text, ticker_info, style):
    prompt = f"""
    Post: {post_text}
    Ticker: {ticker_info}
    Style: {style}

    Generate a comment:
    """

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=150
    )
    return response.choices[0].text.strip()

# Анализ тикера (заглушка)
def analyze_ticker(ticker):
    return f"Info about {ticker}"

# Обновление данных о реакции
def update_feedback(db, comment, reaction=None):
    styles_table = db.table('styles')
    reactions_table = db.table('reactions')
    
    # Проверяем, если уже есть такой комментарий
    reaction_entry = reactions_table.get(Query().comment == comment)
    
    if reaction_entry:
        # Обновляем реакцию
        reactions_table.update({"count": reaction_entry["count"] + 1}, Query().comment == comment)
    else:
        reactions_table.insert({"comment": comment, "count": 1})
    
    # Адаптация стиля
    avg_reaction = sum([r["count"] for r in reactions_table.all()]) / len(reactions_table.all()) if reactions_table.all() else 0
    
    if avg_reaction > 5:  # Порог для популярности комментариев (например, больше 5 реакций)
        new_mode = "analytical"
    else:
        new_mode = "motivational"

    # Обновляем стиль комментариев
    styles_table.upsert({"mode": new_mode}, Query().doc_id == 1)
