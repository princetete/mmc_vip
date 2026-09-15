import os
import sqlite3
import logging
from datetime import datetime, timedelta, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    PreCheckoutQueryHandler, ContextTypes, filters
)

BOT_TOKEN = os.environ["BOT_TOKEN"]
ADMIN_ID = 1132914072

UPI_ID = "princeroshantete@oksbi"
UPI_AMOUNT = "₹1,500"
BINANCE_ID = "462584728"
BINANCE_AMOUNT = "$20"
USDT_AMOUNT = "$20"
USDT_NETWORK = "TRON (TRC20)"
USDT_ADDRESS = "TYnkPKrWSM4t9pHUEXkpn5RSmaVD88RPaB"
STARS_AMOUNT = 1500

UPI_QR_PATH = "upi_qr.png"
USDT_QR_PATH = "usdt_trc20_qr.jpg"

VIP_RESOURCES = -1003822415883
VIP_FILES = -1003804517341
VIP_VIDEOS = -1003488961204
MONEY_TALKS = -1003881674854
GROWTH_TALKS = -1003876546032

PUBLIC_COURSES_URL = "https://t.me/VIP_Coursesss"
REVIEWS_URL = "https://t.me/VIP_Coursesss/2418"
SUPPORT_URL = "https://t.me/Elliotnex"

PRIVATE_CHATS = [
    ("VIP Resources", VIP_RESOURCES),
    ("VIP Files", VIP_FILES),
    ("VIP Videos", VIP_VIDEOS),
    ("Money Talks", MONEY_TALKS),
    ("Growth Talks", GROWTH_TALKS),
]

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)
DB_FILE = "payments.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL,
        username TEXT, first_name TEXT, plan TEXT, amount TEXT, method TEXT,
        screenshot_file_id TEXT, status TEXT DEFAULT 'pending',
        telegram_payment_charge_id TEXT, created_at TEXT)""")
    conn.commit(); conn.close()

def create_payment(user_id, username, first_name, plan, amount, method):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("""INSERT INTO payments
        (user_id,username,first_name,plan,amount,method,status,created_at)
        VALUES (?,?,?,?,?,?,?,?)""",
        (user_id, username, first_name, plan, amount, method, "awaiting_proof",
         datetime.now(timezone.utc).isoformat()))
    payment_id = cur.lastrowid
    conn.commit(); conn.close()
    return payment_id

def get_payment(payment_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.execute("""SELECT id,user_id,username,first_name,plan,amount,method,
        screenshot_file_id,status,telegram_payment_charge_id,created_at
        FROM payments WHERE id=?""", (payment_id,))
    row = cur.fetchone(); conn.close()
    return row

def update_payment_status(payment_id, status):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE payments SET status=? WHERE id=?", (status, payment_id))
    conn.commit(); conn.close()

def save_screenshot(payment_id, file_id):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("UPDATE payments SET screenshot_file_id=? WHERE id=?", (file_id, payment_id))
    conn.commit(); conn.close()

def save_stars_charge(payment_id, charge_id):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("""UPDATE payments SET status=?,telegram_payment_charge_id=? WHERE id=?""",
                 ("approved", charge_id, payment_id))
    conn.commit(); conn.close()

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 BUY VIP", callback_data="buy")],
        [InlineKeyboardButton("📚 CATALOGUE", callback_data="catalogue")],
        [InlineKeyboardButton("⭐ REVIEWS", url=REVIEWS_URL)],
        [InlineKeyboardButton("📩 CONTACT SUPPORT", url=SUPPORT_URL)],
    ])

def payment_methods_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇮🇳 UPI — ₹1,500", callback_data="pay_upi")],
        [InlineKeyboardButton("💱 Binance — $20", callback_data="pay_binance")],
        [InlineKeyboardButton("🪙 USDT — $20", callback_data="pay_usdt")],
        [InlineKeyboardButton("⭐ Telegram Stars — 1,500", callback_data="pay_stars")],
        [InlineKeyboardButton("⬅️ BACK", callback_data="back_start")],
    ])

def paid_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ I'VE PAID", callback_data="paid")],
        [InlineKeyboardButton("⬅️ BACK", callback_data="buy")],
    ])

START_TEXT = """👋 Welcome to the VIP Payment Bot

🚀 Your gateway to premium access.

Explore complete collection of premium courses, resources & tools.

Payment methods:

🇮🇳 UPI — ₹1,500
💱 Binance — $20
🪙 Crypto (USDT) — $20
⭐ Telegram Stars — 1,500

Active hours:

🇮🇳 India: 05:00 PM – 10:00 PM
🇬🇧 UK: 12:30 PM – 05:30 PM
🇺🇸 USA: 07:30 AM – 12:30 PM
🇦🇪 Gulf: 03:30 PM – 08:30 PM

Payment verification notice:
1–6 hours during active hours.
"""

async def start(update, context):
    context.user_data.clear()
    await update.message.reply_text(START_TEXT, reply_markup=main_menu_keyboard())

async def buy(update, context):
    q = update.callback_query
    if q:
        await q.answer()
        await q.edit_message_text(
            """💎 VIP LIFETIME ACCESS

Get lifetime access to the complete VIP collection.

━━━━━━━━━━━━━━━━━━

💰 PAYMENT OPTIONS

🇮🇳 UPI
₹1,500

💱 Binance
$20

🪙 USDT
$20

⭐ Telegram Stars
1,500 Stars

━━━━━━━━━━━━━━━━━━

🔐 Lifetime access
📚 Courses
📦 Resources
🎬 Files & Videos
💬 Private communities
""",
            reply_markup=payment_methods_keyboard())
    else:
        await update.message.reply_text("Choose your payment method:",
                                        reply_markup=payment_methods_keyboard())

async def catalogue_command(update, context):
    await catalogue(update, context)

async def reviews_command(update, context):
    await update.message.reply_text("⭐ Reviews:", reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("⭐ VIEW REVIEWS", url=REVIEWS_URL)]]))

async def contact_command(update, context):
    await update.message.reply_text("📩 Contact support:", reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("📩 CONTACT SUPPORT", url=SUPPORT_URL)]]))

async def cancel(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ Payment process cancelled.\n\nUse /start to begin again.",
                                    reply_markup=main_menu_keyboard())

async def pay_upi(update, context):
    q = update.callback_query; await q.answer()
    context.user_data["payment_method"] = "UPI"
    caption = f"""🇮🇳 UPI PAYMENT

Amount: {UPI_AMOUNT}

━━━━━━━━━━━━━━━━━━

Scan the QR code above

OR

UPI ID:

`{UPI_ID}`

━━━━━━━━━━━━━━━━━━

After completing the payment,
tap **I'VE PAID** below.
"""
    if os.path.exists(UPI_QR_PATH):
        with open(UPI_QR_PATH, "rb") as photo:
            await q.message.reply_photo(photo=photo, caption=caption,
                                         parse_mode="Markdown", reply_markup=paid_keyboard())
    else:
        await q.message.reply_text(caption, parse_mode="Markdown", reply_markup=paid_keyboard())

async def pay_binance(update, context):
    q = update.callback_query; await q.answer()
    context.user_data["payment_method"] = "Binance"
    text = f"""💱 BINANCE PAYMENT

Amount: {BINANCE_AMOUNT}

━━━━━━━━━━━━━━━━━━

Send {BINANCE_AMOUNT} to:

Binance ID:

`{BINANCE_ID}`

━━━━━━━━━━━━━━━━━━

After completing the payment,
tap **I'VE PAID** below.
"""
    await q.message.reply_text(text, parse_mode="Markdown", reply_markup=paid_keyboard())

async def pay_usdt(update, context):
    q = update.callback_query; await q.answer()
    context.user_data["payment_method"] = "USDT"
    caption = f"""🪙 USDT PAYMENT

Amount: {USDT_AMOUNT}

Network: {USDT_NETWORK}

━━━━━━━━━━━━━━━━━━

USDT Address:

`{USDT_ADDRESS}`

━━━━━━━━━━━━━━━━━━

Send only through the TRON (TRC20)
network.

After completing the payment,
tap **I'VE PAID** below.
"""
    if os.path.exists(USDT_QR_PATH):
        with open(USDT_QR_PATH, "rb") as photo:
            await q.message.reply_photo(photo=photo, caption=caption,
                                         parse_mode="Markdown", reply_markup=paid_keyboard())
    else:
        await q.message.reply_text(caption, parse_mode="Markdown", reply_markup=paid_keyboard())

async def paid_button(update, context):
    q = update.callback_query; await q.answer()
    method = context.user_data.get("payment_method")
    if method not in ["UPI", "Binance", "USDT"]:
        await q.message.reply_text("❌ Payment session expired.\n\nPlease go back and select a payment method again.")
        return
    u = q.from_user
    payment_id = create_payment(u.id, u.username, u.first_name, "Lifetime",
                                {"UPI": UPI_AMOUNT, "Binance": BINANCE_AMOUNT, "USDT": USDT_AMOUNT}[method],
                                method)
    context.user_data["payment_id"] = payment_id
    context.user_data["awaiting_proof"] = True
    try:
        await q.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning("Could not remove payment buttons: %s", e)
    await q.message.reply_text("""📸 PAYMENT PROOF

Please send a clear screenshot of your payment.

Make sure the screenshot shows:

• Amount
• Payment status
• Relevant payment details

⚠️ Manual verification

📸 Send your screenshot below.

You can also send /cancel.
""")

async def receive_payment_proof(update, context):
    if not context.user_data.get("awaiting_proof"):
        return
    payment_id = context.user_data.get("payment_id")
    if not payment_id:
        await update.message.reply_text("❌ Payment session expired.\n\nPlease start again with /start.")
        context.user_data.clear(); return
    payment = get_payment(payment_id)
    if not payment:
        await update.message.reply_text("❌ Payment record not found."); return
    if payment[8] not in ["awaiting_proof", "pending"]:
        await update.message.reply_text("This payment has already been processed.")
        context.user_data.clear(); return
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith("image/"):
        file_id = update.message.document.file_id
    else:
        await update.message.reply_text("📸 Please send the payment screenshot as an image/photo.")
        return
    save_screenshot(payment_id, file_id)
    update_payment_status(payment_id, "proof_submitted")
    context.user_data["awaiting_proof"] = False
    await update.message.reply_text("""✅ PAYMENT PROOF RECEIVED

Your payment screenshot has been submitted
for manual verification.

⏳ Verification may take 1–6 hours during
active hours.

You will receive your VIP access automatically
after approval.
""")
    u = update.effective_user
    username = f"@{u.username}" if u.username else "No username"
    admin_text = f"""💰 NEW PAYMENT PROOF

Payment ID: #{payment_id}

👤 User:
{u.first_name}

🆔 Telegram ID:
{u.id}

📱 Username:
{username}

━━━━━━━━━━━━━━━━━━

💳 Method:
{payment[6]}

💰 Amount:
{payment[5]}

📦 Plan:
{payment[4]}

━━━━━━━━━━━━━━━━━━

Please verify the payment.
"""
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ APPROVE", callback_data=f"approve:{payment_id}"),
        InlineKeyboardButton("❌ REJECT", callback_data=f"reject:{payment_id}")
    ]])
    try:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=file_id, caption=admin_text, reply_markup=kb)
    except Exception as e:
        logger.exception("Failed to send payment proof to admin: %s", e)

async def create_vip_links(context, payment_id):
    links = []
    expire_date = datetime.now(timezone.utc) + timedelta(hours=24)
    for name, chat_id in PRIVATE_CHATS:
        invite = await context.bot.create_chat_invite_link(
            chat_id=chat_id, name=f"VIP-{payment_id}",
            expire_date=expire_date, member_limit=1)
        links.append((name, invite.invite_link))
    return links

async def send_vip_access(context, user_id, payment_id):
    links = await create_vip_links(context, payment_id)
    buttons = [[InlineKeyboardButton("📚 ACCESS COURSES", url=PUBLIC_COURSES_URL)]]
    for name, link in links:
        buttons.append([InlineKeyboardButton(f"🔐 JOIN {name.upper()}", url=link)])
    await context.bot.send_message(
        chat_id=user_id,
        text="""🎉 Congratulations on Purchasing VIP!

Your payment has been successfully verified. ✅

━━━━━━━━━━━━━━━━━━

📚 MATERIALS

🎓 VIP Courses
📦 VIP Resources

━━━━━━━━━━━━━━━━━━

🎬 MEDIA

📁 VIP Files
🎥 VIP Videos

━━━━━━━━━━━━━━━━━━

💬 CHATTING

💰 Money Talks
📈 Growth Talks

━━━━━━━━━━━━━━━━━━

🔐 All links are personal and one-time use.
""",
        reply_markup=InlineKeyboardMarkup(buttons))

async def approve_payment(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer("❌ You are not authorized.", show_alert=True); return
    await q.answer()
    try: payment_id = int(q.data.split(":")[1])
    except Exception: return
    payment = get_payment(payment_id)
    if not payment:
        await q.message.reply_text("❌ Payment not found."); return
    if payment[8] == "approved":
        await q.answer("Already approved.", show_alert=True); return
    if payment[8] == "rejected":
        await q.answer("This payment was already rejected.", show_alert=True); return
    try:
        await send_vip_access(context, payment[1], payment_id)
        update_payment_status(payment_id, "approved")
        try:
            await q.edit_message_caption(caption=f"✅ PAYMENT APPROVED\n\nPayment ID: #{payment_id}\nUser ID: {payment[1]}",
                                         reply_markup=None)
        except Exception:
            try:
                await q.edit_message_text(text=f"✅ PAYMENT APPROVED\n\nPayment ID: #{payment_id}\nUser ID: {payment[1]}",
                                           reply_markup=None)
            except Exception: pass
    except Exception as e:
        logger.exception("Approval failed: %s", e)
        await q.message.reply_text("❌ Approval failed.\n\nMake sure the bot is an administrator in all VIP groups/channels and can manage invite links.")

async def reject_payment(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer("❌ You are not authorized.", show_alert=True); return
    await q.answer()
    try: payment_id = int(q.data.split(":")[1])
    except Exception: return
    payment = get_payment(payment_id)
    if not payment: return
    if payment[8] in ["approved", "rejected"]:
        await q.answer("Payment already processed.", show_alert=True); return
    update_payment_status(payment_id, "rejected")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("📩 CONTACT SUPPORT", url=SUPPORT_URL)]])
    try:
        await context.bot.send_message(chat_id=payment[1],
            text="""❌ PAYMENT NOT VERIFIED

Unfortunately, we couldn't verify your payment.

If you believe this is a mistake, please contact support.""",
            reply_markup=kb)
    except Exception as e:
        logger.warning("Could not notify rejected user: %s", e)
    try:
        await q.edit_message_caption(caption=f"❌ PAYMENT REJECTED\n\nPayment ID: #{payment_id}\nUser ID: {payment[1]}",
                                     reply_markup=None)
    except Exception:
        try:
            await q.edit_message_text(text=f"❌ PAYMENT REJECTED\n\nPayment ID: #{payment_id}\nUser ID: {payment[1]}",
                                       reply_markup=None)
        except Exception: pass

async def pay_stars(update, context):
    q = update.callback_query; await q.answer()
    u = q.from_user
    payment_id = create_payment(u.id, u.username, u.first_name, "Lifetime",
                                f"{STARS_AMOUNT} Stars", "Telegram Stars")
    context.user_data["stars_payment_id"] = payment_id
    await context.bot.send_invoice(
        chat_id=u.id, title="VIP Lifetime Access",
        description="Lifetime access to the VIP courses, resources, files, videos and communities.",
        payload=f"vip_stars:{payment_id}", currency="XTR",
        prices=[LabeledPrice(label="VIP Lifetime Access", amount=STARS_AMOUNT)])

async def precheckout_callback(update, context):
    await update.pre_checkout_query.answer(ok=True)

async def successful_payment(update, context):
    payment = update.message.successful_payment
    if not payment or not payment.invoice_payload.startswith("vip_stars:"): return
    try: payment_id = int(payment.invoice_payload.split(":")[1])
    except Exception: return
    if not get_payment(payment_id):
        await update.message.reply_text("❌ Payment record not found. Please contact support."); return
    try:
        save_stars_charge(payment_id, payment.telegram_payment_charge_id)
        await send_vip_access(context, update.effective_user.id, payment_id)
    except Exception as e:
        logger.exception("Stars fulfillment failed: %s", e)
        await update.message.reply_text("✅ Payment received.\n\nThere was a temporary issue generating your VIP access links.\n\nPlease contact support.")

CATALOGUE = {
    "AI": [("AI Automations","https://t.me/VIP_Coursesss/774"),("AI Content Creation","https://t.me/VIP_Coursesss/1129")],
    "Business": [("Real Estate","https://t.me/VIP_Coursesss/18"),("Personal Brand","https://t.me/VIP_Coursesss/293"),("Agency","https://t.me/VIP_Coursesss/501"),("Freelancing","https://t.me/VIP_Coursesss/30"),("Coaching","https://t.me/VIP_Coursesss/50"),("Business","https://t.me/VIP_Coursesss/931")],
    "Sales & Marketing": [("Sales & Leads","https://t.me/VIP_Coursesss/522"),("Ads","https://t.me/VIP_Coursesss/955"),("Copywriting","https://t.me/VIP_Coursesss/1074"),("Affiliate Marketing","https://t.me/VIP_Coursesss/645"),("Email Marketing","https://t.me/VIP_Coursesss/753")],
    "Ecommerce": [("Drop-servicing","https://t.me/VIP_Coursesss/3"),("Digital Products","https://t.me/VIP_Coursesss/722"),("E-Com","https://t.me/VIP_Coursesss/894")],
    "Social Media": [("Instagram","https://t.me/VIP_Coursesss/310"),("YouTube","https://t.me/VIP_Coursesss/1045"),("TikTok","https://t.me/VIP_Coursesss/194"),("Twitter","https://t.me/VIP_Coursesss/13"),("Threads","https://t.me/VIP_Coursesss/10"),("Facebook","https://t.me/VIP_Coursesss/23"),("LinkedIn","https://t.me/VIP_Coursesss/77"),("Pinterest","https://t.me/VIP_Coursesss/115")],
    "Content": [("Content Creation","https://t.me/VIP_Coursesss/697"),("Video Editing","https://t.me/VIP_Coursesss/345"),("Graphic Design","https://t.me/VIP_Coursesss/278"),("Filmmaking","https://t.me/VIP_Coursesss/39"),("Animation","https://t.me/VIP_Coursesss/127")],
    "Web & Tech": [("UI/UX","https://t.me/VIP_Coursesss/674"),("SEO","https://t.me/VIP_Coursesss/595")],
    "Personal Development": [("Self Improvement","https://t.me/VIP_Coursesss/450"),("Fitness","https://t.me/VIP_Coursesss/401"),("Self Defence","https://t.me/VIP_Coursesss/161"),("Memory","https://t.me/VIP_Coursesss/221"),("Communication","https://t.me/VIP_Coursesss/90"),("NLP & Hypnosis","https://t.me/VIP_Coursesss/1004"),("Psychology","https://t.me/VIP_Coursesss/628")],
    "Luxury": [("History Courses","https://t.me/VIP_Coursesss/392"),("Peterson Academy","https://t.me/VIP_Coursesss/1327"),("Andrew Tate — TRW","https://t.me/VIP_Coursesss/1238"),("Iman Gadzhi — Educate IO","https://t.me/VIP_Coursesss/1199"),("Luke Belmar — Capital Club","https://t.me/VIP_Coursesss/1288"),("Business","https://t.me/VIP_Coursesss/931")],
}

async def catalogue(update, context):
    q = update.callback_query; await q.answer()
    buttons = [[InlineKeyboardButton(f"📂 {cat}", callback_data=f"cat:{cat}")] for cat in CATALOGUE]
    buttons.append([InlineKeyboardButton("⬅️ BACK", callback_data="back_start")])
    await q.edit_message_text("""📚 VIP COURSES

VIP Courses are structured across 40+ sub-topics.

Choose a category below:
""", reply_markup=InlineKeyboardMarkup(buttons))

async def catalogue_category(update, context):
    q = update.callback_query; await q.answer()
    category = q.data.split(":",1)[1]
    buttons = [[InlineKeyboardButton(f"📘 {name}", url=url)] for name,url in CATALOGUE.get(category,[])]
    buttons.append([InlineKeyboardButton("⬅️ CATALOGUE", callback_data="catalogue")])
    await q.edit_message_text(f"📚 {category.upper()}\n\nSelect a sub-topic:",
                              reply_markup=InlineKeyboardMarkup(buttons))

async def back_start(update, context):
    q = update.callback_query; await q.answer()
    context.user_data.clear()
    await q.edit_message_text(START_TEXT, reply_markup=main_menu_keyboard())

async def error_handler(update, context):
    logger.exception("Unhandled exception:", exc_info=context.error)

def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("buy", buy))
    app.add_handler(CommandHandler("catalogue", catalogue_command))
    app.add_handler(CommandHandler("reviews", reviews_command))
    app.add_handler(CommandHandler("contact", contact_command))
    app.add_handler(CommandHandler("cancel", cancel))

    app.add_handler(CallbackQueryHandler(buy, pattern=r"^buy$"))
    app.add_handler(CallbackQueryHandler(catalogue, pattern=r"^catalogue$"))
    app.add_handler(CallbackQueryHandler(catalogue_category, pattern=r"^cat:"))
    app.add_handler(CallbackQueryHandler(back_start, pattern=r"^back_start$"))
    app.add_handler(CallbackQueryHandler(pay_upi, pattern=r"^pay_upi$"))
    app.add_handler(CallbackQueryHandler(pay_binance, pattern=r"^pay_binance$"))
    app.add_handler(CallbackQueryHandler(pay_usdt, pattern=r"^pay_usdt$"))
    app.add_handler(CallbackQueryHandler(pay_stars, pattern=r"^pay_stars$"))
    app.add_handler(CallbackQueryHandler(paid_button, pattern=r"^paid$"))
    app.add_handler(CallbackQueryHandler(approve_payment, pattern=r"^approve:"))
    app.add_handler(CallbackQueryHandler(reject_payment, pattern=r"^reject:"))
    app.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, receive_payment_proof))
    app.add_error_handler(error_handler)

    print("🚀 VIP Payment Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
