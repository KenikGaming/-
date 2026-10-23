import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import json
import os
import random
import time
import sys
import string
import requests
import math
from datetime import datetime

# ================= CẤU HÌNH =================
BOT_TOKEN = "8845671808:AAGwuhyrZ5ygb7PSwnZ8qP3z10eIjz_5IRA"
ADMIN_ID = 6450901392

banner_id = "AgACAgUAAxkBAAEjxv5q2h5_nj9CJtoRFPZGTgbFaQoMWgAC3RRrG5tA0VaC4wLU4Th8vAEAAwIAA3MAAz0E" 
qr_id = "AgACAgUAAxkBAAEjxwABatoe5xhgMCEpswpx4tr9rXFAD7wAAvkSaxvUpdBWJJgNGFeVAAFGAQADAgADeAADPQQ"

BANK_INFO = {"bank": "SACOMBANK", "stk": "040097074021", "name": "TRUONG THI TRANG"}
BANKS = ["Vietcombank", "Agribank", "VietinBank", "BIDV", "ACB", "Techcombank", "VPBank", "OCB", "LienVietPostBank", "SHB", "TPBank", "SeABank", "MSB", "VIB", "NCB", "PGBank", "SCB", "Eximbank", "ABBank", "VietABank", "HDBank", "Sacombank", "Bac A Bank", "GPBank"]

bot = telebot.TeleBot(BOT_TOKEN)
DB_FILE = "mmo_data.json"

# ================= DATABASE =================
def load_db():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                db = json.load(f)
                for k in ["deposits", "tiktok_checks", "users", "orders", "withdraws", "history", "flash_sale", "inventory", "quests", "mails"]:
                    if k not in db: 
                        db[k] = [] if k in ["deposits", "orders", "withdraws", "flash_sale"] else {}
                return db
        except: pass
    return {"users": {}, "orders": [], "giftcodes": {"KYO100K": 100000}, "deposits": [], "tiktok_checks": {}, "withdraws": [], "history": {}, "flash_sale": [], "inventory": {}, "quests": {}, "mails": {}}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def get_user(user_id, name="Unknown"):
    db = load_db()
    uid = str(user_id)
    if uid not in db["users"]: db["users"][uid] = {}
    
    default_data = {
        "name": name, "balance": 5000, "points": 0, "exp": 0, "level": 1,
        "total_deposit": 0, "vip_level": 0, "rank": "Thường", "loan": 0, "loan_date": "",
        "has_util_access": False, "theme": "dark", "lang": "vi"
    }
    changed = False
    for key, val in default_data.items():
        if key not in db["users"][uid]:
            db["users"][uid][key] = val
            changed = True
    if uid not in db["quests"]:
        db["quests"][uid] = {"buy": 0, "transfer": 0}
        changed = True
    if changed: save_db(db)
    return db["users"][uid]

def update_user(user_id, key, value):
    db = load_db()
    uid = str(user_id)
    if uid in db["users"]:
        db["users"][uid][key] = value
        save_db(db)

def add_history(user_id, action, amount, note=""):
    db = load_db()
    uid = str(user_id)
    if uid not in db["history"]: db["history"][uid] = []
    db["history"][uid].append({"time": datetime.now().strftime("%H:%M %d/%m"), "action": action, "amount": amount, "note": note})
    db["history"][uid] = db["history"][uid][-20:]
    save_db(db)

def format_money(amount): return f"{amount:,}đ".replace(",", ".")

def safe_edit(call, text, markup=None):
    try:
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        if "message is not modified" not in str(e):
            try: bot.delete_message(call.message.chat.id, call.message.message_id)
            except: pass
            bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=markup)

# ================= MENU =================
def main_menu_kb():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🛒 DỊCH VỤ MMO", callback_data="shop"),
        InlineKeyboardButton("🛠 TOOL HỖ TRỢ", callback_data="tools"),
        InlineKeyboardButton("💻 LỆNH BOT (50)", callback_data="bot_cmds_menu"),
        InlineKeyboardButton("👛 VÍ & GIAO DỊCH", callback_data="wallet"),
        InlineKeyboardButton("🎒 TÚI ĐỒ", callback_data="inventory"),
        InlineKeyboardButton("📜 NHIỆM VỤ", callback_data="quests"),
        InlineKeyboardButton("🎮 MINIGAME", callback_data="games"),
        InlineKeyboardButton("💎 TÀI KHOẢN", callback_data="profile"),
        InlineKeyboardButton("🏆 BXH THÁNG", callback_data="top_month"),
        InlineKeyboardButton("🔍 CHECK ID", callback_data="check_id")
    )
    return markup

def tools_kb():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📧 Tạo Mail Ảo (Temp Mail)", callback_data="tool_mail"),
        InlineKeyboardButton("🔗 Rút Gọn Link", callback_data="tool_shortlink"),
        InlineKeyboardButton("🔑 Random Password", callback_data="tool_pass"),
        InlineKeyboardButton("📱 Check SĐT / SMS (Demo)", callback_data="tool_sms"),
        InlineKeyboardButton("🔙 Quay lại", callback_data="back_home")
    )
    return markup

def wallet_kb():
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📥 Nạp Tiền (QR)", callback_data="deposit_qr"),
        InlineKeyboardButton("📤 Rút Tiền (Bank)", callback_data="withdraw_start"),
        InlineKeyboardButton("🎁 Chuyển Quà Tặng", callback_data="gift"),
        InlineKeyboardButton("📜 Lịch Sử Giao Dịch", callback_data="history"),
        InlineKeyboardButton("🔙 Quay lại", callback_data="back_home")
    )
    return markup

def games_kb():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🎰 Tài Xỉu", callback_data="taixiu"),
        InlineKeyboardButton("🎡 Vòng Quay", callback_data="spin"),
        InlineKeyboardButton("📦 Rương Báu", callback_data="lootbox"),
        InlineKeyboardButton("💸 Vay Vốn", callback_data="loan")
    )
    markup.add(InlineKeyboardButton("🔙 Quay lại", callback_data="back_home"))
    return markup

def bot_cmds_menu_kb():
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("🖥 Hệ Thống", callback_data="cmd_cat_sys"),
        InlineKeyboardButton("🛠 Tiện Ích", callback_data="cmd_cat_util"),
        InlineKeyboardButton("🎮 Giải Trí", callback_data="cmd_cat_fun"),
        InlineKeyboardButton("📊 MMO", callback_data="cmd_cat_mmo"),
        InlineKeyboardButton("👑 Admin", callback_data="cmd_cat_admin"),
        InlineKeyboardButton("🔙 Quay lại", callback_data="back_home")
    )
    return markup

def cat_kb(cat):
    markup = InlineKeyboardMarkup(row_width=2)
    if cat == "sys":
        markup.add(
            InlineKeyboardButton("1. Xem Ping", callback_data="cmd_ping"),
            InlineKeyboardButton("2. Xem Giờ", callback_data="cmd_time"),
            InlineKeyboardButton("3. Info Bot", callback_data="cmd_info"),
            InlineKeyboardButton("4. Uptime", callback_data="cmd_uptime"),
            InlineKeyboardButton("5. My ID", callback_data="cmd_myid")
        )
    elif cat == "util":
        markup.add(
            InlineKeyboardButton("6. Tính Toán", callback_data="cmd_calc"),
            InlineKeyboardButton("7. Dịch Thuật", callback_data="cmd_translate"),
            InlineKeyboardButton("8. Tỷ Giá", callback_data="cmd_exchange"),
            InlineKeyboardButton("9. Thời Tiết", callback_data="cmd_weather"),
            InlineKeyboardButton("10. QR Code", callback_data="cmd_qr")
        )
    elif cat == "fun":
        markup.add(
            InlineKeyboardButton("11. Tung Xúc Xắc", callback_data="cmd_dice"),
            InlineKeyboardButton("12. Lật Đồng Xu", callback_data="cmd_coin"),
            InlineKeyboardButton("13. Tỉ Lệ", callback_data="cmd_percent"),
            InlineKeyboardButton("14. Số Ngẫu Nhiên", callback_data="cmd_rand"),
            InlineKeyboardButton("15. Câu Nói", callback_data="cmd_quote")
        )
    elif cat == "mmo":
        markup.add(
            InlineKeyboardButton("16. Lấy User Agent", callback_data="cmd_ua"),
            InlineKeyboardButton("17. Fake IP", callback_data="cmd_fakeip"),
            InlineKeyboardButton("18. Check Pass", callback_data="cmd_checkpass"),
            InlineKeyboardButton("19. Rút Gọn JSON", callback_data="cmd_json"),
            InlineKeyboardButton("20. Text -> Base64", callback_data="cmd_b64")
        )
    elif cat == "admin":
        markup.add(
            InlineKeyboardButton("21. Xem DB", callback_data="cmd_db"),
            InlineKeyboardButton("22. Backup", callback_data="cmd_backup"),
            InlineKeyboardButton("23. Check User", callback_data="cmd_chkuser"),
            InlineKeyboardButton("24. Total Users", callback_data="cmd_totuser"),
            InlineKeyboardButton("25. Reset Bot", callback_data="cmd_reset")
        )
    markup.add(InlineKeyboardButton("🔙 Quay lại", callback_data="bot_cmds_menu"))
    return markup

# ================= DATA =================
PRODUCTS = {
    "web_design": {"cat": "MMO_AI", "name": "THIẾT KẾ WEBSITE", "price": 500000, "icon": "🌐"},
    "tiktok_channel": {"cat": "MMO_AI", "name": "KÊNH TIKTOK", "price": 200000, "icon": "🎵"},
    "ai_code": {"cat": "MMO_AI", "name": "AI CODE MỌI THỨ", "price": 100000, "icon": "🟢"},
    "via_chat": {"cat": "MMO_AI", "name": "VIA CHAT SUPPORT", "price": 50000, "icon": "💬"},
    "fake_ip": {"cat": "MMO_AI", "name": "FAKE IP - VPN", "price": 30000, "icon": "🅿️"},
    "vps": {"cat": "MMO_AI", "name": "VPS", "price": 150000, "icon": "💻"},
    "rua_ip": {"cat": "MMO_AI", "name": "RÙA IP BÁN", "price": 500000, "icon": "🐢"},
    "claude": {"cat": "MMO_AI", "name": "CLAUDE", "price": 200000, "icon": "🟧"},
    "veo3": {"cat": "MMO_AI", "name": "VEO 3", "price": 100000, "icon": "🎬"},
    "via_co": {"cat": "SOCIAL", "name": "VIA CỔ 2010-2014", "price": 150000, "icon": "👨‍🦳"},
    "profile_usa": {"cat": "SOCIAL", "name": "PROFILE NAME USA CỔ", "price": 80000, "icon": "🎀"},
    "giay_to_tiktok": {"cat": "SOCIAL", "name": "GIẤY TỜ UP TÍCH XANH TIKTOK", "price": 400000, "icon": "🐉"},
    "tk_chat_tiktok": {"cat": "SOCIAL", "name": "TÀI KHOẢN CHAT SUPPORT TIKTOK", "price": 200000, "icon": "🎵"},
    "fb_service": {"cat": "SOCIAL", "name": "DỊCH VỤ FACEBOOK", "price": 50000, "icon": "📘"},
    "tt_service": {"cat": "SOCIAL", "name": "DỊCH VỤ TIKTOK", "price": 50000, "icon": "🎵"},
    "tut_fb": {"cat": "SOCIAL", "name": "TUT FACEBOOK", "price": 200000, "icon": "📘"},
    "tut_tiktok": {"cat": "SOCIAL", "name": "TUT TIKTOK", "price": 200000, "icon": "🎵"},
    "insta": {"cat": "SOCIAL", "name": "INSTAGRAM", "price": 100000, "icon": "📷"},
    "tele_service": {"cat": "SOCIAL", "name": "TELEGRAM", "price": 100000, "icon": "✈️"},
    "discord": {"cat": "SOCIAL", "name": "DISCORD", "price": 100000, "icon": "🎮"},
    "thue_sim": {"cat": "SOCIAL", "name": "THUÊ SIM", "price": 50000, "icon": "📱"},
    "zalo": {"cat": "SOCIAL", "name": "ZALO", "price": 50000, "icon": "💬"},
    "x_service": {"cat": "SOCIAL", "name": "X", "price": 100000, "icon": "✖️"},
    "tut_trick_8k": {"cat": "SOCIAL", "name": "TUT TRICK 8K", "price": 300000, "icon": "🥷"},
    "thue_maxcare": {"cat": "OTHER", "name": "THUÊ TOOL MAX CARE", "price": 200000, "icon": "✋"},
    "mua_maxcare": {"cat": "OTHER", "name": "BÁN TOOL MAX CARE", "price": 2000000, "icon": "🐷"},
    "vo_va": {"cat": "OTHER", "name": "VỞ VA VỞ VĂN", "price": 50000, "icon": "🐮"},
    "pr_brand": {"cat": "OTHER", "name": "BÁO PR THƯƠNG HIỆU & TÍCH XANH", "price": 1000000, "icon": "💰"},
    "tai_nguyen": {"cat": "OTHER", "name": "TÀI NGUYÊN MMO", "price": 50000, "icon": "🥷"},
}

# ================= START =================
@bot.message_handler(commands=['start', 'menu'])
def send_welcome(message):
    user = get_user(message.from_user.id, message.from_user.first_name)
    lvl = user.get('level', 1)
    
    # Cài đặt ngôn ngữ ảnh hưởng đến câu chào
    if user.get("lang", "vi") == "en":
        greeting = f"👋 Hello <b>{message.from_user.first_name}</b>"
        text_ba = "Balance"
    else:
        greeting = f"👋 Xin chào <b>{message.from_user.first_name}</b>"
        text_ba = "Số dư"

    caption = (
        f"🤖 <b>KYO SHOP SYSTEM</b>\n"
        f"────────────────────────────\n\n"
        f"{greeting} [Lv.{lvl}]\n"
        f"💵 {text_ba}: <b>{format_money(user.get('balance', 0))}</b>\n"
        f"💎 PTS: <b>{user.get('points', 0)}</b>\n\n"
        f"🕯 Chúc bạn mua sắm vui vẻ!"
    )
    try: bot.send_photo(message.chat.id, banner_id, caption=caption, parse_mode="HTML", reply_markup=main_menu_kb())
    except: bot.send_message(message.chat.id, caption, parse_mode="HTML", reply_markup=main_menu_kb())

def set_commands():
    bot.set_my_commands([
        BotCommand("start", "Khởi động lại Bot"),
        BotCommand("shop", "Mở danh mục sản phẩm"),
        BotCommand("naptien", "Nạp tiền"),
        BotCommand("admin", "Quản trị (Admin)")
    ])

# ================= CALLBACK HANDLER =================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user = get_user(call.from_user.id, call.from_user.first_name)
    uid = call.from_user.id
    is_admin = (uid == ADMIN_ID)
    
    # === LỆNH BOT ===
    if call.data == "bot_cmds_menu":
        if is_admin or user.get("has_util_access"):
            safe_edit(call, "💻 <b>DANH SÁCH 50 LỆNH BOT</b>\n\nChọn nhóm lệnh bạn muốn dùng:", bot_cmds_menu_kb())
        else:
            text = "🔒 <b>TÍNH NĂNG BỊ KHÓA</b>\n\nBạn cần mua quyền sử dụng Menu Lệnh Bot với giá <b>500,000đ</b> để mở khóa toàn bộ 50 lệnh tiện ích."
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton("💳 Mua Ngay (500K)", callback_data="buy_util_access")).add(InlineKeyboardButton("🔙 Quay lại", callback_data="back_home"))
            safe_edit(call, text, markup)
    elif call.data == "buy_util_access":
        if user.get("balance", 0) < 500000:
            return bot.answer_callback_query(call.id, "❌ Số dư không đủ 500,000đ!", show_alert=True)
        update_user(uid, "balance", user["balance"] - 500000)
        update_user(uid, "has_util_access", True)
        add_history(uid, "Mua quyền dùng Menu Lệnh Bot", -500000)
        bot.answer_callback_query(call.id, "✅ Mở khóa thành công! Vào Menu Lệnh Bot để dùng.", show_alert=True)
        safe_edit(call, "💻 <b>MENU LỆNH BOT</b>\n\nBạn đã mở khóa thành công!", bot_cmds_menu_kb())
    elif call.data.startswith("cmd_cat_"):
        cat = call.data.replace("cmd_cat_", "")
        safe_edit(call, f"💻 <b>LỆNH {cat.upper()}</b>\n\nChọn lệnh:", cat_kb(cat))
        
    # Xử lý 50 lệnh (Demo & Thật)
    elif call.data.startswith("cmd_"):
        cmd = call.data.replace("cmd_", "")
        try:
            if cmd == "ping": res = f"🏓 Pong! `{random.randint(10, 80)}ms`"
            elif cmd == "time": res = f"🕒 Giờ hiện tại: `{datetime.now().strftime('%H:%M:%S - %d/%m/%Y')}`"
            elif cmd == "info": res = "🤖 Đây là Bot KYO Shop, code bằng Python (pyTelegramBotAPI)."
            elif cmd == "uptime": res = "⏱ Bot đang chạy ổn định trên server."
            elif cmd == "myid": res = f"🆔 ID của bạn: `{uid}`"
            elif cmd == "calc":
                bot.send_message(call.message.chat.id, "🧮 Nhập phép tính (VD: 1+1):")
                return bot.register_next_step_handler(call.message, process_calc)
            elif cmd == "dice": res = f"🎲 Bạn đổ được: **{random.randint(1,6)}**"
            elif cmd == "coin": res = f"🪙 Kết quả: **{'Sấp' if random.choice([True, False]) else 'Ngửa'}**"
            elif cmd == "percent": res = f"📊 Tỷ lệ ngẫu nhiên: **{random.randint(1, 100)}%**"
            elif cmd == "rand": res = f"🔢 Số ngẫu nhiên: **{random.randint(1, 9999)}**"
            elif cmd == "quote": res = "💬 *Thất bại là mẹ thành công.*"
            elif cmd == "ua": res = "🖥 **Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36**"
            elif cmd == "fakeip": res = f"🌐 IP Fake đề xuất: `103.152.{random.randint(1,255)}.{random.randint(1,255)}`"
            elif cmd == "checkpass":
                bot.send_message(call.message.chat.id, "🔑 Nhập pass cần check độ mạnh:")
                return bot.register_next_step_handler(call.message, process_checkpass)
            elif cmd == "b64":
                bot.send_message(call.message.chat.id, "📝 Nhập text cần mã hóa Base64:")
                return bot.register_next_step_handler(call.message, process_b64)
            elif cmd == "qr":
                bot.send_message(call.message.chat.id, "📸 Nhập text để tạo QR (cần cài thư viện qrcode):\n(Hoặc tao đang chạy demo chữ)")
                res = "📸 Tính năng tạo QR cần cài thêm thư viện `qrcode[pil]` vào VPS của mày."
            elif cmd == "json": res = "`{\"status\": \"success\", \"msg\": \"Tính năng format JSON đang chạy demo\"}`"
            elif cmd == "db":
                if not is_admin: res = "❌ Chỉ Admin mới xem được Data."
                else: res = f"📁 Dung lượng file DB: `{os.path.getsize(DB_FILE) if os.path.exists(DB_FILE) else 0} bytes`"
            elif cmd == "backup":
                if not is_admin: res = "❌ Chỉ Admin mới backup được."
                else:
                    bot.send_document(ADMIN_ID, open(DB_FILE, "rb"), caption="File Backup Data")
                    res = "✅ Đã gửi file backup cho Admin."
            elif cmd == "chkuser":
                if not is_admin: res = "❌ Chỉ Admin."
                else:
                    bot.send_message(call.message.chat.id, "Nhập ID user cần check:")
                    return bot.register_next_step_handler(call.message, process_chkuser)
            elif cmd == "totuser": res = f"👥 Tổng số user: **{len(load_db()['users'])}**"
            elif cmd == "reset":
                if not is_admin: res = "❌ Chỉ Admin."
                else: res = "⚠️ Lệnh này nguy hiểm, tao chưa code nút xác nhận (Demo)."
            else: res = "⚠️ Lệnh này đang được bảo trì."
            safe_edit(call, res, InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="bot_cmds_menu")))
        except Exception as e:
            safe_edit(call, f"❌ Lỗi khi chạy lệnh: {e}", InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="bot_cmds_menu")))

    # === CÁC CHỨC NĂNG KHÁC ===
    elif call.data in ["shop", "menu"]:
        safe_edit(call, "🛒 <b>DANH MỤC DỊCH VỤ</b>\n\n👇 Chọn nhóm dịch vụ:", category_kb())
    elif call.data.startswith("cat_"):
        cat = call.data.replace("cat_", "")
        safe_edit(call, f"📦 <b>DANH SÁCH DỊCH VỤ</b>\n\nChọn mặt hàng bạn muốn mua:", products_kb(cat))
    elif call.data == "back_home":
        text = f"🤖 <b>KYO SHOP</b>\n\n👋 Chào <b>{call.from_user.first_name}</b>\n💵 Số dư: <b>{format_money(user.get('balance', 0))}</b>"
        safe_edit(call, text, main_menu_kb())
    elif call.data == "tools":
        safe_edit(call, "🛠 <b>CÔNG CỤ HỖ TRỢ</b>\n\nChọn tool bạn muốn dùng:", tools_kb())
    
    # TOOL
    elif call.data == "tool_mail":
        bot.send_message(call.message.chat.id, "📧 Đang tạo mail ảo, vui lòng đợi...")
        try:
            r = requests.get("https://api.mail.tm/domains").json()
            domain = r["hydra:member"][0]["domain"]
            email = f"kyo{random.randint(1000,9999)}@{domain}"
            pwd = f"pass{random.randint(10000,99999)}"
            requests.post("https://api.mail.tm/accounts", json={"address": email, "password": pwd})
            db = load_db()
            if str(uid) not in db["mails"]: db["mails"][str(uid)] = []
            db["mails"][str(uid)].append({"email": email, "pwd": pwd})
            save_db(db)
            text = f"✅ <b>MAIL ĐÃ TẠO</b>\n📧 Mail: <code>{email}</code>\n🔑 Pass: <code>{pwd}</code>"
            bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        except Exception as e: bot.send_message(call.message.chat.id, f"❌ Lỗi API tạo mail: {e}")
    elif call.data == "tool_shortlink":
        bot.send_message(call.message.chat.id, "🔗 Nhập link cần rút gọn:")
        bot.register_next_step_handler(call.message, process_shortlink)
    elif call.data == "tool_pass":
        pwd = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*", k=16))
        bot.send_message(call.message.chat.id, f"🔑 <b>Mật khẩu ngẫu nhiên:</b>\n<code>{pwd}</code>", parse_mode="HTML")
    elif call.data == "tool_sms":
        bot.send_message(call.message.chat.id, "📱 <b>Check SĐT / SMS</b>\n\nTính năng đang được cập nhật API.")

    # VÍ & NẠP RÚT
    elif call.data == "wallet":
        safe_edit(call, "👛 <b>QUẢN LÝ VÍ</b>\n\nChọn thao tác:", wallet_kb())
    elif call.data == "deposit_qr":
        text = f"🏧 <b>NẠP TIỀN (QR)</b>\n\n🏦 Bank: <b>{BANK_INFO['bank']}</b>\n💳 STK: <code>{BANK_INFO['stk']}</code>\n👤 Tên: <b>{BANK_INFO['name']}</b>\n📝 Nội dung: <code>NAP {uid}</code>\n\n<i>Quét QR, chuyển xong bấm Gửi Bill.</i>"
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("📤 Gửi Bill", callback_data="send_bill")).add(InlineKeyboardButton("🔙 Quay lại", callback_data="wallet"))
        try: bot.delete_message(call.message.chat.id, call.message.message_id)
        except: pass
        try: bot.send_photo(call.message.chat.id, qr_id, caption=text, parse_mode="HTML", reply_markup=markup)
        except: bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=markup)
    elif call.data == "send_bill":
        bot.send_message(call.message.chat.id, "📸 Gửi ảnh bill chuyển khoản (kèm caption số tiền):")
        bot.register_next_step_handler(call.message, process_bill)
    elif call.data == "withdraw_start":
        safe_edit(call, "🏦 <b>CHỌN NGÂN HÀNG</b>", bank_kb())
    elif call.data.startswith("bank_"):
        bank_name = call.data.replace("bank_", "")
        bot.send_message(call.message.chat.id, f"🏦 Rút về <b>{bank_name}</b>.\n\nNhập: <code>[Số Tài Khoản] [Số Tiền]</code>", parse_mode="HTML")
        bot.register_next_step_handler(call.message, process_withdraw, bank_name)
    elif call.data == "gift":
        bot.send_message(call.message.chat.id, "🎁 Nhập: <code>[ID] [Số Tiền] [Lời Nhắn]</code>", parse_mode="HTML")
        bot.register_next_step_handler(call.message, process_gift)
    elif call.data == "history":
        db = load_db()
        hist = db.get("history", {}).get(str(uid), [])
        text = "📜 <b>BIẾN ĐỘNG SỐ DƯ</b>\n────────────────────────────\n"
        if not hist: text += "<i>Chưa có giao dịch.</i>"
        for h in reversed(hist[-10:]):
            sign = "+" if h["amount"] > 0 else ""
            text += f"• {h['time']} | {h['action']}: <b>{sign}{format_money(h['amount'])}</b>\n"
        safe_edit(call, text, InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="wallet")))

    # PROFILE & SETTINGS
    elif call.data == "profile":
        total_orders = len([o for o in load_db()["orders"] if o["user_id"] == uid])
        text = f"💎 <b>HỒ SƠ</b> 💎\n────────────────────────────\n🆔 ID: <code>{uid}</code>\n👋 Tên: <b>{call.from_user.first_name}</b>\n💵 Số dư: <b>{format_money(user.get('balance', 0))}</b>\n💎 Điểm: <b>{user.get('points', 0)} PTS</b>\n🔥 Lv: <b>{user.get('level', 1)}</b>\n🛡 VIP: <b>{user.get('vip_level', 0)}</b>\n📦 Đơn: <b>{total_orders}</b>\n\n⚙️ <b>Cài đặt:</b>"
        markup = InlineKeyboardMarkup(row_width=2).add(
            InlineKeyboardButton("🌗 Giao diện", callback_data="setting_theme"),
            InlineKeyboardButton("🌐 Ngôn ngữ", callback_data="setting_lang")
        ).add(InlineKeyboardButton("🔙 Quay lại", callback_data="back_home"))
        safe_edit(call, text, markup)
    elif call.data == "setting_theme":
        safe_edit(call, f"🌗 <b>GIAO DIỆN</b>\n\nHiện tại: <b>{user.get('theme', 'dark').capitalize()}</b>\n\nBấm để đổi:", InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("☀️ Sáng", callback_data="set_theme_light"), InlineKeyboardButton("🌙 Tối", callback_data="set_theme_dark")).add(InlineKeyboardButton("🔙 Quay lại", callback_data="profile")))
    elif call.data.startswith("set_theme_"):
        theme = call.data.replace("set_theme_", "")
        update_user(uid, "theme", theme)
        bot.answer_callback_query(call.id, f"✅ Đã đổi giao diện sang {theme.capitalize()}", show_alert=True)
        safe_edit(call, f"🌗 Đã đổi giao diện sang {theme.capitalize()}.", InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="profile")))
    elif call.data == "setting_lang":
        safe_edit(call, f"🌐 <b>NGÔN NGỮ</b>\n\nHiện tại: <b>{user.get('lang', 'vi').upper()}</b>\n\nBấm để đổi:", InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("🇻🇳 Tiếng Việt", callback_data="set_lang_vi"), InlineKeyboardButton("🇺🇸 English", callback_data="set_lang_en")).add(InlineKeyboardButton("🔙 Quay lại", callback_data="profile")))
    elif call.data.startswith("set_lang_"):
        lang = call.data.replace("set_lang_", "")
        update_user(uid, "lang", lang)
        bot.answer_callback_query(call.id, f"✅ Đã đổi ngôn ngữ sang {lang.upper()}", show_alert=True)
        safe_edit(call, "🌐 Đã đổi ngôn ngữ thành công. Bấm /start để thấy sự thay đổi!", InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="profile")))

    # CÁC MỤC KHÁC (Túi đồ, Nhiệm vụ, Games, BXH)
    elif call.data == "inventory":
        db = load_db()
        inv = db.get("inventory", {}).get(str(uid), [])
        text = "🎒 <b>TÚI ĐỒ</b>\n────────────────────────────\n"
        if not inv: text += "<i>Túi đồ trống.</i>"
        else:
            for i, item in enumerate(inv[-10:], 1):
                text += f"{i}. <b>{item['item']}</b>\n└ Key: <code>{item['key']}</code> ({item['time']})\n"
        safe_edit(call, text, InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="back_home")))
    elif call.data == "quests":
        db = load_db()
        q = db.get("quests", {}).get(str(uid), {"buy": 0, "transfer": 0})
        text = f"📜 <b>NHIỆM VỤ NGÀY</b>\n────────────────────────────\n🛒 Mua hàng: <b>{q.get('buy', 0)}/3</b>\n💸 Chuyển tiền: <b>{q.get('transfer', 0)}/1</b>"
        markup = InlineKeyboardMarkup(row_width=1)
        if q.get("buy", 0) >= 3: markup.add(InlineKeyboardButton("🎁 Nhận Mua Hàng", callback_data="claim_buy"))
        if q.get("transfer", 0) >= 1: markup.add(InlineKeyboardButton("🎁 Nhận Chuyển Tiền", callback_data="claim_trans"))
        markup.add(InlineKeyboardButton("🔙 Quay lại", callback_data="back_home"))
        safe_edit(call, text, markup)
    elif call.data.startswith("claim_"):
        claim_type = call.data.replace("claim_", "")
        db = load_db()
        q = db.get("quests", {}).get(str(uid), {})
        if claim_type == "buy" and q.get("buy", 0) >= 3:
            db["users"][str(uid)]["balance"] += 10000
            db["users"][str(uid)]["points"] += 50
            q["buy"] = 0
            save_db(db)
            bot.answer_callback_query(call.id, "✅ Nhận 10k + 50 PTS!", show_alert=True)
        elif claim_type == "trans" and q.get("transfer", 0) >= 1:
            db["users"][str(uid)]["balance"] += 5000
            db["users"][str(uid)]["points"] += 20
            q["transfer"] = 0
            save_db(db)
            bot.answer_callback_query(call.id, "✅ Nhận 5k + 20 PTS!", show_alert=True)
        safe_edit(call, "📜 <b>NHIỆM VỤ</b>\n\nChọn lại nhiệm vụ để xem!", InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="quests")))
    elif call.data == "games":
        safe_edit(call, "🎮 <b>MINI GAME</b>\n\nChọn trò chơi:", games_kb())
    elif call.data == "taixiu":
        text = f"🎰 <b>TÀI XỈU</b>\n────────────────────────────\n💵 Số dư: <b>{format_money(user.get('balance', 0))}</b>\nChọn cửa:"
        markup = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("TÀI", callback_data="tx_tai"), InlineKeyboardButton("XỈU", callback_data="tx_xiu")).add(InlineKeyboardButton("🔙 Quay lại", callback_data="games"))
        safe_edit(call, text, markup)
    elif call.data in ["tx_tai", "tx_xiu"]:
        choice = "TÀI" if call.data == "tx_tai" else "XỈU"
        bot.send_message(call.message.chat.id, f"Chọn <b>{choice}</b>. Nhập số tiền cược:")
        bot.register_next_step_handler(call.message, process_taixiu, choice)
    elif call.data == "spin":
        text = f"🎡 <b>VÒNG QUAY</b>\n────────────────────────────\n💵 Số dư: <b>{format_money(user.get('balance', 0))}</b>\n20,000đ/lượt. Trúng tới 500K!"
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🎰 QUAY (20K)", callback_data="do_spin")).add(InlineKeyboardButton("🔙 Quay lại", callback_data="games"))
        safe_edit(call, text, markup)
    elif call.data == "do_spin":
        if user.get("balance", 0) < 20000: return bot.answer_callback_query(call.id, "❌ Cần ít nhất 20,000đ!", show_alert=True)
        update_user(uid, "balance", user["balance"] - 20000)
        add_history(uid, "Vòng quay", -20000)
        prizes = [0, 10000, 20000, 50000, 100000, 500000]
        weights = [50, 20, 15, 10, 4, 1] 
        win_amount = random.choices(prizes, weights=weights, k=1)[0]
        if win_amount > 0: 
            update_user(uid, "balance", user["balance"] - 20000 + win_amount)
            add_history(uid, "Trúng vòng quay", win_amount)
            result = f"🎉 Trúng <b>{format_money(win_amount)}</b>!"
        else: result = "😢 Trượt rồi!"
        safe_edit(call, f"🎡 <b>KẾT QUẢ</b>\n\n{result}\n💵 Số dư mới: <b>{format_money(user['balance'] - 20000 + win_amount)}</b>", InlineKeyboardMarkup().add(InlineKeyboardButton("🎰 Quay tiếp", callback_data="spin")).add(InlineKeyboardButton("🔙 Về Menu", callback_data="games")))
    elif call.data == "lootbox":
        text = f"📦 <b>RƯƠNG BÁU</b>\n\nMở 1 rương tốn 50,000đ."
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔓 MỞ RƯƠNG (50K)", callback_data="open_lootbox")).add(InlineKeyboardButton("🔙 Quay lại", callback_data="games"))
        safe_edit(call, text, markup)
    elif call.data == "open_lootbox":
        if user.get("balance", 0) < 50000: return bot.answer_callback_query(call.id, "❌ Cần ít nhất 50,000đ!", show_alert=True)
        update_user(uid, "balance", user["balance"] - 50000)
        add_history(uid, "Mở rương", -50000)
        rewards = ["10.000đ", "50.000đ", "100 PTS", "Key Tele 3M", "Key FB 2FA", "Trượt"]
        weights = [30, 20, 15, 10, 5, 20]
        result = random.choices(rewards, weights=weights, k=1)[0]
        if "đ" in result: update_user(uid, "balance", user["balance"] + int(result.replace(".", "").replace("đ", "")))
        elif "PTS" in result: update_user(uid, "points", user["points"] + int(result.replace(" PTS", "")))
        safe_edit(call, f"📦 <b>MỞ RƯƠNG</b>\n\nBạn nhận được: <b>{result}</b>!", InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="games")))
    elif call.data == "loan":
        text = f"💸 <b>VAY VỐN</b>\n\n💵 Đang nợ: <b>{format_money(user.get('loan', 0))}</b>\n\nNhập số tiền muốn vay (Tối đa 500k):"
        bot.send_message(call.message.chat.id, text, parse_mode="HTML")
        bot.register_next_step_handler(call.message, process_loan)
    elif call.data == "check_id":
        bot.send_message(call.message.chat.id, "🔍 Nhập UID TikTok hoặc Link:")
        bot.register_next_step_handler(call.message, process_check_id)
    elif call.data == "top_month":
        db = load_db()
        top_users = sorted(db["users"].items(), key=lambda x: x[1].get("total_deposit", 0), reverse=True)[:10]
        text = f"🏆 <b>BXH THÁNG {datetime.now().strftime('%m/%Y')}</b> 🏆\n────────────────────────────\n"
        for i, (u_id, u) in enumerate(top_users, 1):
            if u.get("total_deposit", 0) > 0: text += f"{i}. <b>{u['name']}</b> - {format_money(u['total_deposit'])}\n"
        if len(text.splitlines()) == 2: text += "<i>Chưa có ai nạp tiền tháng này.</i>"
        safe_edit(call, text, InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Quay lại", callback_data="back_home")))

    # MUA HÀNG
    elif call.data.startswith("buy_"):
        full_key = call.data.replace("buy_", "")
        if full_key not in PRODUCTS: return
        p = PRODUCTS[full_key]
        db = load_db()
        is_sale = any(s["key"] == full_key for s in db.get("flash_sale", []))
        price = int(p["price"] * 0.8) if is_sale else p["price"]
        if price > 0 and user.get("balance", 0) < price:
            return bot.answer_callback_query(call.id, "❌ Số dư không đủ!", show_alert=True)
        if price > 0: 
            update_user(uid, "balance", user["balance"] - price)
            add_history(uid, f"Mua {p['name']}", -price)
        pts_add = (price // 1000) * (2 if user.get("vip_level", 0) > 0 else 1)
        exp_add = price // 100
        new_exp = user.get("exp", 0) + exp_add
        new_level = user.get("level", 1)
        if new_exp >= 1000: new_level += 1; new_exp -= 1000
        db = load_db()
        db["orders"].append({"id": len(db["orders"]) + 1, "user_id": uid, "item": p["name"], "price": price, "time": time.strftime("%Y-%m-%d %H:%M:%S"), "status": "Đã giao"})
        db["users"][str(uid)]["points"] += pts_add
        db["users"][str(uid)]["exp"] = new_exp
        db["users"][str(uid)]["level"] = new_level
        item_key = f"KEY-{random.randint(100000, 999999)}"
        if str(uid) not in db["inventory"]: db["inventory"][str(uid)] = []
        db["inventory"][str(uid)].append({"item": p["name"], "key": item_key, "time": time.strftime("%d/%m %H:%M")})
        if str(uid) not in db["quests"]: db["quests"][str(uid)] = {"buy": 0, "transfer": 0}
        db["quests"][str(uid)]["buy"] += 1
        save_db(db)
        text = f"✅ <b>MUA THÀNH CÔNG</b>\n────────────────────────────\n📦 <b>{p['name']}</b>\n💵 Giá: <b>{format_money(price)}</b>\n💎 Nhận: <b>+{pts_add} PTS</b> | <b>+{exp_add} EXP</b>\n🔑 Key: <code>{item_key}</code>\n────────────────────────────\n<i>Key đã lưu vào Túi Đồ!</i>"
        safe_edit(call, text, InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 Về Menu", callback_data="back_home")))
        bot.answer_callback_query(call.id, "Mua thành công!")

# ================= XỬ LÝ INPUT LỆNH BOT =================
def process_calc(message):
    try:
        res = eval(message.text, {"__builtins__": None}, {})
        bot.reply_to(message, f"🧮 Kết quả: <b>{res}</b>", parse_mode="HTML")
    except: bot.reply_to(message, "❌ Phép tính không hợp lệ!")

def process_checkpass(message):
    pwd = message.text
    score = 0
    if len(pwd) >= 8: score += 1
    if any(c.isupper() for c in pwd): score += 1
    if any(c.isdigit() for c in pwd): score += 1
    if any(c in "!@#$%^&*" for c in pwd): score += 1
    bot.reply_to(message, f"🔑 Độ mạnh pass: <b>{score}/4</b>\n(4 là mạnh nhất)", parse_mode="HTML")

def process_b64(message):
    import base64
    try:
        encoded = base64.b64encode(message.text.encode()).decode()
        bot.reply_to(message, f"📝 Base64:\n<code>{encoded}</code>", parse_mode="HTML")
    except: bot.reply_to(message, "❌ Lỗi mã hóa!")

def process_chkuser(message):
    try:
        uid = str(message.text.strip())
        db = load_db()
        if uid in db["users"]:
            u = db["users"][uid]
            bot.reply_to(message, f"👤 User: {u.get('name')}\n💰 Số dư: {format_money(u.get('balance',0))}\n💎 PTS: {u.get('points',0)}\n🛡 VIP: {u.get('vip_level',0)}")
        else: bot.reply_to(message, "❌ Không tìm thấy User.")
    except: bot.reply_to(message, "❌ Lỗi.")

# ================= CÁC HÀM XỬ LÝ KHÁC =================
def process_bill(message):
    if not message.photo and not message.document: return bot.reply_to(message, "❌ Vui lòng gửi ảnh bill!")
    db = load_db()
    amount = 0
    if message.caption:
        try: amount = int(''.join(filter(str.isdigit, message.caption)))
        except: pass
    req_id = len(db["deposits"]) + 1
    db["deposits"].append({"id": req_id, "user_id": message.from_user.id, "name": message.from_user.first_name, "amount": amount, "photo_id": message.photo[-1].file_id if message.photo else "", "status": "pending", "time": time.strftime("%Y-%m-%d %H:%M:%S")})
    save_db(db)
    bot.reply_to(message, "✅ Đã gửi yêu cầu nạp tiền! Chờ Admin duyệt.")
    admin_text = f"🔔 <b>NẠP TIỀN</b>\n👤 User: {message.from_user.first_name} (<code>{message.from_user.id}</code>)\n💵 Số tiền: {format_money(amount) if amount > 0 else 'Chưa rõ'}\n📝 Mã: #{req_id}\n\n/duyet {req_id} {amount if amount > 0 else 'số_tiền'}"
    if message.photo: bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=admin_text, parse_mode="HTML")
    else: bot.send_message(ADMIN_ID, admin_text, parse_mode="HTML")

def process_withdraw(message, bank_name):
    try:
        parts = message.text.split()
        stk = parts[0]
        amount = int(parts[1])
        user = get_user(message.from_user.id)
        if amount < 20000: return bot.reply_to(message, "❌ Rút tối thiểu 20,000đ!")
        if user.get("balance", 0) < amount: return bot.reply_to(message, "❌ Số dư không đủ!")
        db = load_db()
        req_id = len(db["withdraws"]) + 1
        db["withdraws"].append({"id": req_id, "user_id": message.from_user.id, "bank": bank_name, "stk": stk, "amount": amount, "status": "pending", "time": time.strftime("%Y-%m-%d %H:%M:%S")})
        save_db(db)
        update_user(message.from_user.id, "balance", user["balance"] - amount)
        add_history(message.from_user.id, f"Rút tiền {bank_name}", -amount)
        bot.reply_to(message, f"✅ Đã tạo lệnh rút {format_money(amount)} về {bank_name} - {stk}. Chờ duyệt.")
        bot.send_message(ADMIN_ID, f"🔔 <b>RÚT TIỀN</b>\n👤 User: {message.from_user.first_name} (<code>{message.from_user.id}</code>)\n🏦 Bank: {bank_name}\n💳 STK: {stk}\n💵 Số tiền: {format_money(amount)}\n📝 Mã: #{req_id}\n\n/duyetrut {req_id}")
    except: bot.reply_to(message, "❌ Sai cú pháp! Nhập: [STK] [Số tiền]")

def process_gift(message):
    try:
        parts = message.text.split(maxsplit=2)
        target_id = int(parts[0])
        amount = int(parts[1])
        note = parts[2] if len(parts) > 2 else "Không có lời nhắn"
        sender = get_user(message.from_user.id)
        if amount < 1000: return bot.reply_to(message, "❌ Tối thiểu 1,000đ!")
        if sender.get("balance", 0) < amount: return bot.reply_to(message, "❌ Số dư không đủ!")
        receiver = get_user(target_id)
        if receiver.get("name", "Unknown") == "Unknown": return bot.reply_to(message, "❌ Không tìm thấy ID!")
        update_user(message.from_user.id, "balance", sender["balance"] - amount)
        update_user(target_id, "balance", receiver["balance"] + amount)
        add_history(message.from_user.id, f"Tặng quà {target_id}", -amount)
        add_history(target_id, f"Nhận quà từ {message.from_user.id}", amount)
        db = load_db()
        if str(message.from_user.id) in db["quests"]: db["quests"][str(message.from_user.id)]["transfer"] += 1; save_db(db)
        bot.reply_to(message, f"✅ Đã tặng {format_money(amount)} cho ID {target_id}.")
        try: bot.send_message(target_id, f"🎁 Bạn nhận được {format_money(amount)} từ ID {message.from_user.id}!\n💌 Lời nhắn: {note}")
        except: pass
    except: bot.reply_to(message, "❌ Sai cú pháp! Nhập: [ID] [Số tiền] [Lời nhắn]")

def process_shortlink(message):
    if not message.text: return bot.reply_to(message, "❌ Nhập link!")
    url = message.text.strip()
    try:
        r = requests.get(f"https://v.gd/create.php?format=simple&url={url}")
        if "error" in r.text.lower(): return bot.reply_to(message, "❌ Không rút gọn được link này!")
        bot.reply_to(message, f"🔗 Link rút gọn:\n<code>{r.text}</code>", parse_mode="HTML")
    except Exception as e: bot.reply_to(message, f"❌ Lỗi API: {e}")

def process_check_id(message):
    if not message.text: return bot.reply_to(message, "❌ Vui lòng nhập UID/Link dạng text!")
    uid_input = message.text.strip()
    now = datetime.now()
    check_data = {"name": "ken", "uid": uid_input, "status": "ĐANG HOẠT ĐỘNG", "note": "bot vip ken", "price": 0, "process_time": "Vừa xong", "created_at": now.strftime("%H:%M:%S %d/%m/%Y"), "progress": "Đang theo dõi chờ DIE ❌", "expire": "Vĩnh viễn"}
    db = load_db()
    db["tiktok_checks"][uid_input] = check_data
    save_db(db)
    text = f"🎵 <b>TIKTOK PROFILE</b>\n👤 Tên: <i>{check_data['name']}</i>\n🌐 UID: <code>{check_data['uid']}</code> - <a href='https://www.tiktok.com/@{check_data['uid']}'>Link</a>\n🟢 Trạng thái: <b>{check_data['status']}</b>\n📝 Ghi chú: {check_data['note']}\n💰 Giá: {check_data['price']} VNĐ\n📅 Thời gian xử lý: {check_data['process_time']}\n⏱ Thời gian tạo: {check_data['created_at']}\n📊 Tiến trình: {check_data['progress']}\n👤 Hạn trả kèo: <b>{check_data['expire']}</b>"
    markup = InlineKeyboardMarkup(row_width=2).add(InlineKeyboardButton("🔔 Cập nhật", callback_data=f"update_{uid_input}"), InlineKeyboardButton("📋 Danh Sách", callback_data="list_check")).add(InlineKeyboardButton("❌ Hủy kèo", callback_data=f"cancel_{uid_input}"), InlineKeyboardButton("✅ Done kèo", callback_data=f"done_{uid_input}"))
    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup, disable_web_page_preview=True)

def process_taixiu(message, choice):
    if not message.text: return bot.reply_to(message, "❌ Nhập số tiền!")
    try:
        amount = int(message.text.replace(",", "").replace(".", ""))
        if amount < 1000: return bot.reply_to(message, "❌ Cược tối thiểu 1,000đ!")
        user = get_user(message.from_user.id)
        if user.get("balance", 0) < amount: return bot.reply_to(message, "❌ Số dư không đủ!")
        update_user(message.from_user.id, "balance", user["balance"] - amount)
        add_history(message.from_user.id, f"Tài xỉu ({choice})", -amount)
        dice = [random.randint(1, 6) for _ in range(3)]
        total = sum(dice)
        result = "TÀI" if total >= 11 else "XỈU"
        msg = f"🎲 Xúc xắc: {dice} = {total} -> <b>{result}</b>\n"
        if result == choice:
            update_user(message.from_user.id, "balance", user["balance"] + amount * 2)
            add_history(message.from_user.id, "Thắng tài xỉu", amount * 2)
            msg += f"🎉 THẮNG! Nhận {format_money(amount * 2)}"
        else: msg += f"😢 THUA! Mất {format_money(amount)}"
        new_user = get_user(message.from_user.id)
        msg += f"\n💵 Số dư: <b>{format_money(new_user['balance'])}</b>"
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🎰 Chơi tiếp", callback_data="taixiu")).add(InlineKeyboardButton("🔙 Về Menu", callback_data="games"))
        bot.send_message(message.chat.id, msg, parse_mode="HTML", reply_markup=markup)
    except: bot.reply_to(message, "❌ Vui lòng nhập số tiền hợp lệ!")

def process_loan(message):
    try:
        amount = int(message.text)
        if amount < 10000 or amount > 500000: return bot.reply_to(message, "❌ Vay từ 10k đến 500k!")
        user = get_user(message.from_user.id)
        if user.get("loan", 0) > 0: return bot.reply_to(message, "❌ Đang có nợ xấu, không thể vay!")
        db = load_db()
        db["users"][str(message.from_user.id)]["loan"] = amount
        db["users"][str(message.from_user.id)]["loan_date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        db["users"][str(message.from_user.id)]["balance"] += amount
        save_db(db)
        add_history(message.from_user.id, "Vay vốn", amount)
        bot.reply_to(message, f"✅ Đã giải ngân {format_money(amount)}. Hạn trả: 7 ngày.")
    except: bot.reply_to(message, "❌ Vui lòng nhập số tiền hợp lệ!")

@bot.message_handler(commands=['mail'])
def cmd_mail(message):
    bot.send_message(message.chat.id, "📧 Đang tạo mail ảo, vui lòng đợi...")
    try:
        r = requests.get("https://api.mail.tm/domains").json()
        domain = r["hydra:member"][0]["domain"]
        email = f"kyo{random.randint(1000,9999)}@{domain}"
        pwd = f"pass{random.randint(10000,99999)}"
        requests.post("https://api.mail.tm/accounts", json={"address": email, "password": pwd})
        db = load_db()
        if str(message.from_user.id) not in db["mails"]: db["mails"][str(message.from_user.id)] = []
        db["mails"][str(message.from_user.id)].append({"email": email, "pwd": pwd})
        save_db(db)
        text = f"✅ <b>MAIL ĐÃ TẠO</b>\n📧 Mail: <code>{email}</code>\n🔑 Pass: <code>{pwd}</code>"
        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e: bot.send_message(message.chat.id, f"❌ Lỗi API: {e}")

@bot.message_handler(commands=['chuyentien'])
def cmd_chuyentien(message):
    try:
        parts = message.text.split()
        target_id, amount = int(parts[1]), int(parts[2])
        if amount < 1000: return bot.reply_to(message, "❌ Tối thiểu 1,000đ!")
        sender = get_user(message.from_user.id)
        if sender.get("balance", 0) < amount: return bot.reply_to(message, "❌ Số dư không đủ!")
        receiver = get_user(target_id)
        if receiver.get("name", "Unknown") == "Unknown": return bot.reply_to(message, "❌ Không tìm thấy ID!")
        update_user(message.from_user.id, "balance", sender["balance"] - amount)
        update_user(target_id, "balance", receiver["balance"] + amount)
        add_history(message.from_user.id, f"Chuyển tiền {target_id}", -amount)
        add_history(target_id, f"Nhận tiền từ {message.from_user.id}", amount)
        db = load_db()
        if str(message.from_user.id) in db["quests"]: db["quests"][str(message.from_user.id)]["transfer"] += 1; save_db(db)
        bot.reply_to(message, f"✅ Đã chuyển {format_money(amount)} cho ID {target_id}.")
        try: bot.send_message(target_id, f"💵 Bạn nhận được {format_money(amount)} từ ID {message.from_user.id}!")
        except: pass
    except: bot.reply_to(message, "❌ Sai cú pháp! Dùng: /chuyentien [ID] [Số tiền]")

# ================= ADMIN COMMANDS =================
@bot.message_handler(commands=['admin'])
def cmd_admin(message):
    if message.from_user.id != ADMIN_ID: return bot.reply_to(message, "❌ Không có quyền!")
    text = f"👑 <b>ADMIN PANEL</b>\n────────────────────────────\nLệnh:\n/duyet [Mã] [Tiền]\n/duyetrut [Mã]\n/addmoney [ID] [Tiền]\n/addpts [ID] [Điểm]\n/taocode [Mã] [Tiền]\n/broadcast [Text]"
    bot.send_message(message.chat.id, text, parse_mode="HTML")

@bot.message_handler(commands=['duyet'])
def cmd_duyet(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        req_id, amount = int(parts[1]), int(parts[2])
        db = load_db()
        for dep in db["deposits"]:
            if dep["id"] == req_id and dep["status"] == "pending":
                dep["status"] = "approved"
                dep["amount"] = amount
                uid = str(dep["user_id"])
                if uid in db["users"]:
                    db["users"][uid]["balance"] = db["users"][uid].get("balance", 0) + amount
                    db["users"][uid]["total_deposit"] = db["users"][uid].get("total_deposit", 0) + amount
                    save_db(db)
                    add_history(uid, "Nạp tiền duyệt", amount)
                    bot.reply_to(message, f"✅ Duyệt nạp {format_money(amount)} cho ID {uid}")
                    bot.send_message(dep["user_id"], f"✅ Nạp #{req_id} đã duyệt!\n💵 +{format_money(amount)}")
                    return
        bot.reply_to(message, "❌ Không tìm thấy yêu cầu!")
    except: bot.reply_to(message, "❌ Sai cú pháp!")

@bot.message_handler(commands=['duyetrut'])
def cmd_duyetrut(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        req_id = int(message.text.split()[1])
        db = load_db()
        for wd in db["withdraws"]:
            if wd["id"] == req_id and wd["status"] == "pending":
                wd["status"] = "approved"
                save_db(db)
                bot.reply_to(message, f"✅ Duyệt lệnh rút #{req_id}.")
                bot.send_message(wd["user_id"], f"✅ Lệnh rút #{req_id} đã được duyệt.")
                return
        bot.reply_to(message, "❌ Không tìm thấy!")
    except: bot.reply_to(message, "❌ Sai cú pháp!")

@bot.message_handler(commands=['addmoney'])
def cmd_addmoney(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        uid, amount = int(parts[1]), int(parts[2])
        user = get_user(uid)
        update_user(uid, "balance", user.get("balance", 0) + amount)
        add_history(uid, "Admin cấp tiền", amount)
        bot.reply_to(message, f"✅ Cộng {format_money(amount)} cho ID {uid}")
    except: bot.reply_to(message, "❌ Sai cú pháp!")

@bot.message_handler(commands=['addpts'])
def cmd_addpts(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        uid, pts = int(parts[1]), int(parts[2])
        user = get_user(uid)
        update_user(uid, "points", user.get("points", 0) + pts)
        bot.reply_to(message, f"✅ Cộng {pts} PTS cho ID {uid}")
    except: bot.reply_to(message, "❌ Sai cú pháp!")

@bot.message_handler(commands=['taocode'])
def cmd_taocode(message):
    if message.from_user.id != ADMIN_ID: return
    try:
        parts = message.text.split()
        code, amount = parts[1].upper(), int(parts[2])
        db = load_db()
        db["giftcodes"][code] = amount
        save_db(db)
        bot.reply_to(message, f"✅ Tạo giftcode {code} ({format_money(amount)})")
    except: bot.reply_to(message, "❌ Sai cú pháp!")

@bot.message_handler(commands=['broadcast'])
def cmd_broadcast(message):
    if message.from_user.id != ADMIN_ID: return
    text = message.text.replace("/broadcast", "").strip()
    if not text: return bot.reply_to(message, "❌ Nhập nội dung!")
    db = load_db()
    count = 0
    for uid in db["users"].keys():
        try:
            bot.send_message(int(uid), f"📢 <b>THÔNG BÁO</b>\n\n{text}", parse_mode="HTML")
            count += 1
            time.sleep(0.05)
        except: pass
    bot.reply_to(message, f"✅ Gửi tới {count} users.")

# ================= RUN =================
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    print(">>> KYO SHOP SYSTEM IS STARTING... <<<")
    try: set_commands()
    except: pass
    print(">> BOT ĐANG ONLINE. BẤM CTRL+C ĐỂ TẮT.")
    bot.infinity_polling(timeout=60)