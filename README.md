# Chhattisgarh Multilingual RAG — Starter Project

Starter scaffold for a Chhattisgarhi/Hindi/English RAG project. It does not auto-approve or ingest every archive record. Review source permissions and record quality first.

## Prerequisites
- Python 3.11+
- Node.js 20+ and npm

## Run backend (Windows PowerShell)
```powershell
cd backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
Open http://127.0.0.1:8000/docs.

## Run frontend (second terminal)
```powershell
cd frontend
npm install
npm run dev
```
Open the URL shown by Vite, usually http://localhost:5173.

## Audit your dataset archive
From `backend`:
```powershell
python scripts/audit_zip.py "C:\path\to\chhattisgarhi_all_created_datasets_and_toolkits_v1(1).zip" --outdir audit_output
```
This creates a JSON report and CSV inventory. It does not validate legal permission, factual accuracy, or linguistic correctness.

## Next milestones
1. Inspect audit results and map records to one schema.
2. Verify provenance, reuse permission, and factual quality.
3. Prepare reviewed/approved JSONL; keep AI-generated language examples separate until reviewed.
4. Chunk records, generate multilingual embeddings, and build FAISS index.
5. Connect an LLM provider with source-grounded prompting.
6. Test English, Hindi, and Chhattisgarhi.
7. Add Sarvam speech-to-text/text-to-speech after text RAG works.

`GET /health` checks the API. `POST /chat` is intentionally a placeholder until retrieval and an LLM are connected. Copy `.env.example` to `.env` only when configuring providers; never commit or share API keys.
