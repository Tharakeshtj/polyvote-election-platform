# PolyVote hosted demo: builds the React app, then runs the FastAPI service that also serves it.
FROM node:20-slim AS web
WORKDIR /web
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
WORKDIR /app
COPY requirements-hosted.txt ./
RUN pip install --no-cache-dir -r requirements-hosted.txt
COPY *.py ./
COPY verification ./verification
COPY --from=web /web/dist ./frontend/dist
# Public demo defaults: seed a demo election at start, require the emailed code, and show the code on screen
# (a public demo has no mailbox the evaluator can open). Override any of these as environment variables.
ENV HOSTED_DEMO=true OTP_REQUIRED=true OTP_DEMO_HINT=true
EXPOSE 8000
CMD ["sh", "-c", "python -m uvicorn server:app --host 0.0.0.0 --port ${PORT:-8000}"]
