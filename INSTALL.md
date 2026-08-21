# Compilación — Guía de Radiocomunicaciones

El documento completo se genera desde una única fuente Markdown.

## Requisitos

- Python 3.10+
- WeasyPrint: `pip install weasyprint`
  (Linux: requiere `libpango-1.0-0 libpangocairo-1.0-0` del sistema)

## Flujo de trabajo

1. Editar la fuente: `FUENTE_RADIOCOMUNICACIONES.md`
2. Generar PDF y HTML:
   ```bash
   python3 build_pdf.py
   ```
3. Verificar integridad (claves 10, códigos Q/R, alfabeto OACI, estructura):
   ```bash
   python3 check_integrity.py
   ```

> El CI del repositorio ejecuta el control de integridad automáticamente en cada push.

## Publicación

- Sitio web: servido desde `main` vía GitHub Pages (`index.html` redirige a
  `manual_radiocomunicaciones.html`).
- QR imprimible: `docs/qr-tarjeta-imprimible.pdf`.
