#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para enviar un mensaje de prueba a Telegram AHORA MISMO
"""

import os
from urllib import request as urlrequest, parse as urlparse

def enviar_mensaje_prueba():
    """Envía un mensaje de prueba a Telegram."""
    token = "8569114423:AAHMgnRPbYAXyOBhCZqeX0N5BrOhGYEizYU"
    chat_id = "7529527522"
    
    fecha_hora = __import__('datetime').datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    mensaje = f"""🚀 PRUEBA DEL MONITOR DE VACANTES
    
Hora: {fecha_hora}

✅ ¡El sistema funciona correctamente!
✅ Los mensajes se envían sin problemas
✅ Está listo para monitorear vacantes

Monitor: Sistema Maestro (MEN Colombia)
"""
    
    print(f"📱 Enviando mensaje a Telegram...")
    print(f"Token: {token[:20]}...")
    print(f"Chat ID: {chat_id}")
    print(f"\nMensaje:\n{mensaje}")
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    datos = urlparse.urlencode({"chat_id": chat_id, "text": mensaje}).encode()
    
    try:
        with urlrequest.urlopen(urlrequest.Request(url, data=datos), timeout=20) as r:
            respuesta = r.read()
        print("\n✅ ¡Mensaje enviado exitosamente a Telegram!")
        return True
    except Exception as e:
        print(f"\n❌ Error al enviar: {e}")
        return False

if __name__ == "__main__":
    enviar_mensaje_prueba()
