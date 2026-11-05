#!/usr/bin/env python3
"""Lê equações lineares na imagem da câmera e mostra a solução em tempo real."""

import argparse
import re
import subprocess
import sys
import time

import cv2


TERM = re.compile(r"([+-]?)\s*(\d*\.?\d*)\s*(x?)", re.IGNORECASE)


def parse_side(side: str) -> tuple[float, float]:
    """Retorna (coeficiente de x, constante) para uma soma de termos."""
    side = side.replace(" ", "").replace("−", "-").replace("×", "x")
    if not side or side[0] not in "+-":
        side = "+" + side
    pos = 0
    a = b = 0.0
    for match in TERM.finditer(side):
        if match.start() != pos:
            raise ValueError("expressão não reconhecida")
        sign_text, number, variable = match.groups()
        if not number and not variable:
            raise ValueError("termo vazio")
        sign = -1.0 if sign_text == "-" else 1.0
        value = float(number) if number else 1.0
        if variable:
            a += sign * value
        else:
            b += sign * value
        pos = match.end()
    if pos != len(side):
        raise ValueError("expressão não reconhecida")
    return a, b


def solve_equation(text: str) -> str | None:
    text = text.lower().replace(" ", "").replace("−", "-")
    text = text.replace("×", "x").replace("х", "x")
    text = text.replace("＝", "=")
    if text.count("=") != 1:
        return None
    try:
        left_a, left_b = parse_side(text.split("=")[0])
        right_a, right_b = parse_side(text.split("=")[1])
    except (ValueError, IndexError):
        return None
    coefficient, constant = left_a - right_a, right_b - left_b
    if abs(coefficient) < 1e-10:
        return "sem solução" if abs(constant) > 1e-10 else "infinitas soluções"
    answer = constant / coefficient
    return f"x = {answer:g}"


def recognize(frame) -> str:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    ok, encoded = cv2.imencode(".png", binary)
    if not ok:
        return ""
    result = subprocess.run(
        ["tesseract", "stdin", "stdout", "--psm", "6", "-c",
         "tessedit_char_whitelist=0123456789.xX+-=()"],
        input=encoded.tobytes(), capture_output=True, check=False,
    )
    return result.stdout.decode("utf-8", errors="ignore").strip().replace("\n", " ")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--camera", type=int, default=0, help="índice da câmera (padrão: 0)")
    args = parser.parse_args()

    camera = cv2.VideoCapture(args.camera)
    if not camera.isOpened():
        print(f"Não foi possível abrir a câmera {args.camera}.", file=sys.stderr)
        return 1

    recognized = "Aponte para uma equação (ex.: 2x + 3 = 7)"
    solution = ""
    last_ocr = 0.0
    print("Pressione q ou Esc para sair.")
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Não foi possível ler a imagem da câmera.", file=sys.stderr)
                return 1
            now = time.monotonic()
            if now - last_ocr >= 1.0:
                recognized = recognize(frame) or "Não foi possível reconhecer a equação"
                solution = solve_equation(recognized) or "Equação não identificada"
                last_ocr = now

            cv2.rectangle(frame, (0, 0), (frame.shape[1], 92), (20, 20, 20), -1)
            cv2.putText(frame, f"Texto: {recognized[:75]}", (16, 35),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Resultado: {solution}", (16, 72),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (80, 255, 100), 2, cv2.LINE_AA)
            cv2.imshow("Leitor de equacoes de primeiro grau", frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
