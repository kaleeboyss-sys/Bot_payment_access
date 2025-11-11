from config import ADMIN_ID, TRAKTEER_URL
import random
from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.utils import load_db, save_db

state = {}

def register_handlers(app):

    # ==== COMMAND /START ====
    @app.on_message(filters.command("start"))
    async def start_command(client, message):
        db = load_db()
        args = message.text.split()

        if len(args) == 2 and args[1].startswith("VIP"):
            code = args[1]
            if code in db:
                content = db[code]
                await message.reply_text(
                    f"💎 *Konten Premium*\n"
                    f"📌 Judul: {content['title']}\n"
                    f"💰 Harga: Rp{content['price']:,}\n\n"
                    f"Untuk akses, silakan bayar melalui Trakteer:\n{TRAKTEER_URL}\n\n"
                    f"Setelah membayar, kirim bukti ke admin.",
                    disable_web_page_preview=True
                )
            else:
                await message.reply_text("❌ Link tidak ditemukan.")
        else:
            await message.reply_text(
                "Halo! Kirim file atau link ke bot untuk membuat link berbayar (hanya admin)."
            )
            await message.delete()

    # ==== ADMIN: BUAT LINK PREMIUM ====
    @app.on_message(filters.user(ADMIN_ID) & ~filters.command(["shorturl", "list", "hapus"]))
    async def admin_handler(client, message):
        uid = str(message.from_user.id)
        db = load_db()

        if message.text and message.text.startswith("/"):
            return

        # Step 1: Minta judul
        if uid not in state:
            state[uid] = {"step": "judul", "content": message}
            await message.reply_text("📌 Masukkan *judul konten/link*:")
            return

        # Step 2: Simpan judul, lanjut ke harga
        if state[uid]["step"] == "judul":
            state[uid]["title"] = message.text
            state[uid]["step"] = "harga"
            await message.reply_text("💎 Masukkan *harga konten* (angka saja):")
            return

        # Step 3: Simpan harga dan buat link
        if state[uid]["step"] == "harga":
            try:
                price = int(message.text)
            except ValueError:
                return await message.reply_text("⚠️ Masukkan angka valid!")

            title = state[uid]["title"]
            content = state[uid]["content"]

            code = f"VIP{random.randint(10000, 99999)}"
            db[code] = {
                "title": title,
                "price": price,
                "file_id": getattr(content, "id", None),
                "text": getattr(content, "text", None),
            }
            save_db(db)

            bot_info = await app.get_me()
            link = f"https://t.me/{bot_info.username}?start={code}"

            await message.reply_text(
                f"✅ *Link berhasil dibuat!*\n\n"
                f"📌 Judul: {title}\n"
                f"💰 Harga: Rp{price:,}\n"
                f"🔗 Order Link: {link}",
                disable_web_page_preview=True
            )

            del state[uid]
            

    # ==== ADMIN: LIHAT LIST ====
    @app.on_message(filters.user(ADMIN_ID) & filters.command(["list"]))
    async def list_premium(client, message):
        db = load_db()
        if not db:
            return await message.reply_text("📭 Belum ada konten premium yang dibuat.")

        text = "📜 *Daftar Konten Premium:*\n\n"
        bot_info = await app.get_me()
        for code, data in db.items():
            link = f"https://t.me/{bot_info.username}?start={code}"
            text += (
                f"📌 *{data['title']}*\n"
                f"💰 Rp{data['price']:,}\n"
                f"🔗 [Order Link]({link})\n"
                f"🗑 /hapus_{code}\n\n"
            )

        await message.reply_text(text, disable_web_page_preview=True)
        await message.delete()

   # ==== ADMIN: HAPUS KONTEN (FIXED & DEBUG) ====
    @app.on_message(filters.user(ADMIN_ID) & filters.regex(r"^/hapus"))
    async def hapus_konten(client, message):
        db = load_db()
        teks = message.text.strip()

        # Debug log di terminal
       # print("== DEBUG HAPUS ==") 
       # print("Pesan:", teks) 
       # print("Database keys:", list(db.keys()))

        # Ambil kode setelah /hapus atau /hapus_
        if teks.startswith("/hapus_"):
            code = teks.replace("/hapus_", "").strip()
        else:
            code = teks.replace("/hapus", "").strip()
            await message.delete()

       # print("Code hasil parsing:", code)

        if code in db:
            del db[code]
            save_db(db)
            await message.reply_text(f"✅ Konten {code} berhasil dihapus.")
          #  print("✅ Dihapus:", code)
        else:
            await message.reply_text(f"❌ Kode {code} tidak ditemukan di database.")
          #  print("❌ Tidak ditemukan:", code)