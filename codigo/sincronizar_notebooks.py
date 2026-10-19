"""Regenera los cuadernos .ipynb a partir de los scripts .py con celdas `# %%`.

Los scripts son la fuente de verdad (se versionan y se ejecutan como programa);
el cuaderno es una vista cómoda para leer la narrativa y correr celda a celda.
Se genera SIN salidas, para que ninguna tabla con datos de Postobón quede
embebida en el repositorio.

Uso::

    python codigo/sincronizar_notebooks.py            # todos los scripts con celdas
    python codigo/sincronizar_notebooks.py eda_fase1  # solo uno
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# La consola de Windows usa cp1252 por defecto y rompe con "→" (mismo ajuste que comun.py).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

CODIGO = Path(__file__).resolve().parent
MARCA = re.compile(r"^# %%(?P<md> \[markdown\])?\s*$")


def celdas_de(script: Path) -> list[dict]:
    celdas, actual, tipo = [], [], None

    def cerrar():
        if tipo is None:
            return
        texto = "\n".join(actual).strip("\n")
        if tipo == "markdown":
            # Quita el prefijo "# " de cada línea (y deja las líneas "#" vacías).
            texto = "\n".join(re.sub(r"^# ?", "", l) for l in texto.splitlines())
        if texto.strip():
            lineas = texto.splitlines(keepends=True)
            celdas.append({"cell_type": tipo, "metadata": {}, "source": lineas,
                           **({"outputs": [], "execution_count": None} if tipo == "code" else {})})

    for linea in script.read_text(encoding="utf-8").splitlines():
        m = MARCA.match(linea)
        if m:
            cerrar()
            actual, tipo = [], ("markdown" if m.group("md") else "code")
        elif tipo is not None:
            actual.append(linea)
    cerrar()
    return celdas


def escribir_notebook(script: Path) -> Path:
    nb = {
        "cells": celdas_de(script),
        "metadata": {
            "kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4, "nbformat_minor": 5,
    }
    destino = script.with_suffix(".ipynb")
    destino.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
    return destino


if __name__ == "__main__":
    nombres = sys.argv[1:]
    scripts = [CODIGO / f"{n.removesuffix('.py')}.py" for n in nombres] if nombres else [
        p for p in CODIGO.glob("*.py") if p.name != Path(__file__).name and celdas_de(p)
    ]
    for s in scripts:
        d = escribir_notebook(s)
        print(f"{s.name} → {d.name} ({len(celdas_de(s))} celdas)")
