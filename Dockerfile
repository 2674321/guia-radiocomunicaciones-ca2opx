FROM python:3.12-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz-subset0 fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir weasyprint

WORKDIR /docs

ENTRYPOINT ["weasyprint"]
CMD ["--help"]
