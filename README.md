setup Instructions:

- `cp .env.example .env`
- inside mysql create medisync database first
- run mysql database and fill the necessaity .env fields
- enable python virtual environment using `python3 -m venv venv` and activate it
- `pip install -r requirements.txt`
- `alembic upgrade head`
- `python3 main.py`

# for development?
- formatting -> ruff_format, ruff_organize_imports
