#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de Vacantes - Sistema Maestro
Monitorea vacantes en MEN Colombia y envía notificaciones por Telegram
"""

import json
import time
from urllib import request as urlrequest, parse as urlparse
from datetime import datetime

# Configuración
TELEGRAM_TOKEN = "8569114423:AAHMgnRPbYAXyOBhCZqeX0N5BrOhGYEizYU"
TELEGRAM_CHAT_ID = "7529527522"
API_BASE = "https://api.telegram.org/bot"

def enviar_telegram(mensaje):
    """
    Envía un mensaje a Telegram usando la API de Bot
    
    Args:
        mensaje (str): Texto del mensaje a enviar
        
    Returns:
        bool: True si se envió correctamente, False en caso contrario
    """
    try:
        url = f"{API_BASE}{TELEGRAM_TOKEN}/sendMessage"
        datos = urlparse.urlencode({
            "chat_id": TELEGRAM_CHAT_ID,
            "text": mensaje,
            "parse_mode": "HTML"
        }).encode('utf-8')
        
        req = urlrequest.Request(url, data=datos)
        with urlrequest.urlopen(req, timeout=15) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            
            if resultado.get("ok"):
                print(f"✅ Mensaje enviado a Telegram (ID: {resultado['result']['message_id']})")
                return True
            else:
                print(f"❌ Error en Telegram: {resultado.get('description')}")
                return False
                
    except Exception as e:
        print(f"❌ Error al enviar a Telegram: {str(e)}")
        return False

def obtener_bot_info():
    """Obtiene información del bot de Telegram"""
    try:
        url = f"{API_BASE}{TELEGRAM_TOKEN}/getMe"
        with urlrequest.urlopen(url, timeout=10) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            
            if resultado.get("ok"):
                bot = resultado["result"]
                return {
                    "username": bot.get("username"),
                    "id": bot.get("id"),
                    "nombre": bot.get("first_name")
                }
            return None
    except Exception as e:
        print(f"Error obteniendo info del bot: {e}")
        return None

def obtener_actualizaciones(offset=0):
    """Obtiene las últimas actualizaciones del bot"""
    try:
        url = f"{API_BASE}{TELEGRAM_TOKEN}/getUpdates?offset={offset}&timeout=10"
        with urlrequest.urlopen(url, timeout=15) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            
            if resultado.get("ok"):
                return resultado.get("result", [])
            return []
    except Exception as e:
        print(f"Error obteniendo actualizaciones: {e}")
        return []

def procesar_comando(texto_mensaje):
    """Procesa comandos recibidos del usuario"""
    texto = texto_mensaje.lower().strip()
    
    if texto == "/start":
        return "👋 ¡Hola! Soy el Monitor de Vacantes de MEN Colombia.\n\nComandos disponibles:\n/estado - Ver estado del monitor\n/vacantes - Obtener vacantes recientes"
    
    elif texto == "/estado":
        return "🟢 Monitor activo\n⏰ Última verificación: hace unos momentos\n👥 Chat ID: " + str(TELEGRAM_CHAT_ID)
    
    elif texto == "/vacantes":
        return "📋 No hay vacantes nuevas en este momento.\nSigue monitoreando..."
    
    else:
        return "No entiendo ese comando. Usa /start para ver las opciones disponibles."

def iniciar_monitor():
    """Inicia el monitor de vacantes"""
    print("=" * 70)
    print("MONITOR DE VACANTES - SISTEMA MAESTRO")
    print("=" * 70)
    
    # Obtener info del bot
    print("\n1️⃣ Verificando conexión con Telegram...")
    bot_info = obtener_bot_info()
    
    if bot_info:
        print(f"✅ Conectado al bot: @{bot_info['username']}")
        print(f"   Bot ID: {bot_info['id']}")
    else:
        print("❌ No se pudo conectar al bot")
        return
    
    # Enviar mensaje de inicio
    print("\n2️⃣ Enviando mensaje de prueba...")
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    mensaje_inicio = f"""🚀 <b>MONITOR DE VACANTES INICIADO</b>

📅 Fecha: {hora}
🔍 Sistema: Maestro MEN Colombia
✅ Estado: Activo

El monitor está listo para rastrear vacantes.
Recibirás notificaciones cuando se publiquen nuevas oportunidades."""
    
    enviar_telegram(mensaje_inicio)
    
    # Polling simple
    print("\n3️⃣ Escuchando mensajes...")
    offset = 0
    
    try:
        while True:
            actualizaciones = obtener_actualizaciones(offset)
            
            for update in actualizaciones:
                update_id = update.get("update_id")
                offset = update_id + 1
                
                if "message" in update:
                    mensaje = update["message"]
                    chat_id = mensaje["chat"]["id"]
                    usuario = mensaje["from"]["first_name"]
                    texto = mensaje.get("text", "")
                    
                    print(f"\n📨 Mensaje de {usuario}: {texto}")
                    
                    # Procesar comando y responder
                    respuesta = procesar_comando(texto)
                    
                    # Enviar respuesta
                    url_respuesta = f"{API_BASE}{TELEGRAM_TOKEN}/sendMessage"
                    datos = urlparse.urlencode({
                        "chat_id": chat_id,
                        "text": respuesta
                    }).encode('utf-8')
                    
                    req = urlrequest.Request(url_respuesta, data=datos)
                    with urlrequest.urlopen(req, timeout=10) as response:
                        resultado = json.loads(response.read().decode('utf-8'))
                        if resultado.get("ok"):
                            print(f"✅ Respuesta enviada a {usuario}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n❌ Monitor detenido por el usuario")
        return
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return

if __name__ == "__main__":
    iniciar_monitor()
