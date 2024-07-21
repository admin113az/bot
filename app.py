import logging
import requests
from datetime import datetime
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, MessageHandler, filters, CallbackContext

# Cấu hình logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Khởi tạo Flask app
app = Flask(__name__)

# API token của Yeumoney và Blitly
YEUMONEY_API_TOKEN = 'e8edddc9ae4d29dcabd6a71f33422c4e5b7a8772f207335e882bf8d49357b4ed'
BLITLY_API_TOKEN = '63dca44244744c829e1607e384045e20'
TELEGRAM_BOT_TOKEN = '7416961605:AAG_WSkEAfz1_LGxfUfrgAjx5q6cW5ttLV4'

# Khởi tạo bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# Tập hợp để theo dõi các liên kết đã xử lý
processed_links = set()

# Hàm rút gọn link qua Yeumoney
def shorten_with_yeumoney(url: str) -> str:
    yeumoney_api_url = f'https://yeumoney.com/QL_api.php?token={YEUMONEY_API_TOKEN}&format=json&url={url}'
    response = requests.get(yeumoney_api_url)
    data = response.json()
    if data['status'] == 'success':
        return data['shortenedUrl']
    else:
        raise Exception(f"Yeumoney API error: {data['status']}")

# Hàm rút gọn link qua Blitly
def shorten_with_blitly(url: str) -> str:
    blitly_api_url = f'https://apimanegement.blitly.io/api/public/gen-shorten-link?apikey={BLITLY_API_TOKEN}&url={url}'
    response = requests.get(blitly_api_url)
    data = response.json()
    if 'url' in data:
        return f"https://blitly.io/{data['id']}"
    else:
        raise Exception(f"Blitly API error: {data}")

# Hàm lấy ngày tháng hiện tại
def get_current_date() -> str:
    now = datetime.now()
    return now.strftime("%d/%m/%Y")

# Hàm xử lý tin nhắn từ người dùng
async def handle_message(update: Update, context: CallbackContext) -> None:
    try:
        user_message = update.message.text

        # Kiểm tra nếu tin nhắn bắt đầu với "key"
        if user_message.lower().startswith("key "):
            # Tách liên kết từ tin nhắn
            parts = user_message.split(" ", 1)
            if len(parts) > 1:
                original_url = parts[1].strip()

                # Kiểm tra nếu liên kết đã được xử lý
                if original_url in processed_links:
                    await update.message.reply_text('Liên kết này đã được xử lý.')
                    return

                # Rút gọn liên kết qua Yeumoney
                yeumoney_shortened_url = shorten_with_yeumoney(original_url)

                # Rút gọn liên kết đã rút gọn qua Blitly
                blitly_shortened_url = shorten_with_blitly(yeumoney_shortened_url)

                formatted_date = get_current_date()

                response_message = (
                    f"KEY NGÀY {formatted_date}**\n\n"
                    "**⚠️KEY sẽ HẾT HẠN vào 5h SÁNG NGÀY HÔM SAU⚠️**\n\n"
                    "**⭐️KEY dùng để LOGIN vào IPA LIÊN QUÂN MAP & MOD, DÙNG ĐỂ MỞ MENU MOD SKIN**\n\n"
                    "**⚠️Tranh thủ lấy KEY sớm, đừng để muộn hết mã sẽ KHÔNG LẤY ĐƯỢC KEY⚠️**\n\n"
                    "**➡️Vượt link bên dưới để lấy KEY: (Bạn vượt link lấy key là đã ủng hộ ad có động lực cống hiến cho Team Hd Mod rồi đó😙 Nhớ mở link bằng trình duyệt nhé)**\n\n"
                    f"{blitly_shortened_url}"
                )
                await update.message.reply_text(response_message, parse_mode='Markdown')

                # Thêm liên kết vào tập hợp đã xử lý
                processed_links.add(original_url)
            else:
                await update.message.reply_text('Vui lòng gửi liên kết sau từ khóa "key". Ví dụ: key https://example.com')

    except Exception as e:
        await update.message.reply_text(f'Có lỗi xảy ra: {str(e)}')

# Khởi tạo ứng dụng
application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    application.process_update(update)
    return 'ok', 200

if __name__ == '__main__':
    import asyncio
    import os
    from datetime import datetime
    loop = asyncio.get_event_loop()
    loop.run_until_complete(application.initialize())
    loop.run_until_complete(application.start())
    loop.run_until_complete(application.updater.start_polling())
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
