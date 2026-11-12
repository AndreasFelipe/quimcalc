from pathlib import Path
from shutil import copytree


raiz = Path(__file__).resolve().parent
copytree(
    raiz / "static",
    raiz / "public" / "static",
    dirs_exist_ok=True
)
