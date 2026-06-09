# Monitor de Vacantes en Replit

## ¿Qué es Replit?
Replit es una plataforma donde puedes ejecutar código Python **gratuitamente en la nube**. El bot correrá 24/7 sin necesidad de tu computadora.

## Pasos para configurar:

### 1. Crear cuenta en Replit
- Ve a https://replit.com
- Crea una cuenta (gratis)
- Haz clic en "Create Repl"

### 2. Crear un nuevo proyecto
- Selecciona "Python" como lenguaje
- Dale un nombre: `monitor-vacantes`

### 3. Copiar los archivos
- En Replit, crea dos archivos:

#### Archivo 1: `main.py`
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import time
from urllib import request as urlrequest, parse as urlparse
from datetime import datetime

TELEGRAM_TOKEN = "8569114423:AAHMgnRPbYAXyOBhCZqeX0N5BrOhGYEizYU"
TELEGRAM_CHAT_ID = "7529527522"
API_BASE = "https://api.telegram.org/bot"

def enviar_telegram(mensaje):
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
                print(f"✅ Mensaje enviado (ID: {resultado['result']['message_id']})")
                return True
            else:
                print(f"❌ Error: {resultado.get('description')}")
                return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def obtener_bot_info():
    try:
        url = f"{API_BASE}{TELEGRAM_TOKEN}/getMe"
        with urlrequest.urlopen(url, timeout=10) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            if resultado.get("ok"):
                bot = resultado["result"]
                return {"username": bot.get("username"), "id": bot.get("id")}
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def obtener_actualizaciones(offset=0):
    try:
        url = f"{API_BASE}{TELEGRAM_TOKEN}/getUpdates?offset={offset}"
        with urlrequest.urlopen(url, timeout=10) as response:
            resultado = json.loads(response.read().decode('utf-8'))
            if resultado.get("ok"):
                return resultado.get("result", [])
            return []
    except Exception as e:
        print(f"Error: {e}")
        return []

def procesar_comando(texto):
    texto = texto.lower().strip()
    if texto == "/start":
        return "👋 ¡Hola! Soy el Monitor de Vacantes.\n\n/estado - Ver estado\n/vacantes - Ver vacantes"
    elif texto == "/estado":
        return "🟢 Monitor activo en Replit"
    elif texto == "/vacantes":
        return "📋 Monitoreando vacantes..."
    else:
        return "Comando no entendido. Usa /start"

def main():
    print("=" * 60)
    print("MONITOR DE VACANTES EN REPLIT")
    print("=" * 60)
    
    bot_info = obtener_bot_info()
    if bot_info:
        print(f"✅ Bot: @{bot_info['username']}")
    else:
        print("❌ Error al conectar")
        return
    
    hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    mensaje = f"🚀 Monitor iniciado en Replit\n📅 {hora}\n✅ Estado: Activo"
    enviar_telegram(mensaje)
    
    print("\n📨 Escuchando mensajes...")
    offset = 0
    
    try:
        while True:
            actualizaciones = obtener_actualizaciones(offset)
            
            for update in actualizaciones:
                offset = update.get("update_id", 0) + 1
                
                if "message" in update:
                    msg = update["message"]
                    chat_id = msg["chat"]["id"]
                    usuario = msg["from"].get("first_name", "Usuario")
                    texto = msg.get("text", "")
                    
                    print(f"\n📨 De {usuario}: {texto}")
                    
                    respuesta = procesar_comando(texto)
                    
                    url = f"{API_BASE}{TELEGRAM_TOKEN}/sendMessage"
                    datos = urlparse.urlencode({
                        "chat_id": chat_id,
                        "text": respuesta
                    }).encode('utf-8')
                    
                    req = urlrequest.Request(url, data=datos)
                    try:
                        with urlrequest.urlopen(req, timeout=10) as r:
                            resultado = json.loads(r.read().decode('utf-8'))
                            if resultado.get("ok"):
                                print(f"✅ Respuesta enviada a {usuario}")
                    except:
                        pass
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n❌ Monitor detenido")

if __name__ == "__main__":
    main()
```

#### Archivo 2: `replit.nix` (dependencias)
```nix
{ pkgs }: {
  deps = [
    pkgs.python310
  ];
}
```

### 4. Ejecutar el bot
- En Replit, haz clic en "Run"
- El bot empezará a escuchar mensajes

### 5. Prueba
- Abre Telegram
- Envía `/start` a `@monitor_vacantes_bot`
- ¡Deberías recibir respuesta!

## ¿Qué ocurre después?
El bot correrá **sin parar** en Replit (gratis, con límites justos). Si quieres que sea permanente:
- Usa Replit Deployments (gratis)
- O paga $7/mes para Always On

## Preguntas frecuentes

**¿Necesito mi computadora prendida?**
No. Replit ejecuta el código en sus servidores.

**¿Es gratis?**
Sí, con limitaciones. Para siempre encendido, es de pago.

**¿Puedo usar otro servicio?**
Sí: Railway, Heroku (de pago), AWS, Google Cloud, etc.

---

¿Quieres que cree un script para desplegar automáticamente?
