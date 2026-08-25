# Презентация Gridec для Janitza

Собирается кодом, не руками. Правки вносятся в `gen.js`, потом пересборка.

```bash
node gen.js
```

На выходе — `Gridec_for_Janitza.pptx` рядом со скриптом.

## Что откуда

* Палитра скопирована из `build.py`, `PALETTES['blue']`: бумага `#F6F1E9`,
  плашка `#0D2440`, акцент `#2E5E99` на светлом и `#7BA4D0` на тёмном.
* Логотип — не шрифт, а картинка: `wm_*.png`. Departure Mono на машине
  получателя не стоит, поэтому слово нарисовано заранее скриптом
  `wordmark.py` по правилу шапки сайта (кегль кратен 11, трекинг 3/22 кегля).
* Шрифты в самом файле — Arial и Consolas. Они есть в любом Office, поэтому
  вёрстка не поедет у Janitza. Overused Grotesk и Departure Mono для этого
  не годятся: их надо было бы вшивать.
* Снимки — из `../img/`.

## Страница для просмотра

`page.py` собирает `view.html` — все слайды картинками, шрифты сайта внутри
файла, ничего наружу не тянется. Сначала выгрузить слайды в папку `hi/`, потом
запустить скрипт.

## Выгрузка слайдов в PNG

LibreOffice на машине нет, но есть PowerPoint. Из PowerShell:

```powershell
$app = New-Object -ComObject PowerPoint.Application
$p = $app.Presentations.Open("...\Gridec_for_Janitza.pptx", $true, $false, $false)
$p.Export("...\hi", "PNG", 1920, 1080)
$p.Close(); $app.Quit()
```

Схему самого файла проверяет `scripts/office/validate.py` из скилла pptx.
