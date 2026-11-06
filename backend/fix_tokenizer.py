from pathlib import Path
import re

path = Path("app/main.py")
source = path.read_text(encoding="utf-8")

pattern = r'def tokenize\(text: str\) -> list\[str\]:.*?(?=\ndef canonical_url\()'

replacement = '''def tokenize(text: str) -> list[str]:
    """Tokenize Latin and Devanagari text while preserving vowel marks."""
    tokens = []
    current = []

    for char in (text or "").casefold():
        category = __import__("unicodedata").category(char)

        if category.startswith(("L", "N")):
            current.append(char)
        elif category.startswith("M") and current:
            current.append(char)
        else:
            if current:
                tokens.append("".join(current))
                current = []

    if current:
        tokens.append("".join(current))

    return tokens


'''

updated, count = re.subn(pattern, lambda _: replacement, source, count=1, flags=re.DOTALL)

if count != 1:
    raise SystemExit("ERROR: tokenize() was not replaced. File unchanged.")

path.write_text(updated, encoding="utf-8")
print("SUCCESS: tokenize() replaced in app/main.py")
