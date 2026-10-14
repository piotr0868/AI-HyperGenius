FROM python@sha256:a6e34c598f2467ed0e9a8d349809fcd8b5c603269512df273a0bb1784edc11b1
RUN mkdir /data && chown 65534:65534 /data
WORKDIR /app
COPY --chown=65534:65534 main.py .
COPY --chown=65534:65534 web/ ./web/
USER 65534:65534
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
VOLUME ["/data"]
EXPOSE 8000
CMD ["python", "main.py", "--host", "0.0.0.0", "--port", "8000", "--db", "/data/activities.sqlite3"]
