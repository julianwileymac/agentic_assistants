import json
from pathlib import Path

def md(t):
    return {"cell_type": "markdown", "metadata": {}, "source": t.splitlines(keepends=True)}

def code(t):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": t.splitlines(keepends=True),
    }

META = {
    "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
    "language_info": {"name": "python", "version": "3.11.0"},
}
p = Path('notebooks/36_unsloth_finetuning.ipynb')
nb = json.loads(p.read_text(encoding="utf-8"))
