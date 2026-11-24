"""Gera resultados/resultado.png (curva de loss + acerto antes/depois).

Uso:  uv run --with matplotlib python scripts/grafico.py
"""

import json

import matplotlib.pyplot as plt

from comum import RESULTADOS

log = json.loads((RESULTADOS / "treino_log.json").read_text(encoding="utf-8"))
orig = json.loads((RESULTADOS / "avaliacao_original.json").read_text(encoding="utf-8"))
lora = json.loads((RESULTADOS / "avaliacao_lora.json").read_text(encoding="utf-8"))

fig, (a, b) = plt.subplots(1, 2, figsize=(11, 4.2))

passos = [h["passo"] for h in log["historico"]]
a.plot(passos, [h["loss"] for h in log["historico"]], color="#2a6fdb", linewidth=2, marker="o", markersize=3)
a.set_title("Loss durante o treino (só CPU)")
a.set_xlabel("passo")
a.set_ylabel("loss")
a.grid(alpha=0.3)

taxas = [orig["taxa_acerto"], lora["taxa_acerto"]]
barras = b.bar(["Original", "Com LoRA"], taxas, color=["#9aa5b1", "#2a9d6f"], width=0.55)
for barra, taxa, r in zip(barras, taxas, [orig, lora]):
    b.text(barra.get_x() + barra.get_width() / 2, taxa + 2, f"{taxa:.1f}%\n({r['acertos']}/{r['perguntas']})",
           ha="center", va="bottom", fontsize=11)
b.set_ylim(0, 110)
b.set_title("Acerto em perguntas que NÃO estavam no treino")
b.set_ylabel("% de acerto")
b.grid(axis="y", alpha=0.3)

fig.suptitle("Qwen2.5-0.5B-Instruct + LoRA: assistente de biblioteca", fontsize=13, fontweight="bold")
fig.tight_layout()
fig.savefig(RESULTADOS / "resultado.png", dpi=150)
print("ok")
