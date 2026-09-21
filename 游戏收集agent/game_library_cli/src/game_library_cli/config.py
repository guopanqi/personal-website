from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

DEFAULT_CSV_PATH = PROJECT_ROOT / "game-library.csv"
DEFAULT_TASTE_PATH = PROJECT_ROOT / "taste.txt"
DEFAULT_DOCTOR_REVIEWS_PATH = PROJECT_ROOT / "game-library-doctor-reviews.json"
DEFAULT_SYNC_STATE_PATH = PROJECT_ROOT / "gamer520-sync-state.json"
