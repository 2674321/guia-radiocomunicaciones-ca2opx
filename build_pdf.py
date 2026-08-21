#!/usr/bin/env python3
"""Genera el PDF A4 desde el HTML maestro.

Uso: python3 build_pdf.py [entrada.html] [salida.pdf]
Sin argumentos usa los nombres de la edición original.
"""

import sys

from weasyprint import HTML

SRC = sys.argv[1] if len(sys.argv) > 1 else "manual_radiocomunicaciones.html"
OUT = sys.argv[2] if len(sys.argv) > 2 else "GUIA_RADIOCOMUNICACIONES.pdf"

HTML(filename=SRC).write_pdf(OUT)
print(f"PDF generado: {OUT}")
