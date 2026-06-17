# bot2_redistribuidor.py
import os
import json
import aiohttp
import logging
import re
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ParseMode

# Configuración
BOT_TOKEN_2 = os.environ.get("BOT_TOKEN_2")
API_ID = os.environ.get("API_ID")
API_HASH = os.environ.get("API_HASH")
BOT_COMM_CHANNEL = os.environ.get("BOT_COMM_CHANNEL", "-1001234567890")
FINAL_DEST_CHANNEL = os.environ.get("FINAL_DEST_CHANNEL", "-1002000000001")

app = Client("bot2", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN_2)

def extract_bin_info(source_info: str):
    """Extrae información REAL del BIN del source_info de Bot 1"""
    # Formato: "Chat: @AsukaScr | Bin: 546409 | Banco: SANTANDER | Marca: MASTERCARD | Tipo: DEBIT | Nivel: PREPAID | Pais: SPAIN"
    
    info = {
        "banco": "UNKNOWN BANK",
        "marca": "UNKNOWN",
        "tipo": "UNKNOWN",
        "nivel": "UNKNOWN",
        "pais": "UNKNOWN 🌍"
    }
    
    # Extraer información REAL si está disponible
    if "Banco:" in source_info:
        try:
            info["banco"] = source_info.split("Banco:")[1].split("|")[0].strip()
        except:
            pass
            
    if "Marca:" in source_info:
        try:
            info["marca"] = source_info.split("Marca:")[1].split("|")[0].strip()
        except:
            pass
            
    if "Tipo:" in source_info:
        try:
            info["tipo"] = source_info.split("Tipo:")[1].split("|")[0].strip()
        except:
            pass
            
    if "Nivel:" in source_info:
        try:
            info["nivel"] = source_info.split("Nivel:")[1].split("|")[0].strip()
        except:
            pass
            
    if "Pais:" in source_info:
        try:
            info["pais"] = source_info.split("Pais:")[1].split("|")[0].strip()
        except:
            pass
    
    return info

def extract_bin_number(card_data: str):
    """Extrae el BIN REAL de los datos de la tarjeta"""
    try:
        # Formato: "546409229029xxxx|09|2024|123"
        card_number = card_data.split("|")[0].strip()
        digits = re.sub(r'\D', '', card_number)
        return digits[:6] if len(digits) >= 6 else "000000"
    except:
        return "000000"

async def create_telegraph_article(card_data: str, source_info: str):
    """Crea artículo en telegra.ph con los datos REALES completos"""
    try:
        title = "💳 Serie Completa"
        content = [
            "<h3>OLIMPO FREE SCRAPPER</h3>",
            "<h4>🔐 Serie Completa</h4>",
            "<blockquote>",
            f"Serie= {card_data}",
            "</blockquote>",
            "<hr>",
            "<h4>🌍 Metadata</h4>",
            f"<p><b>Fuente:</b> {source_info}</p>",
            f"<p><b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            "<hr>",
            "<p><i>Publicado por OLIMPO BINS</i></p>"
        ]
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "title": title,
                "author_name": "OLIMPO BINS",
                "author_url": "https://t.me/",
                "content": json.dumps(content),
                "return_content": False
            }
            
            async with session.post(
                "https://api.telegra.ph/createPage",
                json=payload,
                timeout=30
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        return data["result"]["url"]
        
        return None
    except Exception as e:
        logging.error(f"❌ Error creando telegra.ph: {e}")
        return None

def format_visible_message(bin_number: str, bin_info: dict):
    """Formatea el mensaje con información REAL extraída"""
    message = f"""
<code>OLIMPO FREE SCRAPPER</code>
<code>#{bin_number}</code>
<code>━━━━━━━━</code>
<code>Bin= {bin_number}</code>
<code>Banco= {bin_info['banco']}</code>
<code>Marca= {bin_info['marca']}</code>
<code>Tipo= {bin_info['tipo']}</code>
<code>Nivel= {bin_info['nivel']}</code>
<code>País= {bin_info['pais']}</code>
<code>━━━━━━━━</code>
<code>OLIMPO BINS</code>
<code> @MrMxyzptlk04</code>
<code>━━━━━━━━</code>
"""
    return message

@app.on_message(filters.chat(BOT_COMM_CHANNEL) & filters.text)
async def handle_bot1_messages(client, message):
    """Procesa mensajes REALES de Bot 1"""
    try:
        if message.text.startswith("💳|"):
            parts = message.text.split("|", 2)
            if len(parts) >= 3:
                _, card_data, source_info = parts
                
                logging.info(f"📨 Mensaje REAL recibido: {source_info[:50]}...")
                
                # Extraer información REAL
                bin_number = extract_bin_number(card_data)
                bin_info = extract_bin_info(source_info)
                
                logging.info(f"🔍 BIN REAL: {bin_number}")
                logging.info(f"🏦 Banco REAL: {bin_info['banco']}")
                
                # Crear telegra.ph con datos REALES
                telegraph_url = await create_telegraph_article(card_data, source_info)
                
                if telegraph_url:
                    # Formatear mensaje con información REAL
                    formatted_message = format_visible_message(bin_number, bin_info)
                    
                    keyboard = InlineKeyboardMarkup([[
                        InlineKeyboardButton("Serie", url=telegraph_url)
                    ]])
                    
                    await app.send_message(
                        FINAL_DEST_CHANNEL,
                        formatted_message,
                        parse_mode=ParseMode.HTML,
                        reply_markup=keyboard
                    )
                    
                    logging.info(f"✅ Publicado con información REAL")
                    
    except Exception as e:
        logging.error(f"❌ Error: {e}")

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    )
    
    logging.info("🤖 Bot 2 iniciado - Extraerá información REAL de Bot 1")
    app.run()
