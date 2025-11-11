from pyrogram import Client
from bot.handlers import register_handlers
from config import API_ID, API_HASH, BOT_TOKEN

app = Client("trakteer_paidlink", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

register_handlers(app)

if __name__ == "__main__":
    app.run()