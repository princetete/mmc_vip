import os
from dotenv import load_dotenv

load_dotenv()

import html as html_lib
import sqlite3
import logging
from datetime import datetime, timedelta, timezone

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler,
    ContextTypes, filters
)

BOT_TOKEN = os.environ ["BOT_TOKEN"]
ADMIN_ID = 1132914072

UPI_ID = "princeroshantete@oksbi"
UPI_AMOUNT = "₹1,500"
BINANCE_ID = "462584728"
BINANCE_AMOUNT = "$20"
USDT_AMOUNT = "$20"
USDT_NETWORK = "TRON (TRC20)"
USDT_ADDRESS = "TYnkPKrWSM4t9pHUEXkpn5RSmaVD88RPaB"
BTC_AMOUNT = "$20"
BTC_ADDRESS = "164fBBFhFtSTHq73QXGRo67yBypFKgxJhg"

UPI_QR_PATH = "upi_qr.png"
USDT_QR_PATH = "usdt_trc20_qr.jpg"
BTC_QR_PATH = "btc_qr.jpg"

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

DIVIDER = "━━━━━━━━━━━━━━━━━━"

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

def main_menu_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎  BUY VIP", callback_data="buy")],
        [InlineKeyboardButton("📚  CATALOGUE", callback_data="catalogue")],
        [InlineKeyboardButton("⭐  REVIEWS", url=REVIEWS_URL)],
        [InlineKeyboardButton("📩  SUPPORT", url=SUPPORT_URL)],
    ])

def payment_methods_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(f"🇮🇳  UPI  —  {UPI_AMOUNT}", callback_data="pay_upi")],
        [InlineKeyboardButton(f"💸  Binance Pay  —  {BINANCE_AMOUNT}", callback_data="pay_binance")],
        [InlineKeyboardButton(f"🪙  USDT  —  {USDT_AMOUNT}", callback_data="pay_usdt")],
        [InlineKeyboardButton(f"₿  BTC  —  {BTC_AMOUNT}", callback_data="pay_btc")],
        [InlineKeyboardButton("⬅️   BACK", callback_data="back_start")],
    ])

def paid_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅  I'VE PAID", callback_data="paid")],
        [InlineKeyboardButton("⬅️  BACK", callback_data="buy")],
    ])

START_TEXT = f"""<b>👋 Welcome to the VIP Payment Bot</b>

🚀 <i>Your gateway to premium access</i>

Explore our complete collection of premium courses, resources &amp; tools all in one place.

{DIVIDER}
<b>💳 PAYMENT METHODS</b>

🇮🇳  UPI  —  {UPI_AMOUNT}
💸  Binance Pay  —  {BINANCE_AMOUNT}
🪙  USDT  —  {USDT_AMOUNT}
₿  Bitcoin  —  {BTC_AMOUNT}

{DIVIDER}
<b>🕒 ACTIVE HOURS</b>

🇮🇳 India  :  05:00 PM – 10:00 PM
🇬🇧 UK     :  12:30 PM – 05:30 PM
🇺🇸 USA   :  07:30 AM – 12:30 PM
🇦🇪 Gulf   :  03:30 PM – 08:30 PM

⏳ <b>Payment verification may take 1–6 hours during active hours.</b>
"""

async def start(update, context):
    context.user_data.clear()
    await update.message.reply_text(START_TEXT, parse_mode="HTML", reply_markup=main_menu_keyboard())

async def buy(update, context):
    q = update.callback_query
    text = f"""<b>💎 VIP LIFETIME ACCESS</b>

Get lifetime access to the complete VIP collection — once, forever.

{DIVIDER}
<b>💰 PAYMENT OPTIONS</b>

🇮🇳  UPI  —  {UPI_AMOUNT}
💸  Binance Pay  —  {BINANCE_AMOUNT}
🪙  USDT  —  {USDT_AMOUNT}
₿  Bitcoin  —  {BTC_AMOUNT}

{DIVIDER}
<b>✨ WHAT'S INCLUDED</b>

📚 Courses
📦 Resources
🎬 Files &amp; Videos
💬 Private communities
"""
    if q:
        await q.answer()
        await q.edit_message_text(text, parse_mode="HTML", reply_markup=payment_methods_keyboard())
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=payment_methods_keyboard())

async def catalogue_command(update, context):
    await catalogue(update, context)

async def reviews_command(update, context):
    await update.message.reply_text("⭐ <b>Reviews</b>", parse_mode="HTML", reply_markup=InlineKeyboardMarkup(
        [[InlineKeyboardButton("⭐  VIEW REVIEWS", url=REVIEWS_URL)]]))

async def contact_command(update, context):
    await update.message.reply_text(
        "📩 <b>Payment Support</b>\n\n"
        "Need help with a payment or transaction?.\n\n"
        "<i>Support is limited to payment-related issues.</i>\n\n"
        "<i>No DMs for courses or other matters. Violations may result in a ban.</i>",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("📩  CONTACT SUPPORT", url=SUPPORT_URL)]]
        )
    )

async def cancel(update, context):
    context.user_data.clear()
    await update.message.reply_text("❌ <b>Payment process cancelled.</b>\n\nUse /start to begin again.",
                                    parse_mode="HTML", reply_markup=main_menu_keyboard())

async def pay_upi(update, context):
    q = update.callback_query; await q.answer()
    context.user_data["payment_method"] = "UPI"
    caption = f"""<b>🇮🇳 UPI PAYMENT</b>

💰 Amount: <b>{UPI_AMOUNT}</b>

{DIVIDER}

📷 Scan the QR code above

        <u>OR</u>

🆔 UPI ID:
<code>{UPI_ID}</code>

{DIVIDER}

✅ After completing the payment, tap <b>I'VE PAID</b> below.
"""
    if os.path.exists(UPI_QR_PATH):
        with open(UPI_QR_PATH, "rb") as photo:
            await q.message.reply_photo(photo=photo, caption=caption,
                                         parse_mode="HTML", reply_markup=paid_keyboard())
    else:
        await q.message.reply_text(caption, parse_mode="HTML", reply_markup=paid_keyboard())

async def pay_binance(update, context):
    q = update.callback_query; await q.answer()
    context.user_data["payment_method"] = "Binance"
    text = f"""<b>💸 BINANCE PAYMENT</b>

💰 Amount: <b>{BINANCE_AMOUNT}</b>

{DIVIDER}

📤 Send <b>{BINANCE_AMOUNT}</b> to Binance ID:

<code>{BINANCE_ID}</code>

{DIVIDER}

✅ After completing the payment, tap <b>I'VE PAID</b> below.
"""
    await q.message.reply_text(text, parse_mode="HTML", reply_markup=paid_keyboard())

async def pay_usdt(update, context):
    q = update.callback_query; await q.answer()
    context.user_data["payment_method"] = "USDT"
    caption = f"""<b>🪙 USDT PAYMENT</b>

💰 Amount: <b>{USDT_AMOUNT}</b>
🌐 Network: <b>{USDT_NETWORK}</b>

{DIVIDER}

📤 USDT Address:

<code>{USDT_ADDRESS}</code>

{DIVIDER}

⚠️ Send only through the TRON (TRC20) network.

✅ After completing the payment, tap <b>I'VE PAID</b> below.
"""
    if os.path.exists(USDT_QR_PATH):
        with open(USDT_QR_PATH, "rb") as photo:
            await q.message.reply_photo(photo=photo, caption=caption,
                                         parse_mode="HTML", reply_markup=paid_keyboard())
    else:
        await q.message.reply_text(caption, parse_mode="HTML", reply_markup=paid_keyboard())

async def pay_btc(update, context):
    q = update.callback_query
    await q.answer()
    context.user_data["payment_method"] = "BTC"

    caption = f"""<b>₿ BTC PAYMENT</b>

💰 Amount: <b>{BTC_AMOUNT}</b>

{DIVIDER}

📤 BTC Address:

<code>{BTC_ADDRESS}</code>

{DIVIDER}

⚠️ Send only Bitcoin (BTC) to this address.

✅ After completing the payment, tap <b>I'VE PAID</b> below.
"""
    if os.path.exists(BTC_QR_PATH):
        with open(BTC_QR_PATH, "rb") as photo:
            await q.message.reply_photo(
                photo=photo,
                caption=caption,
                parse_mode="HTML",
                reply_markup=paid_keyboard()
            )
    else:
        await q.message.reply_text(
            caption,
            parse_mode="HTML",
            reply_markup=paid_keyboard()
        )


async def paid_button(update, context):
    q = update.callback_query; await q.answer()
    method = context.user_data.get("payment_method")
    if method not in ["UPI", "Binance", "USDT", "BTC"]:
        await q.message.reply_text("❌ <b>Payment session expired.</b>\n\nPlease go back and select a payment method again.",
                                    parse_mode="HTML")
        return
    u = q.from_user
    payment_id = create_payment(u.id, u.username, u.first_name, "Lifetime",
                                {"UPI": UPI_AMOUNT, "Binance": BINANCE_AMOUNT, "USDT": USDT_AMOUNT, "BTC": BTC_AMOUNT}[method],
                                method)
    context.user_data["payment_id"] = payment_id
    context.user_data["awaiting_proof"] = True
    try:
        await q.message.edit_reply_markup(reply_markup=None)
    except Exception as e:
        logger.warning("Could not remove payment buttons: %s", e)
    await q.message.reply_text(f"""<b>📸 PAYMENT PROOF</b>

Please send a clear screenshot of your payment.

Make sure it clearly shows:
   •  Amount
   •  Payment status
   •  Relevant payment details

⚠️ <i>Manual verification in progress</i>

📸 Send your screenshot below, or /cancel to stop.
""", parse_mode="HTML")

async def receive_payment_proof(update, context):
    if not context.user_data.get("awaiting_proof"):
        return
    payment_id = context.user_data.get("payment_id")
    if not payment_id:
        await update.message.reply_text("❌ <b>Payment session expired.</b>\n\nPlease start again with /start.",
                                        parse_mode="HTML")
        context.user_data.clear(); return
    payment = get_payment(payment_id)
    if not payment:
        await update.message.reply_text("❌ Payment record not found."); return
    if payment[8] not in ["awaiting_proof", "pending"]:
        await update.message.reply_text("This payment has already been processed.")
        context.user_data.clear(); return

    # BUGFIX: track whether the proof came in as a compressed Photo or as a
    # Document (file). Telegram's sendPhoto rejects a document-type file_id,
    # which was silently breaking the admin notification whenever a user
    # uploaded their screenshot as a "file" instead of a photo.
    is_document = False
    if update.message.photo:
        file_id = update.message.photo[-1].file_id
    elif update.message.document and update.message.document.mime_type and update.message.document.mime_type.startswith("image/"):
        file_id = update.message.document.file_id
        is_document = True
    else:
        await update.message.reply_text("📸 Please send the payment screenshot as an image/photo.")
        return

    save_screenshot(payment_id, file_id)
    update_payment_status(payment_id, "proof_submitted")
    context.user_data["awaiting_proof"] = False
    await update.message.reply_text(f"""<b>✅ PAYMENT PROOF RECEIVED</b>

Your payment screenshot has been submitted for manual verification.

⏳ Verification may take <b>1–6 hours</b> during active hours.

🎉 You'll receive your VIP access automatically after approval.
""", parse_mode="HTML")

    u = update.effective_user
    safe_name = html_lib.escape(u.first_name or "")
    safe_username = html_lib.escape(f"@{u.username}") if u.username else "No username"
    admin_text = f"""<b>💰 NEW PAYMENT PROOF</b>

🆔 Payment ID: <b>#{payment_id}</b>

{DIVIDER}
<b>👤 BUYER DETAILS</b>
{DIVIDER}

Name        :  {safe_name}
Telegram ID :  <code>{u.id}</code>
Username    :  {safe_username}

{DIVIDER}
<b>💳 PAYMENT DETAILS</b>
{DIVIDER}

Method  :  {payment[6]}
Amount  :  {payment[5]}
Plan    :  {payment[4]}

{DIVIDER}

👉 Please verify the payment.
"""
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅  APPROVE", callback_data=f"approve:{payment_id}"),
        InlineKeyboardButton("❌  REJECT", callback_data=f"reject:{payment_id}")
    ]])
    try:
        if is_document:
            # A document's file_id can't be sent through send_photo.
            await context.bot.send_document(chat_id=ADMIN_ID, document=file_id, caption=admin_text,
                                             parse_mode="HTML", reply_markup=kb)
        else:
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=file_id, caption=admin_text,
                                          parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        logger.exception("Failed to send payment proof to admin: %s", e)
        # Fallback: at minimum, get a text alert to the admin so the
        # payment doesn't go unnoticed even if the media itself failed.
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=admin_text + f"\n⚠️ Could not attach the screenshot automatically. "
                                   f"Check payment #{payment_id} in the database.",
                parse_mode="HTML", reply_markup=kb
            )
        except Exception as e2:
            logger.exception("Fallback admin text notification also failed: %s", e2)

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
    buttons = [[InlineKeyboardButton("📚  ACCESS COURSES", url=PUBLIC_COURSES_URL)]]
    for name, link in links:
        buttons.append([InlineKeyboardButton(f"🔐  JOIN {name.upper()}", url=link)])
    await context.bot.send_message(
        chat_id=user_id,
        text=f"""<b>🎉 Congratulations on Your VIP Purchase!</b>

Your payment has been successfully verified. ✅

{DIVIDER}
<b>📚 MATERIALS:</b>

🎓 VIP Courses
📦 VIP Resources

{DIVIDER}
<b>🎬 MEDIA:</b>

📁 VIP Files
🎥 VIP Videos

{DIVIDER}
<b>💬 COMMUNITIES:</b>

💰 Money Talks
📈 Growth Talks

{DIVIDER}

🔐 <i>All links are personal and one-time use.</i>
""",
        parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def approve_payment(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer("❌ You are not authorized.", show_alert=True); return
    try: payment_id = int(q.data.split(":")[1])
    except Exception:
        await q.answer(); return
    payment = get_payment(payment_id)
    if not payment:
        await q.answer(); await q.message.reply_text("❌ Payment not found."); return
    # A callback_query can only be answered once — check terminal states
    # before the generic answer() to avoid a second (failing) call.
    if payment[8] == "approved":
        await q.answer("Already approved.", show_alert=True); return
    if payment[8] == "rejected":
        await q.answer("This payment was already rejected.", show_alert=True); return
    await q.answer()
    try:
        await send_vip_access(context, payment[1], payment_id)
        update_payment_status(payment_id, "approved")
        approved_text = f"<b>✅ PAYMENT APPROVED</b>\n\n🆔 Payment ID: <b>#{payment_id}</b>\n👤 User ID: <code>{payment[1]}</code>"
        try:
            await q.edit_message_caption(caption=approved_text, parse_mode="HTML", reply_markup=None)
        except Exception:
            try:
                await q.edit_message_text(text=approved_text, parse_mode="HTML", reply_markup=None)
            except Exception: pass
    except Exception as e:
        logger.exception("Approval failed: %s", e)
        await q.message.reply_text("❌ Approval failed.\n\nMake sure the bot is an administrator in all VIP groups/channels and can manage invite links.")

async def reject_payment(update, context):
    q = update.callback_query
    if q.from_user.id != ADMIN_ID:
        await q.answer("❌ You are not authorized.", show_alert=True); return
    try: payment_id = int(q.data.split(":")[1])
    except Exception:
        await q.answer(); return
    payment = get_payment(payment_id)
    if not payment:
        await q.answer(); return
    # Same double-answer fix as approve_payment.
    if payment[8] in ["approved", "rejected"]:
        await q.answer("Payment already processed.", show_alert=True); return
    await q.answer()
    update_payment_status(payment_id, "rejected")
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("📩  CONTACT SUPPORT", url=SUPPORT_URL)]])
    try:
        await context.bot.send_message(chat_id=payment[1],
            text="""<b>❌ PAYMENT NOT VERIFIED</b>

Unfortunately, we couldn't verify your payment.

If you believe this is a mistake, please contact support.""",
            parse_mode="HTML", reply_markup=kb)
    except Exception as e:
        logger.warning("Could not notify rejected user: %s", e)
    rejected_text = f"<b>❌ PAYMENT REJECTED</b>\n\n🆔 Payment ID: <b>#{payment_id}</b>\n👤 User ID: <code>{payment[1]}</code>"
    try:
        await q.edit_message_caption(caption=rejected_text, parse_mode="HTML", reply_markup=None)
    except Exception:
        try:
            await q.edit_message_text(text=rejected_text, parse_mode="HTML", reply_markup=None)
        except Exception: pass

CATALOGUE = {
    "AI": [("AI Automations","https://t.me/VIP_Coursesss/774"),("AI Content Creation","https://t.me/VIP_Coursesss/1129")],
    "Business": [("Real Estate","https://t.me/VIP_Coursesss/18"),("Personal Brand","https://t.me/VIP_Coursesss/293"),("Agency","https://t.me/VIP_Coursesss/501"),("Freelancing","https://t.me/VIP_Coursesss/30"),("Coaching","https://t.me/VIP_Coursesss/50"),("Business","https://t.me/VIP_Coursesss/931")],
    "Sales & Marketing": [("Sales & Leads","https://t.me/VIP_Coursesss/522"),("Ads","https://t.me/VIP_Coursesss/955"),("Copywriting","https://t.me/VIP_Coursesss/1074"),("Affiliate Marketing","https://t.me/VIP_Coursesss/645"),("Email Marketing","https://t.me/VIP_Coursesss/753")],
    "Ecommerce": [("Drop-servicing","https://t.me/VIP_Coursesss/3"),("Digital Products","https://t.me/VIP_Coursesss/722"),("E-Com","https://t.me/VIP_Coursesss/894")],
    "Social Media": [("Instagram","https://t.me/VIP_Coursesss/310"),("YouTube","https://t.me/VIP_Coursesss/1045"),("TikTok","https://t.me/VIP_Coursesss/194"),("Twitter","https://t.me/VIP_Coursesss/13"),("Threads","https://t.me/VIP_Coursesss/10"),("Facebook","https://t.me/VIP_Coursesss/23"),("LinkedIn","https://t.me/VIP_Coursesss/77"),("Pinterest","https://t.me/VIP_Coursesss/115")],
    "Content": [("Content Creation","https://t.me/VIP_Coursesss/697"),("Video Editing","https://t.me/VIP_Coursesss/345"),("Graphic Design","https://t.me/VIP_Coursesss/278"),("Filmmaking","https://t.me/VIP_Coursesss/39"),("Animation","https://t.me/VIP_Coursesss/127")],
    "Web & Tech": [("UI/UX","https://t.me/VIP_Coursesss/674"),("SEO","https://t.me/VIP_Coursesss/595")],
    "Personal Development": [("Self Improvement","https://t.me/VIP_Coursesss/450"),("Fitness","https://t.me/VIP_Coursesss/401"),("Self Defence","https://t.me/VIP_Coursesss/161"),("Memory","https://t.me/VIP_Coursesss/221"),("Communication","https://t.me/VIP_Coursesss/90"),("NLP & Hypnosis","https://t.me/VIP_Coursesss/1004"),("Psychology","https://t.me/VIP_Coursesss/628")],
    "Luxury": [("History Courses","https://t.me/VIP_Coursesss/392"),("Peterson Academy","https://t.me/VIP_Coursesss/1327"),("Andrew Tate — TRW","https://t.me/VIP_Coursesss/1238"),("Iman Gadzhi — Educate IO","https://t.me/VIP_Coursesss/1199"),("Luke Belmar — Capital Club","https://t.me/VIP_Coursesss/1288")],
}

async def catalogue(update, context):
    # Handles being called both from a button press (callback_query) and
    # directly from the /catalogue command (no callback_query).
    q = update.callback_query
    buttons = [[InlineKeyboardButton(f"📂  {cat}", callback_data=f"cat:{cat}")] for cat in CATALOGUE]
    buttons.append([InlineKeyboardButton("⬅️  BACK", callback_data="back_start")])
    text = """<b>📚 VIP COURSES</b>

Our VIP courses are organized across <b>40+ sub-topics</b>.

👇 Choose a category below:
"""
    if q:
        await q.answer()
        await q.edit_message_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await update.message.reply_text(text, parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def catalogue_category(update, context):
    q = update.callback_query; await q.answer()
    category = q.data.split(":",1)[1]
    buttons = [[InlineKeyboardButton(f"📘  {name}", url=url)] for name,url in CATALOGUE.get(category,[])]
    buttons.append([InlineKeyboardButton("⬅️  CATALOGUE", callback_data="catalogue")])
    await q.edit_message_text(f"<b>📚 {html_lib.escape(category.upper())}</b>\n\n👇 Select a sub-topic:",
                              parse_mode="HTML", reply_markup=InlineKeyboardMarkup(buttons))

async def back_start(update, context):
    q = update.callback_query; await q.answer()
    context.user_data.clear()
    await q.edit_message_text(START_TEXT, parse_mode="HTML", reply_markup=main_menu_keyboard())

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
    app.add_handler(CallbackQueryHandler(pay_btc, pattern=r"^pay_btc$"))
    app.add_handler(CallbackQueryHandler(paid_button, pattern=r"^paid$"))
    app.add_handler(CallbackQueryHandler(approve_payment, pattern=r"^approve:"))
    app.add_handler(CallbackQueryHandler(reject_payment, pattern=r"^reject:"))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.IMAGE, receive_payment_proof))
    app.add_error_handler(error_handler)

    print("🚀 VIP Payment Bot started!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
