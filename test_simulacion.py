#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de simulación para probar el monitor sin Playwright.
Simula vacantes y envía notificaciones a Telegram.
"""

import os
import json
import datetime as dt
from urllib import request as urlrequest, parse as urlparse


def normaliza(texto: str) -> str:
    """Minúsculas y sin acentos, para comparar de forma robusta."""
    if not texto:
        return ""
    t = texto.lower()
    reemplazos = {"á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ñ": "n"}
    for a, b in reemplazos.items():
        t = t.replace(a, b)
    return " ".join(t.split())


def enviar_telegram(texto: str) -> None:
    """Envía mensaje a Telegram."""
    token = os.environ.get("TELEGRAM_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    
    if not (token and chat_id):
        print("[telegram] ⚠️ TELEGRAM_TOKEN/CHAT_ID no configurados")
        print(f"[telegram] Mensaje que se hubiera enviado:\n{texto}\n")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    datos = urlparse.urlencode({"chat_id": chat_id, "text": texto}).encode()
    
    try:
        with urlrequest.urlopen(urlrequest.Request(url, data=datos), timeout=20) as r:
            r.read()
        print("[telegram] ✅ Mensaje enviado a Telegram")
    except Exception as e:
        print(f"[telegram] ❌ Error: {e}")


def main():
    print("=" * 60)
    print("SIMULACIÓN DEL MONITOR DE VACANTES")
    print("=" * 60)
    
    # Vacantes simuladas (como si vinieran de la web)
    vacantes_simuladas = [
        "Departamento: Cauca | Municipio: Popayán | Área: Tecnología e informática | Vacante: Ingeniero de Sistemas",
        "Departamento: Nariño | Municipio: Pasto | Área: Primaria | Vacante: Docente Primaria",
        "Departamento: Huila | Municipio: Neiva | Área: Tecnología e informática | Vacante: Técnico en TI",
        "Departamento: Putumayo | Municipio: Puerto Asís | Área: Primaria | Vacante: Docente Primaria",
    ]
    
    print(f"\n📋 Se leyeron {len(vacantes_simuladas)} vacantes de la página\n")
    for i, v in enumerate(vacantes_simuladas, 1):
        print(f"{i}. {v}")
    
    # Filtrar por criterios
    TARGET_DEPARTAMENTOS = ["Cauca", "Nariño", "Huila", "Putumayo"]
    TARGET_AREAS = ["Tecnología e informática", "Primaria"]
    
    interesantes = []
    for v in vacantes_simuladas:
        t = normaliza(v)
        dep_ok = any(normaliza(d) in t for d in TARGET_DEPARTAMENTOS)
        area_ok = any(normaliza(a) in t for a in TARGET_AREAS)
        if dep_ok and area_ok:
            interesantes.append(v)
    
    print(f"\n✅ Vacantes que coinciden con criterios: {len(interesantes)}\n")
    for i, v in enumerate(interesantes, 1):
        print(f"{i}. {v}")
    
    # Simular reporte horario
    fecha = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if interesantes:
        mensaje = f"[Reporte Horario] {fecha}\n✅ Se encontraron {len(interesantes)} vacante(s) que coinciden"
    else:
        mensaje = f"[Reporte Horario] {fecha}\n❌ No se encontraron vacantes que coincidan"
    
    print(f"\n📱 Mensaje a enviar por Telegram:\n")
    print(mensaje)
    print("\n" + "=" * 60)
    
    # Intentar enviar
    print("\nIntentando enviar mensaje...")
    enviar_telegram(mensaje)
    
    print("\n✅ Simulación completada")


if __name__ == "__main__":
    main()
