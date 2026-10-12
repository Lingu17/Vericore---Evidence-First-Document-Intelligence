FROM node:22-alpine AS frontend
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 CHROMA_PATH=/data/chroma HF_HOME=/opt/models EMBEDDING_BACKEND=onnx
WORKDIR /app
COPY backend/requirements*.txt ./
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu \
    && pip install --no-cache-dir -r requirements-onnx.txt
RUN python -c "from huggingface_hub import hf_hub_download; [hf_hub_download('sentence-transformers/all-MiniLM-L6-v2', f) for f in ['tokenizer.json', 'onnx/model.onnx']]"
COPY backend/app ./app
COPY backend/sample_documents ./sample_documents
COPY --from=frontend /frontend/dist ./static
RUN useradd --create-home vericore && mkdir -p /data/chroma && chown -R vericore:vericore /data /app /opt/models
USER vericore
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
