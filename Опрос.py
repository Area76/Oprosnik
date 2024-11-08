import logging
import pandas as pd
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

# Настройка логирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
# Замените на ваш токен
TOKEN = "7551388193:AAGz0PeOFbbdnapmzQOHJUEWifZgWYITYUY"  # Не забудьте заменить на ваш токен
# Вопросы опроса
questions = [
    {
        "question": "Считаете ли Вы, что государство, решая задачи экономической политики, должно придерживаться определенных правил?",
        "options": {
            "а": "Решать экономические задачи в основном поочередно.",
            "б": "Достигать целей одновременно.",
            "в": "Правил придерживаться не следует, важно лишь оперативно реагировать на обстановку."
        },
        "responses": {key: 0 for key in "абв"}
    },
    {
        "question": "Что Вы считаете более предпочтительным в проведении экономической политики?",
        "options": {
            "а": "Бороться с инфляцией, т.е. ростом цен, и допускать, если это неизбежно, определенное увеличение безработицы.",
            "б": "Бороться с безработицей и допускать, если это неизбежно, рост цен, т. е. усиление инфляции.",
            "в": "Искать новые пути решения двух указанных проблем."
        },
        "responses": {key: 0 for key in "абв"}
    },
    {
        "question": "О чем, по Вашему мнению, должен заботиться каждый россиянин в период сложной экономической ситуации?",
        "options": {
            "а": "Быть более активным.",
            "б": "Заботиться прежде всего о себе.",
            "в": "Ориентироваться на то, что значительные экономические трудности - своего рода школа обучения и стимул к более быстрому решению накопившихся и застарелых проблем.",
            "г": "Думать о нуждах всей страны.",
            "д": "Искать источники помощи извне."
        },
        "responses": {key: 0 for key in "абвгд"}
    },
    {
        "question": "Влияние каких внешних факторов ощущаете Вы как субъект экономической (профессиональной) сферы деятельности?",
        "options": {
            "а": "Условия развития всей экономики страны.",
            "б": "Экономическая политика государства.",
            "в": "Конъюнктура развития отрасли, в которой находится предприятие.",
            "г": "Коррупция.",
            "д": "Криминальные структуры.",
            "е": "Практически никакого влияния не ощущаю."
        },
        "responses": {key: 0 for key in "абвгде"}
    },
    {
        "question": "Хотите ли Вы, будучи деловой личностью, бизнесменом (или желая стать им), оказывать встречное влияние на государство, на его экономическую политику?",
        "options": {
            "а": "Хотел бы путем влияния на государственных лиц (метод лобби).",
            "б": "Хотел бы через систему выборов.",
            "в": "Встречного влияния оказывать не хочу. Каждый идет своей дорогой, делая свое дело.",
            "г": "Хотел бы через стиль своего постоянного поведения (проведения «своей линии»).",
            "д": "Хотел бы через организацию политического движения."
        },
        "responses": {key: 0 for key in "абвгд"}
    },
    {
        "question": "Если Вы стремитесь избежать налогообложения, на что похожи подобные действия?",
        "options": {
            "а": "Стараюсь не избегать налогообложения и быть законопослушным.",
            "б": "Уход от налогов - форма сохранения у себя средств, которые государство может нерационально использовать.",
            "в": "Уход от налогов - проявление природной (и потому закономерной) изворотливости всех субъектов экономики, каждый из которых имеет свои личные цели.",
            "г": "Уход от налогов - способ поддержания своего относительного материального достатка.",
            "д": "Уход от налогов - способ воровства финансовых средств у государства."
        },
        "responses": {key: 0 for key in "абвгд"}
    }
]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['question_index'] = 0
    context.user_data['responses'] = {key: 0 for question in questions for key in question["responses"].keys()}
    await show_question(update, context)


async def show_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_index = context.user_data['question_index']
    question_data = questions[question_index]
    question_text = question_data["question"] + "\n\n"
    for key, value in question_data["options"].items():
        question_text += f"{key}) {value}\n"
    options = [[key] for key in question_data["options"].keys()]
    reply_markup = ReplyKeyboardMarkup(options, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(question_text, reply_markup=reply_markup)


async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question_index = context.user_data['question_index']
    question_data = questions[question_index]
    answer = update.message.text.strip().lower()
    if answer in question_data["responses"]:
        question_data["responses"][answer] += 1
        context.user_data['responses'][answer] += 1
        if question_index + 1 < len(questions):
            context.user_data['question_index'] += 1
            await show_question(update, context)
        else:
            await show_final_results(update, context)
    else:
        await update.message.reply_text("Пожалуйста, выберите один из предложенных вариантов ответа.")


async def show_final_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    results_text = "Результаты опроса:\n"
    results_data = []  # Список для хранения данных для Excel
    for question in questions:
        total_responses = sum(question["responses"].values())
        results_text += f"\n{question['question']}\n"
        for key, count in question["responses"].items():
            if count > 0:
                percentage = (count / total_responses * 100) if total_responses > 0 else 0
                results_text += f"{key}) {question['options'][key]}: {count} ответов ({percentage:.2f}%)\n"
                # Добавляем данные в список для Excel
                results_data.append({
                    "Вопрос": question['question'],
                    "Ответ": question['options'][key],
                    "Количество": count,
                    "Процент": percentage
                })
    await update.message.reply_text("Спасибо за прохождение опроса!")
    await update.message.reply_text(results_text)

    # Сохранение результатов в файл Excel
    df = pd.DataFrame(results_data)
    df.to_excel('survey_results.xlsx', index=False)  # Удалён параметр encoding

    # Кнопка для удаления бота
    keyboard = [[InlineKeyboardButton("Удалить бота", callback_data='delete_bot')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Если вы хотите удалить бота из вашего профиля, нажмите кнопку ниже:",
                                    reply_markup=reply_markup)


async def delete_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    # Уведомление о том, как удалить бота
    await query.message.reply_text(
        "Чтобы удалить бота, просто нажмите на его имя в верхней части чата и выберите 'Удалить'.")
    # Удаляем все данные пользователя
    context.user_data.clear()


def main():
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer))
    application.add_handler(CallbackQueryHandler(delete_bot, pattern='delete_bot'))
    application.run_polling()


if __name__ == '__main__':
    main()
