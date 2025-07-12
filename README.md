# libreviz

Party visuals in libre office!

setup:

```
uv sync
source .venv/bin/activate
```

run:

```
python src/boxes
```

## dev

```
ruff format . && ruff check --fix --unsafe-fixes . && mypy .
```

## links

https://help.libreoffice.org/latest/en-US/text/sbasic/shared/01020000.html?DbPAR=BASIC
https://github.com/socsieng/sendkeys
https://github.com/BlueM/cliclick