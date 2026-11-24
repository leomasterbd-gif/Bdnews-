FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN useradd --create-home --uid 10001 atm
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=atm:atm atm ./atm
COPY --chown=atm:atm config ./config
COPY --chown=atm:atm dashboard ./dashboard
COPY --chown=atm:atm data/historical ./data/historical
COPY --chown=atm:atm scripts ./scripts
COPY --chown=atm:atm .claude ./.claude
RUN mkdir -p /app/reports /app/data && chown -R atm:atm /app/reports /app/data
USER atm
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8000/api/health',timeout=4).status==200 else 1)"
CMD ["python", "-m", "uvicorn", "--factory", "atm.api.server:create_app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers"]
