# Leitor de equações

Este projeto oferece duas formas de reconhecer equações: pela câmera, com
Tesseract, ou a partir de um arquivo de imagem, com pix2tex. O pix2tex reconhece
fórmulas matemáticas e retorna código LaTeX; ele não é um OCR de texto geral.

## Imagem para LaTeX

Instale as dependências Python no ambiente virtual:

```bash
.venv/bin/pip install -r requirements.txt
```

Passe uma imagem com uma fórmula para o conversor:

```bash
.venv/bin/python image_to_latex.py formula.png
```

O resultado é impresso como código LaTeX. Na primeira execução, o pix2tex baixa
os arquivos do modelo automaticamente.

## Leitor pela câmera

O programa exibe o vídeo da câmera, reconhece texto com o Tesseract OCR e resolve
equações lineares com uma incógnita, como `2x + 3 = 7` ou `3(x-1)=6` (nesta
última, escreva `3x-3=6`, pois parênteses não são expandidos).

## Requisitos

- Python 3
- OpenCV para Python (`cv2`)
- Tesseract OCR instalado e disponível no `PATH`
- Uma câmera conectada
- Para conversão de imagens: dependências de `requirements.txt`

Execute a partir desta pasta usando o Python do ambiente virtual. O comando
`python camera_equation.py` pode selecionar o Python do sistema, que não tem
`cv2` instalado:

```bash
.venv/bin/python camera_equation.py
```

Para selecionar outra câmera:

```bash
.venv/bin/python camera_equation.py --camera 1
```

Pressione `q` ou `Esc` para fechar. O reconhecimento roda aproximadamente uma
vez por segundo; boa iluminação e texto com alto contraste ajudam o OCR.
# opencv_python
