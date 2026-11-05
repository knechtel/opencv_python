#!/usr/bin/env python3
"""Converte uma imagem de uma fórmula matemática para código LaTeX usando pix2tex."""

import argparse
import sys
from pathlib import Path

from PIL import Image, UnidentifiedImageError
from pix2tex.cli import LatexOCR


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("imagem", type=Path, help="arquivo de imagem com uma fórmula matemática")
    args = parser.parse_args()

    if not args.imagem.is_file():
        print(f"Arquivo não encontrado: {args.imagem}", file=sys.stderr)
        return 1

    try:
        with Image.open(args.imagem) as image:
            formula = LatexOCR()(image)
    except (UnidentifiedImageError, OSError) as error:
        print(f"Não foi possível abrir a imagem: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Falha ao reconhecer a fórmula: {error}", file=sys.stderr)
        return 1

    print(formula)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
