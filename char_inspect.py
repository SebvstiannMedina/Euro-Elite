from pathlib import Path
text = Path("EuroElite/Main/templates/Taller/perfil.html").read_text(encoding="utf-8")
idx = text.find('El c')
for i in range(idx, idx+40):
    ch = text[i]
    print(i-idx, repr(ch), ord(ch))
    if ch == '\n':
        break
