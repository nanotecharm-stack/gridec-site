# -*- coding: utf-8 -*-
"""Give both pages a real head: description, theme colour, icons, sharing tags."""
import io

p = 'build.py'
s = io.open(p, encoding='utf-8').read()

old = """def wrap(tokens, body, extra_head=''):
    return ('<!doctype html>\\n<html lang="%s">\\n<head>\\n<meta charset="utf-8">\\n'
            '<meta name="viewport" content="width=device-width, initial-scale=1">\\n'
            '<title>%s</title>\\n%s</head>\\n<body>\\n%s\\n</body>\\n</html>\\n'
            % (tokens['LANG'], tokens['TITLE'], extra_head, body))"""

new = '''def wrap(tokens, body, extra_head=''):
    """The description reuses the page's own opening paragraph, so nothing is invented."""
    desc = re.sub(r'<[^>]+>', '', tokens['HERO_P'])
    if len(desc) > 175:
        desc = desc[:175].rsplit(' ', 1)[0] + '\\u2026'
    head = ''.join([
        '<meta charset="utf-8">\\n',
        '<meta name="viewport" content="width=device-width, initial-scale=1">\\n',
        '<title>', tokens['TITLE'], '</title>\\n',
        '<meta name="description" content="', desc, '">\\n',
        '<meta name="theme-color" content="#C8603D">\\n',
        '<link rel="icon" href="../favicon.svg" type="image/svg+xml">\\n',
        '<link rel="apple-touch-icon" href="../apple-touch-icon.png">\\n',
        '<meta property="og:type" content="website">\\n',
        '<meta property="og:title" content="', tokens['TITLE'], '">\\n',
        '<meta property="og:description" content="', desc, '">\\n',
        '<meta property="og:locale" content="',
        'hy_AM' if tokens['LANG'] == 'hy' else 'en_US', '">\\n',
    ])
    return ('<!doctype html>\\n<html lang="%s">\\n<head>\\n%s%s</head>\\n<body>\\n%s\\n</body>\\n</html>\\n'
            % (tokens['LANG'], head, extra_head, body))'''

assert old in s, 'wrap() not found verbatim'
s = s.replace(old, new)
io.open(p, 'w', encoding='utf-8').write(s)
print('meta head wired:', 'og:description' in s)
