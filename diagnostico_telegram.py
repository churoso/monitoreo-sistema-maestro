#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script avanzado de diagnóstico para Telegram Bot
Muestra todos los detalles de la configuración
"""

import json
from urllib import request as urlrequest, parse as urlparse

def hacer_request(url, metodo="GET", datos=None):
    """Hace un request a la API de Telegram y devuelve la respuesta."""
    try:
        if metodo == "POST" and datos:
            datos = urlparse.urlencode(datos).encode()
            req = urlrequest.Request(url, data=datos, method="POST")
        else:
            req = urlrequest.Request(url)
        
        with urlrequest.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"ok": False, "error": str(e)}

def main():
    token = "8569114423:AAHMgnRPbYAXyOBhCZqeX0N5BrOhGYEizYU"
    chat_id = "7529527522"
    
    print("=" * 70)
    print("DIAGNÓSTICO COMPLETO DEL BOT DE TELEGRAM")
    print("=" * 70)
    
    # PASO 1: Verificar token
    print("\n📍 PASO 1: Verificando token del bot...")
    print("-" * 70)
    
    url_getme = f"https://api.telegram.org/bot{token}/getMe"
    respuesta = hacer_request(url_getme)
    
    print(f"URL: {url_getme}")
    print(f"Respuesta: {json.dumps(respuesta, indent=2, ensure_ascii=False)}")
    
    if not respuesta.get("ok"):
        print("\n❌ ERROR: El token podría ser inválido o expirado")
        print("Solución: Verifica el token en BotFather")
        return
    
    bot_info = respuesta.get("result", {})
    print(f"\n✅ Bot encontrado:")
    print(f"   - Username: @{bot_info.get('username')}")
    print(f"   - ID: {bot_info.get('id')}")
    print(f"   - Nombre: {bot_info.get('first_name')}")
    print(f"   - ¿Es bot?: {bot_info.get('is_bot')}")
    
    # PASO 2: Verificar actualizaciones recientes
    print("\n\n📍 PASO 2: Verificando mensajes recientes...")
    print("-" * 70)
    
    url_updates = f"https://api.telegram.org/bot{token}/getUpdates"
    respuesta_updates = hacer_request(url_updates)
    
    print(f"URL: {url_updates}")
    
    if respuesta_updates.get("ok"):
        updates = respuesta_updates.get("result", [])
        print(f"✅ Se encontraron {len(updates)} actualizaciones recientes\n")
        
        if updates:
            for i, update in enumerate(updates[-3:], 1):  # Últimas 3
                print(f"Actualización {i}:")
                print(f"  - Update ID: {update.get('update_id')}")
                
                if "message" in update:
                    msg = update["message"]
                    print(f"  - Chat ID: {msg.get('chat', {}).get('id')}")
                    print(f"  - Usuario: {msg.get('from', {}).get('first_name')}")
                    print(f"  - Texto: {msg.get('text', 'N/A')}")
                    print(f"  - Hora: {msg.get('date')}")
                print()
        else:
            print("⚠️  No hay actualizaciones recientes. Esto podría significar:")
            print("   - El bot fue bloqueado")
            print("   - No has iniciado una conversación con el bot")
            print("\n   Solución: Abre Telegram y envía /start al bot @monitor_vacantes_bot")
    else:
        print(f"❌ Error: {respuesta_updates}")
    
    # PASO 3: Intentar enviar mensaje
    print("\n📍 PASO 3: Intentando enviar mensaje de prueba...")
    print("-" * 70)
    
    url_sendmessage = f"https://api.telegram.org/bot{token}/sendMessage"
    datos_mensaje = {
        "chat_id": chat_id,
        "text": "🧪 Test desde diagnóstico - Sistema Maestro"
    }
    
    print(f"URL: {url_sendmessage}")
    print(f"Datos: {datos_mensaje}")
    
    respuesta_envio = hacer_request(url_sendmessage, metodo="POST", datos=datos_mensaje)
    print(f"Respuesta: {json.dumps(respuesta_envio, indent=2, ensure_ascii=False)}")
    
    if respuesta_envio.get("ok"):
        print("\n✅ Mensaje enviado exitosamente")
        msg_id = respuesta_envio.get("result", {}).get("message_id")
        print(f"   - ID del mensaje: {msg_id}")
        print(f"   - Deberías verlo en Telegram ahora")
    else:
        error = respuesta_envio.get("description", "Error desconocido")
        print(f"\n❌ Error al enviar: {error}")
        
        if "chat not found" in error.lower():
            print("\n💡 Solución: El chat_id es incorrecto o el bot fue bloqueado")
            print("   1. Abre Telegram")
            print("   2. Busca @monitor_vacantes_bot")
            print("   3. Envía /start")
            print("   4. Luego ejecuta: python diagnostico_telegram.py")
        elif "bot was blocked" in error.lower():
            print("\n💡 Solución: El bot fue bloqueado")
            print("   1. Abre Telegram")
            print("   2. Busca @monitor_vacantes_bot")
            print("   3. Desbloquea el bot")
            print("   4. Envía /start")
        else:
            print(f"\n💡 Error desconocido: {error}")
    
    # PASO 4: Información de referencia
    print("\n\n📍 INFORMACIÓN DE REFERENCIA:")
    print("-" * 70)
    print(f"Token: {token[:30]}...")
    print(f"Chat ID: {chat_id}")
    print(f"Bot URL: https://t.me/monitor_vacantes_bot")
    print("\n")

if __name__ == "__main__":
    main()
