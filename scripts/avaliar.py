"""Mede a taxa de acerto nas perguntas de TESTE (que não entraram no treino).

Uso:
  uv run python scripts/avaliar.py            -> modelo original
  uv run python scripts/avaliar.py --lora     -> modelo com o adaptador treinado
  uv run python scripts/avaliar.py --comparar -> junta os dois resultados em resultados/comparacao.md
"""

import argparse
import json
import time

from comum import PASTA_ADAPTADOR, RESULTADOS, carregar, ler_jsonl, responder, tela_citada


def avaliar(usar_lora: bool) -> None:
    nome = "lora" if usar_lora else "original"
    tokenizer, modelo = carregar(PASTA_ADAPTADOR if usar_lora else None)
    teste = ler_jsonl("teste.jsonl")

    inicio = time.time()
    respostas = responder(tokenizer, modelo, [t["pergunta"] for t in teste])
    linhas = []
    for item, resposta in zip(teste, respostas):
        citada = tela_citada(resposta)
        linhas.append(
            {
                "pergunta": item["pergunta"],
                "esperada": item["tela"],
                "resposta": resposta,
                "tela_citada": citada,
                "acertou": citada == item["tela"],
            }
        )
    acertos = sum(l["acertou"] for l in linhas)
    resumo = {
        "modelo": nome,
        "perguntas": len(linhas),
        "acertos": acertos,
        "taxa_acerto": round(100 * acertos / len(linhas), 1),
        "tempo_segundos": round(time.time() - inicio, 1),
        "respostas": linhas,
    }
    RESULTADOS.mkdir(exist_ok=True)
    (RESULTADOS / f"avaliacao_{nome}.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    for l in linhas:
        print(("OK  " if l["acertou"] else "ERRO") + f" | {l['pergunta']} -> {l['resposta']}")
    print(f"\n{nome}: {acertos}/{len(linhas)} acertos ({resumo['taxa_acerto']}%)")


def comparar() -> None:
    orig = json.loads((RESULTADOS / "avaliacao_original.json").read_text(encoding="utf-8"))
    lora = json.loads((RESULTADOS / "avaliacao_lora.json").read_text(encoding="utf-8"))

    def celula(texto: str) -> str:
        return texto.replace("|", "/").replace("\n", " ")

    md = [
        "# Comparação: modelo original x modelo ajustado com LoRA",
        "",
        f"Perguntas de teste (fora do treino): **{orig['perguntas']}**",
        "",
        "| Modelo | Acertos | Taxa de acerto |",
        "|---|---|---|",
        f"| Qwen2.5-0.5B-Instruct original | {orig['acertos']}/{orig['perguntas']} | {orig['taxa_acerto']}% |",
        f"| Qwen2.5-0.5B-Instruct + LoRA | {lora['acertos']}/{lora['perguntas']} | {lora['taxa_acerto']}% |",
        "",
        "## Resposta a resposta",
        "",
        "| Pergunta | Tela esperada | Original | Com LoRA |",
        "|---|---|---|---|",
    ]
    for o, l in zip(orig["respostas"], lora["respostas"]):
        md.append(
            f"| {celula(o['pergunta'])} | {o['esperada']} | "
            f"{'✅' if o['acertou'] else '❌'} {celula(o['resposta'])} | "
            f"{'✅' if l['acertou'] else '❌'} {celula(l['resposta'])} |"
        )
    (RESULTADOS / "comparacao.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md[:9]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lora", action="store_true", help="avalia o modelo com o adaptador treinado")
    parser.add_argument("--comparar", action="store_true", help="gera resultados/comparacao.md")
    args = parser.parse_args()
    comparar() if args.comparar else avaliar(args.lora)
