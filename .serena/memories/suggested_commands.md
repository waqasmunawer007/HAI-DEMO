# Suggested Commands for HAI Dashboard Development

## Running the Application
```bash
streamlit run app.py
```
App opens at `http://localhost:8501`

## Installing Dependencies
```bash
pip install -r requirements.txt
```

## Authentication Setup
**Option A (Recommended for local dev):**
```bash
gcloud auth application-default login
```

**Option B (Service Account):**
Set `GOOGLE_APPLICATION_CREDENTIALS` in `.env` to point to service account JSON key in `credentials/`

## Testing Syntax
```bash
python3 -m py_compile app.py
python3 -m py_compile database/bigquery_client.py
python3 -m py_compile utils/data_processing.py
```

## Git Commands (Darwin/macOS)
```bash
git status
git add .
git commit -m "message"
git push
```

## Utility Commands (Darwin/macOS)
- `ls -la` - List files with details
- `cd <directory>` - Change directory
- `grep -r "pattern" .` - Search for pattern recursively
- `find . -name "*.py"` - Find Python files