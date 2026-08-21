#!/usr/bin/env python3
"""Genera el PDF A4 de la Guía de Radiocomunicaciones desde el HTML maestro."""
from weasyprint import HTML

SRC = "manual_radiocomunicaciones.html"
OUT = "GUIA_RADIOCOMUNICACIONES.pdf"

HTML(filename=SRC).write_pdf(OUT)
print(f"PDF generado: {OUT}")
