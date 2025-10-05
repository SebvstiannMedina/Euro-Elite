from pathlib import Path
text = Path("EuroElite/Main/templates/Taller/perfil.html").read_text(encoding="utf-8")
for target in ['La letra K solo puede usarse como ', 'El RUT debe contener 9 caracteres', 'El código postal debe tener 7 dígitos.', 'Ingresa 7 dígitos.']:
    idx = text.find(target)
    print(target, idx)
    if idx != -1:
        snippet = text[idx:idx+len(target)+30]
        print(repr(snippet))
