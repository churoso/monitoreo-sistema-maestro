#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de diagnóstico para verificar credenciales de Telegram
"""

import json
from urllib import request as urlrequest, parse as urlparse

def verificar_credenciales():
    """Verifica si el token y chat ID son válidos."""
    token = "8569114423:AAHMgnRPbYAXyOBhCZqeX0N5BrOhGYEizYU"
    chat_id = "7529527522"
    
    print("=" * 60)
    print("DIAGNÓSTICO DE TELEGRAM")
    print("=" * 60)
    
    # Paso 1: Verificar el bot
    print("\n1️⃣ Verificando token del bot...")
    try:
        url = f"https://api.telegram.org/bot{token}/getMe"
        with urlrequest.urlopen(url, timeout=10) as r:
            respuesta = json.loads(r.read().decode())
        
        if respuesta.get("ok"):
            bot_info = respuesta.get("result", {})
            print(f"✅ Bot encontrado: @{bot_info.get('username')}")
            print(f"   ID: {bot_info.get('id')}")
            print(f"   Nombre: {bot_info.get('first_name')}")
        else:
            print(f"❌ Error: {respuesta.get('description')}")
            return False
    except Exception as e:
        print(f"❌ Error al conectar: {e}")
        return False
    
    # Paso 2: Enviar mensaje de prueba
    print(f"\n2️⃣ Enviando mensaje a chat {chat_id}...")
    mensaje_prueba = "🧪 Prueba de envío - Sistema Maestro"
    
    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        datos = urlparse.urlencode({
            "chat_id": chat_id, 
            "text": mensaje_prueba
        }).encode()
        
        with urlrequest.urlopen(urlrequest.Request(url, data=datos), timeout=10) as r:
            respuesta = json.loads(r.read().decode())
        
        if respuesta.get("ok"):
            msg_id = respuesta.get("result", {}).get("message_id")
            print(f"✅ Mensaje enviado exitosamente (ID: {msg_id})")
            return True
        else:
            error = respuesta.get("description", "Error desconocido")
            print(f"❌ Error: {error}")
            if "chat not found" in error.lower():
                print("   → El chat_id podría ser incorrecto")
            elif "bot was blocked" in error.lower():
                print("   → El bot fue bloqueado. Desbloquéalo en Telegram")
            return False
    except Exception as e:
        print(f"❌ Error al enviar: {e}")
        return False

if __name__ == "__main__":
    verificar_credenciales()
