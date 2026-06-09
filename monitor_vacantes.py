#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor de vacantes del Sistema Maestro (MEN, Colombia).

Qué hace:
  1. Abre el buscador público de vacantes.
  2. Lee las vacantes cargadas (bloque "VACANTES CARGADAS EN EL DÍA"
     y/o resultados de la tabla).
  3. Filtra por los departamentos y áreas que te interesan.
  4. Compara con lo visto en ejecuciones anteriores (estado en disco).
  5. Si hay vacantes NUEVAS, te avisa por correo y/o Telegram.

Pensado para correr solo, en bucle (tu PC/servidor) o por agenda
(GitHub Actions / cron). No guarda contraseñas en el código: todo
se lee de variables de entorno (ver README).
"""

import os
import sys
import json
import time
import smtplib
import hashlib
import datetime as dt
from email.mime.text import MIMEText
from email.header import Header
from urllib import request as urlrequest, parse as urlparse

# --- Playwright se importa de forma perezosa para poder validar el
#     resto del script aunque no esté instalado todavía. ---
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_OK = True
except Exception:
    PLAYWRIGHT_OK = False


# =====================================================================
# CONFIGURACIÓN  (ajústala a tu gusto)
# =====================================================================
URL = "https://sistemamaestro.mineducacion.gov.co/SistemaMaestro/busquedaVacantes.xhtml"

# Departamentos y áreas que te interesan (coincidencia por texto, sin
# distinguir mayúsculas/acentos). Edita estas listas cuando quieras.
TARGET_DEPARTAMENTOS = ["Cauca", "Nariño", "Huila", "Putumayo"]
TARGET_AREAS = ["Tecnología e informática", "Primaria"]

# Si True, una vacante debe coincidir con un departamento Y un área.
# Si te llegan 0 resultados y sospechas que la tabla no muestra el área,
# pon esto en False para filtrar solo por departamento.
REQUIRE_AREA_MATCH = True

# Archivo donde se recuerda lo ya notificado (para no repetir avisos).
STATE_FILE = os.environ.get("STATE_FILE", "estado_vacantes.json")

# Segundos de espera para que cargue la tabla (sitio JSF/PrimeFaces).
PAGE_TIMEOUT_MS = 45000


# =====================================================================
# UTILIDADES DE TEXTO
# =====================================================================
def normaliza(texto: str) -> str:
    """Minúsculas y sin acentos, para comparar de forma robusta."""
    if not texto:
        return ""
    t = texto.lower()
    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}
    for a, b in reemplazos.items():
        t = t.replace(a, b)
    return " ".join(t.split())  # colapsa espacios


def fila_coincide(texto_fila: str) -> bool:
    t = normaliza(texto_fila)
    dep_ok = any(normaliza(d) in t for d in TARGET_DEPARTAMENTOS)
    if not dep_ok:
        return False
    if REQUIRE_AREA_MATCH:
        area_ok = any(normaliza(a) in t for a in TARGET_AREAS)
        return area_ok
    return True


def huella(texto_fila: str) -> str:
    """Identificador estable de una vacante a partir de su texto."""
    return hashlib.sha256(normaliza(texto_fila).encode("utf-8")).hexdigest()[:16]


# =====================================================================
# ESTADO (para no notificar lo mismo dos veces)
# =====================================================================
def cargar_estado() -> set:
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f).get("vistas", []))
    except Exception:
        return set()


def guardar_estado(vistas: set) -> None:
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"actualizado": dt.datetime.now().isoformat(),
                   "vistas": sorted(vistas)}, f, ensure_ascii=False, indent=2)


# =====================================================================
# LECTURA DE LA PÁGINA (Playwright maneja el JavaScript/AJAX del sitio)
# =====================================================================
def leer_vacantes() -> list:
    """Devuelve una lista de filas (texto) que parecen vacantes."""
    if not PLAYWRIGHT_OK:
        raise RuntimeError(
            "Playwright no está instalado. Ejecuta:\n"
            "  pip install playwright && playwright install chromium")

    filas = []
    with sync_playwright() as p:
        navegador = p.chromium.launch(headless=True)
        pagina = navegador.new_page()
        pagina.set_default_timeout(PAGE_TIMEOUT_MS)
        pagina.goto(URL, wait_until="networkidle")

        # Pequeña espera extra por si la tabla termina de pintar vía AJAX.
        pagina.wait_for_timeout(2500)

        # Tomamos TODAS las filas de tabla de la página y luego filtramos
        # por texto. Así no dependemos de IDs internos de JSF (que cambian).
        for tr in pagina.query_selector_all("tr"):
            try:
                texto = tr.inner_text().strip()
            except Exception:
                continue
            if not texto:
                continue
            t = normaliza(texto)
            # Descartamos encabezados y el mensaje de "no hay vacantes".
            if "no existen vacantes" in t:
                continue
            if "departamento/municipio" in t or "tipo priorizacion" in t:
                continue
            filas.append(texto)
        navegador.close()
    return filas


# =====================================================================
# NOTIFICACIONES
# =====================================================================
def enviar_correo(asunto: str, cuerpo: str) -> None:
    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    user = os.environ.get("SMTP_USER")
    pwd = os.environ.get("SMTP_PASS")
    destino = os.environ.get("EMAIL_DESTINO", user)
    if not (user and pwd):
        print("[correo] SMTP_USER/SMTP_PASS no configurados; se omite correo.")
        return
    msg = MIMEText(cuerpo, "plain", "utf-8")
    msg["Subject"] = Header(asunto, "utf-8")
    msg["From"] = user
    msg["To"] = destino
    with smtplib.SMTP(host, port) as s:
        s.starttls()
        s.login(user, pwd)
        s.sendmail(user, [destino], msg.as_string())
    print(f"[correo] Enviado a {destino}.")


def enviar_telegram(texto: str) -> None:
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not (token and chat_id):
        print("[telegram] TELEGRAM_TOKEN/CHAT_ID no configurados; se omite.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    datos = urlparse.urlencode({"chat_id": chat_id, "text": texto}).encode()
    try:
        with urlrequest.urlopen(urlrequest.Request(url, data=datos), timeout=20) as r:
            r.read()
        print("[telegram] Enviado.")
    except Exception as e:
        print(f"[telegram] Error: {e}")


def notificar(nuevas: list) -> None:
    fecha = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    encabezado = f"Sistema Maestro: {len(nuevas)} vacante(s) nueva(s) — {fecha}"
    lineas = [encabezado, ""]
    for i, fila in enumerate(nuevas, 1):
        # Compactamos cada fila a una línea legible.
        compacta = " | ".join(s.strip() for s in fila.splitlines() if s.strip())
        lineas.append(f"{i}. {compacta}")
    lineas += ["", f"Revisa: {URL}"]
    cuerpo = "\n".join(lineas)
    print(cuerpo)
    enviar_correo(encabezado, cuerpo)
    enviar_telegram(cuerpo[:3900])  # Telegram limita el tamaño del mensaje.


# =====================================================================
# CICLO PRINCIPAL
# =====================================================================
def revisar_una_vez() -> int:
    vistas = cargar_estado()
    filas = leer_vacantes()
    interesantes = [f for f in filas if fila_coincide(f)]

    nuevas = []
    nuevas_huellas = set()
    for f in interesantes:
        h = huella(f)
        if h not in vistas:
            nuevas.append(f)
            nuevas_huellas.add(h)

    if nuevas:
        notificar(nuevas)
        guardar_estado(vistas | nuevas_huellas)
    else:
        print(f"[{dt.datetime.now():%H:%M}] Sin vacantes nuevas que coincidan "
              f"({len(interesantes)} coinciden, ya notificadas).")
    return len(nuevas)


def main():
    # Modo bucle: pasa el intervalo en minutos como argumento, p. ej.:
    #   python monitor_vacantes.py 60   -> revisa cada 60 minutos
    # Sin argumento: revisa una sola vez (ideal para GitHub Actions/cron).
    if len(sys.argv) > 1:
        try:
            minutos = int(sys.argv[1])
        except ValueError:
            print("Uso: python monitor_vacantes.py [minutos_entre_revisiones]")
            sys.exit(1)
        print(f"Monitor en bucle cada {minutos} min. Ctrl+C para detener.")
        while True:
            try:
                revisar_una_vez()
            except Exception as e:
                print(f"[error] {e}")
            time.sleep(minutos * 60)
    else:
        revisar_una_vez()


if __name__ == "__main__":
    main()
