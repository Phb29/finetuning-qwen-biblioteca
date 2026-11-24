"""Faz uma pergunta livre ao modelo ajustado (ou ao original, com --original).

Uso:  uv run python scripts/perguntar.py "O leitor quer pagar a multa"
"""

import argparse

from comum import PASTA_ADAPTADOR, carregar, responder

parser = argparse.ArgumentParser()
parser.add_argument("pergunta")
parser.add_argument("--original", action="store_true", help="usa o modelo sem o adaptador")
args = parser.parse_args()

tokenizer, modelo = carregar(None if args.original else PASTA_ADAPTADOR)
print(responder(tokenizer, modelo, [args.pergunta])[0])
