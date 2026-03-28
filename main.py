"""
Telegram-бот по идеологии национал-большевизма.
Отвечает на вопросы по НБ-идеологии, истории НБП (признана экстремистской в РФ), философии и религиям.
"""

import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from knowledge_base import KNOWLEDGE_BASE, get_author_info, get_nbp_history

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN не найден в переменных среды!")


WELCOME_MESSAGE = """
✊ *Приветствую, товарищ!*

Я — бот по идеологии *национал-большевизма*. Моя база знаний охватывает:

📚 *Теоретиков НБ:*
• Устрялов, Никиш, Эвола, Петель, Лимонов

⚡ *Левых мыслителей:*
• Ленин, Троцкий, Махно, Кропоткин, Бакунин

🦅 *Правых мыслителей:*
• Мёллер ван ден Брук, Леонтьев, Генон, Тириар, Йоки, Моррас, Ильин, де Местр

🏛 *Философов:*
• От Гераклита и Платона до Ницше, Хайдеггера и Шмитта

☯ *Религии:*
• Иудаизм, христианство, ислам

🔥 *История НБП (признана экстремистской в РФ)* (1993–н.в.):
• Акции, репрессии, Донбасс

Выберите раздел или задайте свой вопрос:
"""

HELP_MESSAGE = """
*Как пользоваться ботом:*

/start — главное меню
/avtory — список идеологов НБ
/filosofy — раздел философии
/religii — мировые религии
/istoriya — история НБП (признана экстремистской в РФ)
/sintez — современная модель НБ
/help — эта справка

Или просто напишите имя автора, тему или вопрос — я отвечу на основе базы знаний.

*Примеры запросов:*
• Устрялов
• Никиш
• Лимонов
• Акции НБП (признана экстремистской в РФ)
• Ницше
• Ислам и НБ
• Синтез
"""


def main_keyboard():
    keyboard = [
        [
            InlineKeyboardButton("📖 Идеологи НБ", callback_data="menu_authors"),
            InlineKeyboardButton("🏛 Философы", callback_data="menu_philosophers"),
        ],
        [
            InlineKeyboardButton("⚡ Левые мыслители", callback_data="menu_left"),
            InlineKeyboardButton("🦅 Правые мыслители", callback_data="menu_right"),
        ],
        [
            InlineKeyboardButton("☯ Религии", callback_data="menu_religions"),
            InlineKeyboardButton("🔥 История НБП (признана экстремистской в РФ)", callback_data="menu_history"),
        ],
        [
            InlineKeyboardButton("🌐 Синтез: новый НБ", callback_data="menu_synthesis"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def authors_keyboard():
    keyboard = [
        [InlineKeyboardButton("Устрялов", callback_data="author_Устрялов")],
        [InlineKeyboardButton("Эрнст Никиш", callback_data="author_Никиш")],
        [InlineKeyboardButton("Юлиус Эвола", callback_data="author_Эвола")],
        [InlineKeyboardButton("Карл Отто Петель", callback_data="author_Петель")],
        [InlineKeyboardButton("Эдуард Лимонов", callback_data="author_Лимонов")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def left_keyboard():
    keyboard = [
        [InlineKeyboardButton("Ленин", callback_data="left_Ленин")],
        [InlineKeyboardButton("Троцкий", callback_data="left_Троцкий")],
        [InlineKeyboardButton("Махно", callback_data="left_Махно")],
        [InlineKeyboardButton("Кропоткин", callback_data="left_Кропоткин")],
        [InlineKeyboardButton("Бакунин", callback_data="left_Бакунин")],
        [InlineKeyboardButton("Гитлер (как антипод НБ)", callback_data="left_Гитлер")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def right_keyboard():
    keyboard = [
        [InlineKeyboardButton("Мёллер ван ден Брук", callback_data="right_Брук")],
        [InlineKeyboardButton("Константин Леонтьев", callback_data="right_Леонтьев")],
        [InlineKeyboardButton("Рене Генон", callback_data="right_Генон")],
        [InlineKeyboardButton("Жан Тириар", callback_data="right_Тириар")],
        [InlineKeyboardButton("Фрэнсис Паркер Йоки", callback_data="right_Йоки")],
        [InlineKeyboardButton("Шарль Моррас", callback_data="right_Моррас")],
        [InlineKeyboardButton("Иван Ильин", callback_data="right_Ильин")],
        [InlineKeyboardButton("Жозеф де Местр", callback_data="right_Местр")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def philosophers_keyboard():
    keyboard = [
        [InlineKeyboardButton("Античность", callback_data="phil_antiquity")],
        [InlineKeyboardButton("Ницше", callback_data="phil_Ницше")],
        [InlineKeyboardButton("Маркс", callback_data="phil_Маркс")],
        [InlineKeyboardButton("Гегель", callback_data="phil_Гегель")],
        [InlineKeyboardButton("Хайдеггер", callback_data="phil_Хайдеггер")],
        [InlineKeyboardButton("Карл Шмитт", callback_data="phil_Шмитт")],
        [InlineKeyboardButton("Шпенглер", callback_data="phil_Шпенглер")],
        [InlineKeyboardButton("Сорель", callback_data="phil_Сорель")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def religions_keyboard():
    keyboard = [
        [InlineKeyboardButton("Иудаизм", callback_data="rel_judaism")],
        [InlineKeyboardButton("Христианство", callback_data="rel_christianity")],
        [InlineKeyboardButton("Ислам", callback_data="rel_islam")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def history_keyboard():
    keyboard = [
        [InlineKeyboardButton("Основание НБП (признана экстремистской в РФ) (1993)", callback_data="hist_foundation")],
        [InlineKeyboardButton("Газета «Лимонка»", callback_data="hist_liminka")],
        [InlineKeyboardButton("Акции 1990-х", callback_data="hist_90s")],
        [InlineKeyboardButton("Акции 2000-х", callback_data="hist_2000s")],
        [InlineKeyboardButton("Запрет НБП (признана экстремистской в РФ) (2007)", callback_data="hist_ban")],
        [InlineKeyboardButton("Заключённые нацболы", callback_data="hist_prisoners")],
        [InlineKeyboardButton("Донбасс и СВО", callback_data="hist_donbass")],
        [InlineKeyboardButton("Деятели НБП (признана экстремистской в РФ)", callback_data="hist_figures")],
        [InlineKeyboardButton("◀️ Назад", callback_data="menu_main")],
    ]
    return InlineKeyboardMarkup(keyboard)


def format_author_info(name: str, info: dict) -> str:
    text = f"*{name}*\n"
    if "годы" in info:
        text += f"_{info['годы']}_\n\n"
    if "основные_труды" in info:
        text += "*Основные труды:*\n"
        for t in info["основные_труды"]:
            text += f"• {t}\n"
        text += "\n"
    if "идеи" in info:
        text += f"*Идеи и вклад:*\n{info['идеи']}\n\n"
    if "цитаты" in info:
        text += "*Цитаты:*\n"
        for c in info["цитаты"]:
            text += f"_{c}_\n"
    if "цитаты_критика" in info:
        text += "*Критика со стороны НБ-теоретиков:*\n"
        for c in info["цитаты_критика"]:
            text += f"_{c}_\n"
    return text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        WELCOME_MESSAGE,
        parse_mode="Markdown",
        reply_markup=main_keyboard(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")


async def authors_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "📖 *Идеологи национал-большевизма:*\nВыберите автора:",
        parse_mode="Markdown",
        reply_markup=authors_keyboard(),
    )


async def philosophers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🏛 *Философы:*\nВыберите философа или школу:",
        parse_mode="Markdown",
        reply_markup=philosophers_keyboard(),
    )


async def religions_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "☯ *Религии:*\nВыберите религию:",
        parse_mode="Markdown",
        reply_markup=religions_keyboard(),
    )


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "🔥 *История НБП (признана экстремистской в РФ) (1993–н.в.):*\nВыберите раздел:",
        parse_mode="Markdown",
        reply_markup=history_keyboard(),
    )


async def synthesis_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    synth = KNOWLEDGE_BASE["синтез_современного_нб"]
    text = (
        "🌐 *СИНТЕЗ: СОВРЕМЕННЫЙ НАЦИОНАЛ-БОЛЬШЕВИЗМ*\n\n"
        f"{synth['единство_противоречий']}\n\n"
        f"{'—'*30}\n\n"
        f"{synth['новая_модель']}"
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Главное меню", callback_data="menu_main")]]),
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu_main":
        await query.edit_message_text(
            WELCOME_MESSAGE, parse_mode="Markdown", reply_markup=main_keyboard()
        )

    elif data == "menu_authors":
        await query.edit_message_text(
            "📖 *Идеологи национал-большевизма:*\nВыберите автора:",
            parse_mode="Markdown",
            reply_markup=authors_keyboard(),
        )

    elif data == "menu_left":
        await query.edit_message_text(
            "⚡ *Левые мыслители и революционеры:*\nВыберите автора:",
            parse_mode="Markdown",
            reply_markup=left_keyboard(),
        )

    elif data == "menu_right":
        await query.edit_message_text(
            "🦅 *Правые мыслители и консервативные революционеры:*\nВыберите автора:",
            parse_mode="Markdown",
            reply_markup=right_keyboard(),
        )

    elif data == "menu_philosophers":
        await query.edit_message_text(
            "🏛 *Философы:*\nВыберите философа или школу:",
            parse_mode="Markdown",
            reply_markup=philosophers_keyboard(),
        )

    elif data == "menu_religions":
        await query.edit_message_text(
            "☯ *Религии:*\nВыберите религию:",
            parse_mode="Markdown",
            reply_markup=religions_keyboard(),
        )

    elif data == "menu_history":
        await query.edit_message_text(
            "🔥 *История НБП (признана экстремистской в РФ) (1993–н.в.):*\nВыберите раздел:",
            parse_mode="Markdown",
            reply_markup=history_keyboard(),
        )

    elif data == "menu_synthesis":
        synth = KNOWLEDGE_BASE["синтез_современного_нб"]
        text = (
            "🌐 *СИНТЕЗ: СОВРЕМЕННЫЙ НАЦИОНАЛ-БОЛЬШЕВИЗМ*\n\n"
            f"{synth['единство_противоречий']}\n\n"
            f"{'—'*30}\n\n"
            f"{synth['новая_модель']}"
        )
        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_main")]]),
        )

    elif data.startswith("author_"):
        name_key = data.replace("author_", "")
        authors = KNOWLEDGE_BASE["авторы_нб"]
        found = None
        for key, val in authors.items():
            if name_key.lower() in key.lower():
                found = (key, val)
                break
        if found:
            text = format_author_info(found[0], found[1])
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_authors")]]),
            )

    elif data.startswith("left_"):
        name_key = data.replace("left_", "")
        authors = KNOWLEDGE_BASE["марксисты_анархисты"]
        found = None
        for key, val in authors.items():
            if name_key.lower() in key.lower():
                found = (key, val)
                break
        if found:
            text = format_author_info(found[0], found[1])
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_left")]]),
            )

    elif data.startswith("right_"):
        name_key = data.replace("right_", "")
        authors = KNOWLEDGE_BASE["правые_мыслители"]
        found = None
        for key, val in authors.items():
            if name_key.lower() in key.lower():
                found = (key, val)
                break
        if found:
            text = format_author_info(found[0], found[1])
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_right")]]),
            )

    elif data.startswith("phil_"):
        phil_key = data.replace("phil_", "")
        if phil_key == "antiquity":
            antiquity = KNOWLEDGE_BASE["философы"]["античность"]
            text = "🏛 *АНТИЧНАЯ ФИЛОСОФИЯ И НБ*\n\n"
            for name, info in antiquity.items():
                text += f"*{name}* ({info['годы']})\n{info['идеи']}\n\n"
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_philosophers")]]),
            )
        else:
            found = None
            for section_name, section in KNOWLEDGE_BASE["философы"].items():
                if isinstance(section, dict):
                    for name, info in section.items():
                        if phil_key.lower() in name.lower():
                            found = (name, info)
                            break
            if found:
                text = format_author_info(found[0], found[1])
                await query.edit_message_text(
                    text,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_philosophers")]]),
                )

    elif data.startswith("rel_"):
        rel_map = {
            "rel_judaism": ("Иудаизм", "☯ *ИУДАИЗМ И НБ-ИДЕОЛОГИЯ*\n\n"),
            "rel_christianity": ("Христианство", "✝️ *ХРИСТИАНСТВО И НБ-ИДЕОЛОГИЯ*\n\n"),
            "rel_islam": ("Ислам", "☪️ *ИСЛАМ И НБ-ИДЕОЛОГИЯ*\n\n"),
        }
        if data in rel_map:
            rel_key, header = rel_map[data]
            rel_info = KNOWLEDGE_BASE["религии"][rel_key]
            text = header
            text += f"{rel_info['основы']}\n\n"
            text += f"*Основные направления:*\n"
            for d in rel_info["направления"]:
                text += f"• {d}\n"
            await query.edit_message_text(
                text,
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_religions")]]),
            )

    elif data.startswith("hist_"):
        hist = KNOWLEDGE_BASE["история_нбп"]
        hist_key = data.replace("hist_", "")

        if hist_key == "foundation":
            text = f"🔥 *ОСНОВАНИЕ НБП (признана экстремистской в РФ) (1993)*\n\n{hist['основание']}"
        elif hist_key == "liminka":
            text = f"📰 *ГАЗЕТА «ЛИМОНКА»*\n\n{hist['газета_лимонка']}"
        elif hist_key == "90s":
            text = "🔥 *АКЦИИ НБП (признана экстремистской в РФ) В 1990-х*\n\n"
            for a in hist["акции"]["1990е"]:
                text += f"• {a}\n"
        elif hist_key == "2000s":
            text = "🔥 *АКЦИИ НБП (признана экстремистской в РФ) В 2000-х*\n\n"
            for a in hist["акции"]["2000е"]:
                text += f"• {a}\n"
            text += "\n*После запрета (2010-е):*\n"
            for a in hist["акции"]["2010е_и_далее"]:
                text += f"• {a}\n"
        elif hist_key == "ban":
            text = f"⚖️ *ЗАПРЕТ НБП (признана экстремистской в РФ) (2007)*\n\n{hist['запрет']}"
        elif hist_key == "prisoners":
            text = "⛓ *ЗАКЛЮЧЁННЫЕ НАЦБОЛЫ*\n\n"
            for name, info in hist["заключённые"].items():
                if name == "общее":
                    text += f"\n{info}"
                else:
                    text += f"*{name.replace('_', ' ')}*: {info}\n\n"
        elif hist_key == "donbass":
            d = hist["на_донбассе_и_сво"]
            text = f"🔴 *НАЦБОЛЫ НА ДОНБАССЕ И В СВО*\n\n{d['общее']}\n\n{d['погибшие_и_участники']}"
        elif hist_key == "figures":
            text = "👤 *ДЕЯТЕЛИ НБП (признана экстремистской в РФ)*\n\n"
            for f in hist["идеологи_и_деятели"]:
                text += f"• {f}\n"
        else:
            text = "Раздел в разработке."

        await query.edit_message_text(
            text,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("◀️ Назад", callback_data="menu_history")]]),
        )


def smart_answer(text: str) -> str:
    """Генерация ответа на свободный вопрос."""
    text_lower = text.lower()

    keywords_authors_nb = {
        "устрялов": ("авторы_нб", "Николай Устрялов"),
        "никиш": ("авторы_нб", "Эрнст Никиш"),
        "эвола": ("авторы_нб", "Юлиус Эвола"),
        "петель": ("авторы_нб", "Карл Отто Петель"),
        "лимонов": ("авторы_нб", "Эдуард Лимонов"),
    }

    keywords_left = {
        "ленин": ("марксисты_анархисты", "Владимир Ленин"),
        "троцкий": ("марксисты_анархисты", "Лев Троцкий"),
        "махно": ("марксисты_анархисты", "Нестор Махно"),
        "кропоткин": ("марксисты_анархисты", "Пётр Кропоткин"),
        "бакунин": ("марксисты_анархисты", "Михаил Бакунин"),
        "гитлер": ("марксисты_анархисты", "Адольф Гитлер"),
        "маркс": ("философы", "Карл Маркс"),
    }

    keywords_phil = {
        "ницше": "Фридрих Ницше",
        "гегель": "Георг Гегель",
        "хайдеггер": "Мартин Хайдеггер",
        "шмитт": "Карл Шмитт",
        "шпенглер": "Освальд Шпенглер",
        "сорель": "Жорж Сорель",
        "платон": "Платон",
        "аристотель": "Аристотель",
        "гераклит": "Гераклит",
        "дугин": "Александр Дугин",
        "дебор": "Ги Дебор",
    }

    keywords_right = {
        "мёллер": "Артур Мёллер ван ден Брук",
        "моллер": "Артур Мёллер ван ден Брук",
        "ван ден брук": "Артур Мёллер ван ден Брук",
        "третий рейх": "Артур Мёллер ван ден Брук",
        "леонтьев": "Константин Леонтьев",
        "генон": "Рене Генон",
        "традиционализм": "Рене Генон",
        "тириар": "Жан Тириар",
        "йоки": "Фрэнсис Паркер Йоки",
        "imperium": "Фрэнсис Паркер Йоки",
        "моррас": "Шарль Моррас",
        "аксьон": "Шарль Моррас",
        "ильин": "Иван Ильин",
        "де местр": "Жозеф де Местр",
        "местр": "Жозеф де Местр",
        "контрреволюция": "Жозеф де Местр",
        "консервативная революция": "Артур Мёллер ван ден Брук",
    }

    keywords_history = [
        "нбп", "лимонка", "акция", "акции", "история", "запрет",
        "тюрьма", "арест", "заключённый", "донбасс", "сво",
    ]

    keywords_synthesis = ["синтез", "новый нб", "современный нб", "модель", "единство"]

    keywords_religions = {
        "иудаизм": "Иудаизм",
        "евреи": "Иудаизм",
        "христианство": "Христианство",
        "православие": "Христианство",
        "ислам": "Ислам",
        "мусульман": "Ислам",
    }

    for kw, (section, name) in keywords_authors_nb.items():
        if kw in text_lower:
            info = KNOWLEDGE_BASE[section][name]
            return format_author_info(name, info)

    for kw, (section, name) in keywords_left.items():
        if kw in text_lower:
            if section == "марксисты_анархисты":
                info = KNOWLEDGE_BASE[section][name]
                return format_author_info(name, info)
            else:
                for sec_name, sec in KNOWLEDGE_BASE["философы"].items():
                    if isinstance(sec, dict) and name in sec:
                        return format_author_info(name, sec[name])

    for kw, name in keywords_right.items():
        if kw in text_lower:
            info = KNOWLEDGE_BASE["правые_мыслители"].get(name)
            if info:
                return format_author_info(name, info)

    for kw, name in keywords_phil.items():
        if kw in text_lower:
            for sec_name, sec in KNOWLEDGE_BASE["философы"].items():
                if isinstance(sec, dict) and name in sec:
                    return format_author_info(name, sec[name])

    for kw in keywords_synthesis:
        if kw in text_lower:
            synth = KNOWLEDGE_BASE["синтез_современного_нб"]
            return (
                "🌐 *СИНТЕЗ: СОВРЕМЕННЫЙ НАЦИОНАЛ-БОЛЬШЕВИЗМ*\n\n"
                f"{synth['единство_противоречий']}\n\n"
                f"{synth['новая_модель']}"
            )

    for kw in keywords_history:
        if kw in text_lower:
            return get_nbp_history()

    for kw, name in keywords_religions.items():
        if kw in text_lower:
            rel_info = KNOWLEDGE_BASE["религии"][name]
            return (
                f"*{name.upper()} И НБ-ИДЕОЛОГИЯ*\n\n"
                f"{rel_info['основы']}\n\n"
                f"*Основные направления:*\n"
                + "\n".join(f"• {d}" for d in rel_info["направления"])
            )

    return None


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_text = update.message.text

    answer = smart_answer(user_text)

    if answer:
        chunks = [answer[i:i+4000] for i in range(0, len(answer), 4000)]
        for i, chunk in enumerate(chunks):
            if i == len(chunks) - 1:
                await update.message.reply_text(
                    chunk,
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 Главное меню", callback_data="menu_main")]]),
                )
            else:
                await update.message.reply_text(chunk, parse_mode="Markdown")
    else:
        fallback = (
            f"🤔 По запросу «*{user_text}*» я не нашёл точного совпадения в базе знаний.\n\n"
            "Попробуйте:\n"
            "• Написать имя автора (Устрялов, Никиш, Лимонов, Ницше...)\n"
            "• Написать тему (НБП (признана экстремистской в РФ), история, синтез, религии...)\n"
            "• Использовать меню ниже"
        )
        await update.message.reply_text(
            fallback,
            parse_mode="Markdown",
            reply_markup=main_keyboard(),
        )


def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler(["help", "pomosh"], help_command))
    app.add_handler(CommandHandler(["avtory", "authors"], authors_command))
    app.add_handler(CommandHandler(["filosofy", "philosophers"], philosophers_command))
    app.add_handler(CommandHandler(["religii", "religions"], religions_command))
    app.add_handler(CommandHandler(["istoriya", "history"], history_command))
    app.add_handler(CommandHandler(["sintez", "synthesis"], synthesis_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("НБ-бот запущен. Ожидаю сообщения...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
