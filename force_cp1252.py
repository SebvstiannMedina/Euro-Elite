from pathlib import Path
path = Path("EuroElite/Main/templates/Taller/perfil.html")
raw = path.read_bytes()
text = raw.decode('cp1252')
path.write_text(text, encoding='utf-8')
