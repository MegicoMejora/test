Online Banking System

## Run locally
1. Create virtual env and install:
python -m venv venv
source venv/bin/activate # or venv\Scripts\activate on Windows
pip install -r requirements.txt

2. Create `.env` (see .env.example)
3. Run locally:
python create_tables.py
python app.py