# ---- Stage 1: build the three frontend apps ----
FROM node:20-slim AS frontend-build
WORKDIR /build

COPY Landing/package*.json Landing/
RUN cd Landing && npm ci

COPY Frontend/package*.json Frontend/
RUN cd Frontend && npm ci

COPY OfficerFrontend/package*.json OfficerFrontend/
RUN cd OfficerFrontend && npm ci

COPY Landing/ Landing/
RUN cd Landing && npm run build

COPY Frontend/ Frontend/
RUN cd Frontend && npm run build

COPY OfficerFrontend/ OfficerFrontend/
RUN cd OfficerFrontend && npm run build

# ---- Stage 2: runtime image ----
FROM python:3.12-slim
WORKDIR /app

COPY Backend/requirements.txt Backend/requirements.txt
RUN pip install --no-cache-dir -r Backend/requirements.txt

COPY Backend/ Backend/
COPY ai_service/ ai_service/

# Only the built output from stage 1 — no node_modules, no source maps clutter.
COPY --from=frontend-build /build/Landing/dist Landing/dist
COPY --from=frontend-build /build/Frontend/dist Frontend/dist
COPY --from=frontend-build /build/OfficerFrontend/dist OfficerFrontend/dist

WORKDIR /app/Backend
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
