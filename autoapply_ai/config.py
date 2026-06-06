from pathlib import Path
DATA_DIR = Path("data")
OUTPUT_DIR = Path("outputs")
DB_PATH = DATA_DIR / "autoapply.db"
DEMO_SESSION_ID = "demo-user"
DATA_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)
