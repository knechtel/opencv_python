# Webcam OCR — OpenCV + Tesseract

import cv2
import numpy as np
import pytesseract
import os
import textwrap
from datetime import datetime

# Configuração do Tesseract
pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"

IDIOMA = "por"
PASTA = "capturas"

os.makedirs(PASTA, exist_ok=True)


def corrigir_perspectiva(imagem):
    """Detecta o papel e corrige sua perspectiva."""

    cinza = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

    # Reduz ruído e detecta bordas
    suavizada = cv2.GaussianBlur(cinza, (5, 5), 0)
    bordas = cv2.Canny(suavizada, 50, 150)

    contornos, _ = cv2.findContours(
        bordas,
        cv2.RETR_LIST,
        cv2.CHAIN_APPROX_SIMPLE
    )

    contornos = sorted(
        contornos,
        key=cv2.contourArea,
        reverse=True
    )

    for contorno in contornos[:10]:

        perimetro = cv2.arcLength(contorno, True)

        aproximacao = cv2.approxPolyDP(
            contorno,
            0.02 * perimetro,
            True
        )

        # O papel deve possuir quatro cantos
        if len(aproximacao) == 4:

            pontos = aproximacao.reshape(4, 2).astype("float32")

            # Ordenar os quatro cantos
            soma = pontos.sum(axis=1)
            diferenca = np.diff(pontos, axis=1).flatten()

            superior_esquerdo = pontos[np.argmin(soma)]
            inferior_direito = pontos[np.argmax(soma)]
            superior_direito = pontos[np.argmin(diferenca)]
            inferior_esquerdo = pontos[np.argmax(diferenca)]

            ordenados = np.array([
                superior_esquerdo,
                superior_direito,
                inferior_direito,
                inferior_esquerdo
            ], dtype="float32")

            largura = max(
                np.linalg.norm(
                    ordenados[0] - ordenados[1]
                ),
                np.linalg.norm(
                    ordenados[2] - ordenados[3]
                )
            )

            altura = max(
                np.linalg.norm(
                    ordenados[0] - ordenados[3]
                ),
                np.linalg.norm(
                    ordenados[1] - ordenados[2]
                )
            )

            largura = int(largura)
            altura = int(altura)

            if largura < 100 or altura < 100:
                continue

            destino = np.array([
                [0, 0],
                [largura - 1, 0],
                [largura - 1, altura - 1],
                [0, altura - 1]
            ], dtype="float32")

            matriz = cv2.getPerspectiveTransform(
                ordenados,
                destino
            )

            documento = cv2.warpPerspective(
                imagem,
                matriz,
                (largura, altura)
            )

            return documento

    # Se não encontrar o papel, usa a imagem original
    return imagem


def preparar_imagem(imagem):
    """Melhora a imagem para reconhecimento de texto."""

    cinza = cv2.cvtColor(
        imagem,
        cv2.COLOR_BGR2GRAY
    )

    # Aumentar resolução para letras pequenas
    altura, largura = cinza.shape

    if largura < 1800:
        fator = 1800 / largura

        cinza = cv2.resize(
            cinza,
            None,
            fx=fator,
            fy=fator,
            interpolation=cv2.INTER_CUBIC
        )

    # Melhorar contraste local
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )

    contraste = clahe.apply(cinza)

    return contraste


def reconhecer_texto(imagem):
    """Reconhece texto usando diferentes configurações."""

    documento = corrigir_perspectiva(imagem)

    processada = preparar_imagem(documento)

    cv2.imshow("Documento processado", processada)

    # Testar diferentes modos de segmentação
    configuracoes = [
        "--oem 3 --psm 6",
        "--oem 3 --psm 4"
    ]

    melhor_texto = ""
    melhor_confianca = -1

    for config in configuracoes:

        dados = pytesseract.image_to_data(
            processada,
            lang=IDIOMA,
            config=config,
            output_type=pytesseract.Output.DICT
        )

        confiancas = [
            float(c)
            for c, palavra in zip(
                dados["conf"],
                dados["text"]
            )
            if palavra.strip() and float(c) >= 0
        ]

        confianca = (
            sum(confiancas) / len(confiancas)
            if confiancas else 0
        )

        texto = pytesseract.image_to_string(
            processada,
            lang=IDIOMA,
            config=config
        )

        if confianca > melhor_confianca:
            melhor_confianca = confianca
            melhor_texto = texto

    print(f"Confiança média: {melhor_confianca:.1f}%")

    return melhor_texto.strip(), documento


def salvar_resultado(imagem, texto):

    nome = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    caminho_imagem = f"{PASTA}/{nome}.jpg"
    caminho_texto = f"{PASTA}/{nome}.txt"

    cv2.imwrite(caminho_imagem, imagem)

    with open(
        caminho_texto,
        "w",
        encoding="utf-8"
    ) as arquivo:

        arquivo.write(texto)

    print(f"Imagem: {caminho_imagem}")
    print(f"Texto: {caminho_texto}")


def main():

    webcam = cv2.VideoCapture(0)

    webcam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
    webcam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
    webcam.set(cv2.CAP_PROP_AUTOFOCUS, 1)

    if not webcam.isOpened():
        print("Erro ao abrir webcam.")
        return

    print("C = Capturar")
    print("Q = Sair")

    while True:

        sucesso, frame = webcam.read()

        if not sucesso:
            break

        cv2.imshow("Webcam OCR", frame)

        tecla = cv2.waitKey(1) & 0xFF

        if tecla == ord("c"):

            texto, documento = reconhecer_texto(frame)

            print("\n===== TEXTO RECONHECIDO =====")
            print(texto)
            print("=============================")

            salvar_resultado(documento, texto)

        elif tecla == ord("q"):
            break

    webcam.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()



