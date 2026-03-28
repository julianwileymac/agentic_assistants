import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent
nb = json.loads((ROOT / '36_unsloth_finetuning.ipynb').read_text(encoding='utf-8'))

