import os
replacements = {
    'Cingil Tasarim': 'Cingil Tasarim',
    'CINGIL TASARIM': 'CINGIL TASARIM',
    'cingiltasarim': 'cingiltasarim',
    '905434818591': '905434818591',
    '+905434818591': '+905434818591',
    '05434818591': '05434818591'
}

root = r'c:\Users\Asus\Desktop\cingilweb'
for subdir, dirs, files in os.walk(root):
    for fname in files:
        path = os.path.join(subdir, fname)
        try:
            with open(path, 'rb') as f:
                data = f.read()
            try:
                text = data.decode('utf-8')
            except Exception:
                continue
            changed = False
            for a,b in replacements.items():
                if a in text:
                    text = text.replace(a,b)
                    changed = True
            if changed:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(text)
                print('Patched', path)
        except Exception as e:
            print('Skip', path, e)
print('Done')
