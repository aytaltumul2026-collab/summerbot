#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🌞 SummerProduct_bot — Бот магазина летних товаров
Автор: Videos• Team
"""

import logging
import httpx
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    LabeledPrice, ShippingAddress
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes,
    PreCheckoutQueryHandler, ShippingQueryHandler
)

# ══════════════════════════════════════════
#  НАСТРОЙКИ — ЗАПОЛНИ ПЕРЕД ЗАПУСКОМ
# ══════════════════════════════════════════
TOKEN = "8996102976:AAHUHjrpz6OKOekzT8IedorXoOuQjh7Gxo4"           # Токен от @BotFather
ADMIN_ID = 2084021782                        # Твой Telegram ID (узнай у @userinfobot)
PAYMENT_TOKEN = "ВСТАВЬ_ТОКЕН_ОПЛАТЫ"      # Токен от @SberbankPaymentBot или ЮКасса
CLAUDE_API_KEY = "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"   # Ключ от console.anthropic.com

# ══════════════════════════════════════════
#  КАТАЛОГ ТОВАРОВ
# ══════════════════════════════════════════
PRODUCTS = {
    "pool_small": {
        "name": "🏊 Каркасный бассейн малый",
        "desc": "Размер 200×50 см. Идеален для детей 3-8 лет. Быстрая сборка за 20 минут. Усиленный стальной каркас.",
        "price": 4990,
        "emoji": "🏊",
        "category": "pools"
    },
    "pool_medium": {
        "name": "🏊 Каркасный бассейн средний",
        "desc": "Размер 300×76 см. Для всей семьи. В комплекте фильтр-насос. Толстый ПВХ 0.4 мм.",
        "price": 8990,
        "emoji": "🏊",
        "category": "pools"
    },
    "pool_house": {
        "name": "🏠 Бассейн-домик надувной",
        "desc": "Уникальный бассейн с надувным домиком! Защита от солнца + бассейн в одном. Хит сезона 2025!",
        "price": 24990,
        "emoji": "🏠",
        "category": "pools"
    },
    "mosquito_uv": {
        "name": "🦟 UV ловушка для комаров",
        "desc": "Уничтожает комаров и мошек без химии. Площадь до 50 кв.м. Безопасна для детей и животных.",
        "price": 1990,
        "emoji": "🦟",
        "category": "mosquito"
    },
    "mosquito_gas": {
        "name": "⚡ Газовая ловушка CO2",
        "desc": "Профессиональная ловушка. Площадь до 2000 кв.м. Идеальна для дачи и террасы.",
        "price": 12990,
        "emoji": "⚡",
        "category": "mosquito"
    },
    "ball_size3": {
        "name": "⚽ Футбольный мяч размер 3",
        "desc": "Детский мяч для возраста 5-8 лет. Яркий дизайн. Сертифицированный ПВХ. Идеальный подарок!",
        "price": 890,
        "emoji": "⚽",
        "category": "balls"
    },
    "ball_size4": {
        "name": "⚽ Футбольный мяч размер 4",
        "desc": "Для возраста 8-12 лет. Профессиональная камера. Держит форму весь сезон.",
        "price": 1190,
        "emoji": "⚽",
        "category": "balls"
    },
    "sunglasses": {
        "name": "😎 Солнечные очки UV400",
        "desc": "Защита от УФ лучей 100%. Стильный дизайн. Унисекс. Лёгкая оправа.",
        "price": 790,
        "emoji": "😎",
        "category": "accessories"
    },
    "fan_portable": {
        "name": "💨 Портативный вентилятор",
        "desc": "Работает от USB. Три скорости. Тихий мотор. Незаменим в жару.",
        "price": 690,
        "emoji": "💨",
        "category": "accessories"
    },
    "sunscreen": {
        "name": "🧴 Солнцезащитный крем SPF50",
        "desc": "Водостойкий. SPF 50+. Защита 8 часов. Для детей и взрослых. 200 мл.",
        "price": 590,
        "emoji": "🧴",
        "category": "accessories"
    },
}

CATEGORIES = {
    "pools": "🏊 Бассейны",
    "mosquito": "🦟 Защита от комаров",
    "balls": "⚽ Мячи",
    "accessories": "☀️ Аксессуары",
}

# Корзины пользователей (в памяти)
carts = {}

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════
#  ГЛАВНОЕ МЕНЮ
# ══════════════════════════════════════════
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = (
        f"🌞 Привет, {user.first_name}!\n\n"
        "Добро пожаловать в **Summer Products** — магазин лучших летних товаров!\n\n"
        "🏊 Бассейны · 🦟 Защита от комаров\n"
        "⚽ Мячи · ☀️ Аксессуары\n\n"
        "Доставка по всему миру 🌍\n"
        "Выбери что тебя интересует:"
    )
    keyboard = [
        [InlineKeyboardButton("🛍 Каталог товаров", callback_data="catalog")],
        [InlineKeyboardButton("🤖 AI Консультант", callback_data="ai_menu")],
        [InlineKeyboardButton("🛒 Моя корзина", callback_data="cart"),
         InlineKeyboardButton("📦 Мои заказы", callback_data="orders")],
        [InlineKeyboardButton("🚚 Доставка и оплата", callback_data="delivery"),
         InlineKeyboardButton("📞 Поддержка", callback_data="support")],
    ]
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  КАТАЛОГ — КАТЕГОРИИ
# ══════════════════════════════════════════
async def show_catalog(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = "🛍 *Каталог товаров*\n\nВыбери категорию:"
    keyboard = []
    for cat_id, cat_name in CATEGORIES.items():
        keyboard.append([InlineKeyboardButton(cat_name, callback_data=f"cat_{cat_id}")])
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main")])
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  КАТАЛОГ — ТОВАРЫ В КАТЕГОРИИ
# ══════════════════════════════════════════
async def show_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    cat_id = query.data.replace("cat_", "")
    cat_name = CATEGORIES.get(cat_id, "Товары")
    items = {k: v for k, v in PRODUCTS.items() if v["category"] == cat_id}
    text = f"{cat_name}\n\nВыбери товар:"
    keyboard = []
    for prod_id, prod in items.items():
        btn_text = f"{prod['emoji']} {prod['name'].split(' ', 1)[1]} — {prod['price']:,} ₽"
        keyboard.append([InlineKeyboardButton(btn_text, callback_data=f"prod_{prod_id}")])
    keyboard.append([InlineKeyboardButton("◀️ Назад к категориям", callback_data="catalog")])
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  КАРТОЧКА ТОВАРА
# ══════════════════════════════════════════
async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    prod_id = query.data.replace("prod_", "")
    prod = PRODUCTS.get(prod_id)
    if not prod:
        await query.edit_message_text("Товар не найден.")
        return
    cat_id = prod["category"]
    text = (
        f"{prod['emoji']} *{prod['name'].split(' ', 1)[1]}*\n\n"
        f"📝 {prod['desc']}\n\n"
        f"💰 Цена: *{prod['price']:,} ₽*\n"
        f"🚚 Доставка: бесплатно от 2,000 ₽\n"
        f"⭐ Рейтинг: 4.9 / 5.0"
    )
    keyboard = [
        [InlineKeyboardButton("🛒 Добавить в корзину", callback_data=f"add_{prod_id}")],
        [InlineKeyboardButton("⚡ Купить сейчас", callback_data=f"buy_{prod_id}")],
        [InlineKeyboardButton("◀️ Назад", callback_data=f"cat_{cat_id}")],
    ]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  ДОБАВИТЬ В КОРЗИНУ
# ══════════════════════════════════════════
async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("✅ Добавлено в корзину!")
    user_id = query.from_user.id
    prod_id = query.data.replace("add_", "")
    if user_id not in carts:
        carts[user_id] = {}
    if prod_id in carts[user_id]:
        carts[user_id][prod_id] += 1
    else:
        carts[user_id][prod_id] = 1
    prod = PRODUCTS.get(prod_id)
    cat_id = prod["category"] if prod else "pools"
    text = (
        f"✅ *Добавлено в корзину!*\n\n"
        f"{prod['emoji']} {prod['name'].split(' ', 1)[1]}\n"
        f"Количество: {carts[user_id][prod_id]} шт.\n\n"
        f"Продолжай покупки или оформи заказ!"
    )
    keyboard = [
        [InlineKeyboardButton("🛒 Перейти в корзину", callback_data="cart")],
        [InlineKeyboardButton("🛍 Продолжить покупки", callback_data=f"cat_{cat_id}")],
    ]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  КОРЗИНА
# ══════════════════════════════════════════
async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = carts.get(user_id, {})
    if not cart:
        text = "🛒 *Корзина пуста*\n\nДобавь товары из каталога!"
        keyboard = [
            [InlineKeyboardButton("🛍 Перейти в каталог", callback_data="catalog")],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main")],
        ]
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
        return

    total = 0
    text = "🛒 *Твоя корзина:*\n\n"
    keyboard = []
    for prod_id, qty in cart.items():
        prod = PRODUCTS.get(prod_id)
        if prod:
            subtotal = prod["price"] * qty
            total += subtotal
            text += f"{prod['emoji']} {prod['name'].split(' ', 1)[1]}\n"
            text += f"   {qty} шт. × {prod['price']:,} ₽ = *{subtotal:,} ₽*\n\n"
            keyboard.append([
                InlineKeyboardButton(f"❌ Убрать {prod['emoji']}", callback_data=f"rem_{prod_id}")
            ])

    text += f"━━━━━━━━━━━━━━━\n💰 *Итого: {total:,} ₽*"
    if total >= 2000:
        text += "\n🚚 Доставка: *БЕСПЛАТНО* ✅"
    else:
        text += f"\n🚚 Доставка: 300 ₽ (бесплатно от 2,000 ₽)"

    keyboard.append([InlineKeyboardButton("✅ Оформить заказ", callback_data="checkout")])
    keyboard.append([InlineKeyboardButton("🗑 Очистить корзину", callback_data="clear_cart")])
    keyboard.append([InlineKeyboardButton("🛍 Продолжить покупки", callback_data="catalog")])

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  УБРАТЬ ИЗ КОРЗИНЫ
# ══════════════════════════════════════════
async def remove_from_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Товар убран из корзины")
    user_id = query.from_user.id
    prod_id = query.data.replace("rem_", "")
    if user_id in carts and prod_id in carts[user_id]:
        del carts[user_id][prod_id]
    # Показать обновлённую корзину
    query.data = "cart"
    await show_cart(update, context)


# ══════════════════════════════════════════
#  ОЧИСТИТЬ КОРЗИНУ
# ══════════════════════════════════════════
async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer("Корзина очищена")
    user_id = query.from_user.id
    carts[user_id] = {}
    query.data = "cart"
    await show_cart(update, context)


# ══════════════════════════════════════════
#  ОФОРМЛЕНИЕ ЗАКАЗА
# ══════════════════════════════════════════
async def checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = carts.get(user_id, {})
    if not cart:
        await query.edit_message_text("Корзина пуста!")
        return

    total = sum(PRODUCTS[p]["price"] * q for p, q in cart.items() if p in PRODUCTS)

    text = (
        "📦 *Оформление заказа*\n\n"
        "Выбери способ оплаты:"
    )
    keyboard = [
        [InlineKeyboardButton("💳 Оплатить картой", callback_data="pay_card")],
        [InlineKeyboardButton("💵 Оплатить через Wise", callback_data="pay_wise")],
        [InlineKeyboardButton("🪙 Оплатить криптой", callback_data="pay_crypto")],
        [InlineKeyboardButton("📞 Связаться с менеджером", callback_data="support")],
        [InlineKeyboardButton("◀️ Назад в корзину", callback_data="cart")],
    ]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  ОПЛАТА КАРТОЙ (через Telegram Payments)
# ══════════════════════════════════════════
async def pay_card(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = carts.get(user_id, {})
    if not cart:
        return
    total = sum(PRODUCTS[p]["price"] * q for p, q in cart.items() if p in PRODUCTS)
    title = "🌞 Заказ в Summer Products"
    description = "Летние товары с доставкой по всему миру"
    payload = f"order_{user_id}"
    currency = "RUB"
    prices = [LabeledPrice("Товары", total * 100)]
    if total < 2000:
        prices.append(LabeledPrice("Доставка", 30000))
    try:
        await context.bot.send_invoice(
            chat_id=query.message.chat_id,
            title=title,
            description=description,
            payload=payload,
            provider_token=PAYMENT_TOKEN,
            currency=currency,
            prices=prices,
            need_name=True,
            need_phone_number=True,
            need_shipping_address=True,
        )
    except Exception as e:
        await query.edit_message_text(
            "💳 *Оплата картой*\n\n"
            "Для оплаты картой свяжись с менеджером:\n"
            "👉 @SummerProductsSupport\n\n"
            "Принимаем: Visa, Mastercard, МИР",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("◀️ Назад", callback_data="checkout")
            ]]),
            parse_mode="Markdown"
        )


# ══════════════════════════════════════════
#  ПРЕДВАРИТЕЛЬНАЯ ПРОВЕРКА ПЛАТЕЖА
# ══════════════════════════════════════════
async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


# ══════════════════════════════════════════
#  УСПЕШНАЯ ОПЛАТА
# ══════════════════════════════════════════
async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    payment = update.message.successful_payment
    amount = payment.total_amount // 100
    # Уведомить покупателя
    await update.message.reply_text(
        f"✅ *Оплата прошла успешно!*\n\n"
        f"Сумма: {amount:,} ₽\n"
        f"Заказ принят в обработку!\n\n"
        f"📦 Мы свяжемся с тобой в течение 2 часов для подтверждения адреса доставки.\n\n"
        f"Спасибо за покупку! 🌞",
        parse_mode="Markdown"
    )
    # Уведомить администратора
    user_info = (
        f"🛍 *НОВЫЙ ЗАКАЗ!*\n\n"
        f"👤 Покупатель: {user.full_name}\n"
        f"📱 Username: @{user.username or 'нет'}\n"
        f"🆔 ID: {user.id}\n"
        f"💰 Сумма: {amount:,} ₽\n"
        f"🏦 Способ оплаты: Карта"
    )
    try:
        await context.bot.send_message(ADMIN_ID, user_info, parse_mode="Markdown")
    except Exception:
        pass
    carts[user.id] = {}


# ══════════════════════════════════════════
#  ОПЛАТА ЧЕРЕЗ WISE
# ══════════════════════════════════════════
async def pay_wise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = carts.get(user_id, {})
    total = sum(PRODUCTS[p]["price"] * q for p, q in cart.items() if p in PRODUCTS)
    total_usd = round(total / 90, 2)
    text = (
        f"💵 *Оплата через Wise*\n\n"
        f"Сумма к оплате: *${total_usd}*\n\n"
        f"Реквизиты Wise:\n"
        f"Email: your@email.com\n"
        f"Имя: ВСТАВЬ_СВОЁ_ИМЯ\n\n"
        f"После оплаты нажми кнопку ниже и пришли скриншот!"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Я оплатил — прислать скриншот", callback_data="paid_wise")],
        [InlineKeyboardButton("◀️ Назад", callback_data="checkout")],
    ]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  ОПЛАТА КРИПТОЙ
# ══════════════════════════════════════════
async def pay_crypto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    cart = carts.get(user_id, {})
    total = sum(PRODUCTS[p]["price"] * q for p, q in cart.items() if p in PRODUCTS)
    total_usdt = round(total / 90, 2)
    text = (
        f"🪙 *Оплата криптовалютой*\n\n"
        f"Принимаем: USDT (TRC20), TON, Bitcoin\n\n"
        f"Сумма: *{total_usdt} USDT*\n\n"
        f"Кошелёк USDT TRC20:\n"
        f"`ВСТАВЬ_СВОЙ_КОШЕЛЁК`\n\n"
        f"После оплаты пришли хэш транзакции!"
    )
    keyboard = [
        [InlineKeyboardButton("✅ Я оплатил", callback_data="paid_crypto")],
        [InlineKeyboardButton("◀️ Назад", callback_data="checkout")],
    ]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  ПОДТВЕРЖДЕНИЕ ОПЛАТЫ (Wise/Crypto)
# ══════════════════════════════════════════
async def paid_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    method = "Wise" if "wise" in query.data else "Крипта"
    text = (
        f"✅ *Отлично!*\n\n"
        f"Пришли скриншот или хэш оплаты следующим сообщением.\n"
        f"Менеджер проверит в течение 30 минут и подтвердит заказ!"
    )
    context.user_data["awaiting_payment_proof"] = True
    context.user_data["payment_method"] = method
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  ПОЛУЧЕНИЕ СКРИНШОТА ОПЛАТЫ
# ══════════════════════════════════════════
async def receive_payment_proof(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("awaiting_payment_proof"):
        return
    user = update.effective_user
    method = context.user_data.get("payment_method", "Неизвестно")
    # Переслать скриншот/сообщение админу
    try:
        await context.bot.send_message(
            ADMIN_ID,
            f"💰 *ПОДТВЕРЖДЕНИЕ ОПЛАТЫ*\n\n"
            f"👤 {user.full_name} (@{user.username or 'нет'})\n"
            f"🆔 ID: {user.id}\n"
            f"💳 Способ: {method}",
            parse_mode="Markdown"
        )
        await update.message.forward(ADMIN_ID)
    except Exception:
        pass
    context.user_data["awaiting_payment_proof"] = False
    carts[user.id] = {}
    await update.message.reply_text(
        "✅ *Скриншот получен!*\n\n"
        "Менеджер проверит оплату и свяжется с тобой в течение 30 минут.\n\n"
        "Спасибо за покупку! 🌞",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("🏠 Главное меню", callback_data="main")
        ]])
    )


# ══════════════════════════════════════════
#  ДОСТАВКА И ОПЛАТА
# ══════════════════════════════════════════
async def show_delivery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "🚚 *Доставка и оплата*\n\n"
        "📦 *Доставка:*\n"
        "• По России — 1-3 дня, от 300 ₽\n"
        "• Бесплатно при заказе от 2,000 ₽\n"
        "• СНГ — 5-10 дней\n"
        "• Весь мир — 7-21 день\n\n"
        "💳 *Способы оплаты:*\n"
        "• Карта Visa/Mastercard/МИР\n"
        "• Wise (международный перевод)\n"
        "• USDT, TON, Bitcoin\n"
        "• Наличными при получении (Россия)\n\n"
        "🔒 *Гарантия:*\n"
        "• Возврат 14 дней без вопросов\n"
        "• Бесплатный обмен при браке\n"
        "• Отслеживание посылки онлайн"
    )
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  ПОДДЕРЖКА
# ══════════════════════════════════════════
async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📞 *Поддержка*\n\n"
        "Мы всегда на связи!\n\n"
        "💬 Telegram: @SummerProductsSupport\n"
        "📧 Email: support@summerproducts.com\n"
        "⏰ Режим работы: 9:00-21:00 МСК\n\n"
        "Среднее время ответа: 15 минут"
    )
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  ГЛАВНОЕ МЕНЮ (кнопка назад)
# ══════════════════════════════════════════
async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    text = (
        f"🌞 *Summer Products*\n\n"
        "Лучшие летние товары с доставкой по всему миру!\n\n"
        "🏊 Бассейны · 🦟 Защита от комаров\n"
        "⚽ Мячи · ☀️ Аксессуары\n\n"
        "Выбери что тебя интересует:"
    )
    keyboard = [
        [InlineKeyboardButton("🛍 Каталог товаров", callback_data="catalog")],
        [InlineKeyboardButton("🤖 AI Консультант", callback_data="ai_menu")],
        [InlineKeyboardButton("🛒 Моя корзина", callback_data="cart"),
         InlineKeyboardButton("📦 Мои заказы", callback_data="orders")],
        [InlineKeyboardButton("🚚 Доставка и оплата", callback_data="delivery"),
         InlineKeyboardButton("📞 Поддержка", callback_data="support")],
    ]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  МОИ ЗАКАЗЫ (заглушка)
# ══════════════════════════════════════════
async def show_orders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        "📦 *Мои заказы*\n\n"
        "История заказов появится здесь после первой покупки.\n\n"
        "Для отслеживания заказа напиши нам:\n"
        "@SummerProductsSupport"
    )
    keyboard = [[InlineKeyboardButton("◀️ Главное меню", callback_data="main")]]
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


# ══════════════════════════════════════════
#  AI АССИСТЕНТ
# ══════════════════════════════════════════

AI_SYSTEM = """Ты — дружелюбный AI ассистент магазина Summer Products.
Магазин продаёт летние товары: бассейны, ловушки для комаров, футбольные мячи, солнечные очки, вентиляторы, кремы от солнца.

Цены:
- Каркасный бассейн малый (200×50 см) — 4,990 руб
- Каркасный бассейн средний (300×76 см) — 8,990 руб
- Бассейн-домик надувной — 24,990 руб
- UV ловушка для комаров — 1,990 руб
- Газовая ловушка CO2 — 12,990 руб
- Футбольный мяч размер 3 — 890 руб
- Футбольный мяч размер 4 — 1,190 руб
- Солнечные очки UV400 — 790 руб
- Портативный вентилятор — 690 руб
- Солнцезащитный крем SPF50 — 590 руб

Доставка по всему миру. Оплата: карта, Wise, криптовалюта.
Отвечай на русском языке. Будь вежлив, помогай выбрать товар.
Если спрашивают про заказ — предложи нажать /start чтобы перейти в каталог.
Отвечай кратко — не более 3-4 предложений."""

ai_conversations = {}

async def ask_claude(user_id: int, user_message: str) -> str:
    if user_id not in ai_conversations:
        ai_conversations[user_id] = []
    
    ai_conversations[user_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Храним только последние 10 сообщений
    if len(ai_conversations[user_id]) > 10:
        ai_conversations[user_id] = ai_conversations[user_id][-10:]
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": CLAUDE_API_KEY,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 500,
                    "system": AI_SYSTEM,
                    "messages": ai_conversations[user_id]
                }
            )
            data = response.json()
            reply = data["content"][0]["text"]
            
            ai_conversations[user_id].append({
                "role": "assistant",
                "content": reply
            })
            return reply
    except Exception as e:
        logger.error(f"Claude API error: {e}")
        return "Извините, AI консультант временно недоступен. Напишите нам: @SummerProductsSupport"


async def ai_consultant(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать меню AI консультанта"""
    keyboard = [
        [InlineKeyboardButton("💬 Задать вопрос", callback_data="ai_ask")],
        [InlineKeyboardButton("🏊 Помоги выбрать бассейн", callback_data="ai_pool")],
        [InlineKeyboardButton("🦟 Помоги с защитой от комаров", callback_data="ai_mosquito")],
        [InlineKeyboardButton("⚽ Помоги выбрать мяч", callback_data="ai_ball")],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main")],
    ]
    text = (
        "🤖 *AI Консультант Summer Products*\n\n"
        "Я помогу выбрать лучший летний товар!\n"
        "Задай любой вопрос или выбери категорию:"
    )
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )


async def ai_ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Предложить задать вопрос"""
    query = update.callback_query
    await query.answer()
    
    # Быстрые вопросы по категории
    cat = query.data.replace("ai_", "")
    quick_questions = {
        "pool": "Какой бассейн лучше для детей?",
        "mosquito": "Какая ловушка эффективнее от комаров?",
        "ball": "Какой мяч выбрать для ребёнка 7 лет?",
        "ask": None
    }
    
    if cat in quick_questions and quick_questions[cat]:
        # Автоматически задаём вопрос
        user_id = query.from_user.id
        question = quick_questions[cat]
        await query.edit_message_text(f"🤔 *{question}*\n\nИщу ответ...", parse_mode="Markdown")
        reply = await ask_claude(user_id, question)
        keyboard = [
            [InlineKeyboardButton("💬 Задать свой вопрос", callback_data="ai_input")],
            [InlineKeyboardButton("🛍 Перейти в каталог", callback_data="catalog")],
            [InlineKeyboardButton("🤖 AI Консультант", callback_data="ai_menu")],
        ]
        await query.edit_message_text(
            f"🤖 *AI Консультант:*\n\n{reply}",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        # Ждём вопрос от пользователя
        context.user_data["waiting_ai_question"] = True
        await query.edit_message_text(
            "💬 *Задай свой вопрос*\n\n"
            "Напиши что тебя интересует — я отвечу!\n\n"
            "_Например: Какой бассейн лучше для дачи?_",
            parse_mode="Markdown"
        )


async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка сообщений для AI консультанта"""
    if context.user_data.get("waiting_ai_question") or context.user_data.get("awaiting_payment_proof"):
        if context.user_data.get("awaiting_payment_proof"):
            await receive_payment_proof(update, context)
            return
            
        if context.user_data.get("waiting_ai_question"):
            user_id = update.effective_user.id
            question = update.message.text
            context.user_data["waiting_ai_question"] = False
            
            thinking_msg = await update.message.reply_text(
                "🤖 *Думаю над ответом...*",
                parse_mode="Markdown"
            )
            
            reply = await ask_claude(user_id, question)
            
            keyboard = [
                [InlineKeyboardButton("💬 Ещё вопрос", callback_data="ai_input")],
                [InlineKeyboardButton("🛍 Перейти в каталог", callback_data="catalog")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main")],
            ]
            
            await thinking_msg.delete()
            await update.message.reply_text(
                f"🤖 *AI Консультант:*\n\n{reply}",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )


# ══════════════════════════════════════════
#  ЗАПУСК БОТА
# ══════════════════════════════════════════
def main():
    app = Application.builder().token(TOKEN).build()

    # Команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("catalog", lambda u, c: show_catalog(u, c)))
    app.add_handler(CommandHandler("cart", lambda u, c: show_cart(u, c)))

    # Callback handlers
    app.add_handler(CallbackQueryHandler(show_catalog, pattern="^catalog$"))
    app.add_handler(CallbackQueryHandler(show_category, pattern="^cat_"))
    app.add_handler(CallbackQueryHandler(show_product, pattern="^prod_"))
    app.add_handler(CallbackQueryHandler(add_to_cart, pattern="^add_"))
    app.add_handler(CallbackQueryHandler(show_cart, pattern="^cart$"))
    app.add_handler(CallbackQueryHandler(remove_from_cart, pattern="^rem_"))
    app.add_handler(CallbackQueryHandler(clear_cart, pattern="^clear_cart$"))
    app.add_handler(CallbackQueryHandler(checkout, pattern="^checkout$"))
    app.add_handler(CallbackQueryHandler(pay_card, pattern="^pay_card$"))
    app.add_handler(CallbackQueryHandler(pay_wise, pattern="^pay_wise$"))
    app.add_handler(CallbackQueryHandler(pay_crypto, pattern="^pay_crypto$"))
    app.add_handler(CallbackQueryHandler(paid_confirm, pattern="^paid_"))
    app.add_handler(CallbackQueryHandler(show_delivery, pattern="^delivery$"))
    app.add_handler(CallbackQueryHandler(show_support, pattern="^support$"))
    app.add_handler(CallbackQueryHandler(show_orders, pattern="^orders$"))
    app.add_handler(CallbackQueryHandler(main_menu, pattern="^main$"))

    # Платежи
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    # AI Консультант
    app.add_handler(CallbackQueryHandler(ai_consultant, pattern="^ai_menu$"))
    app.add_handler(CallbackQueryHandler(ai_ask_question, pattern="^ai_"))

    # Сообщения — AI и оплата
    app.add_handler(MessageHandler(
        filters.PHOTO | filters.Document.ALL | filters.TEXT & ~filters.COMMAND,
        handle_ai_message
    ))

    print("🌞 Бот Summer Products запущен!")
    print("Нажми Ctrl+C для остановки")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
