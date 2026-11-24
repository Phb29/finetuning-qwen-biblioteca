"""Treina um adaptador LoRA no Qwen2.5-0.5B-Instruct usando só a CPU.

Uso:  uv run python scripts/treinar.py
"""

import json
import random
import time

import torch
from peft import LoraConfig, get_peft_model

from comum import PASTA_ADAPTADOR, RESULTADOS, SEMENTE, carregar, ler_jsonl, mensagens

EPOCAS = 3
LOTE = 8
TAXA_APRENDIZADO = 2e-4


def montar_exemplo(tokenizer, item: dict) -> dict:
    """Tokeniza a conversa e marca com -100 tudo que NÃO é a resposta do assistente.

    Assim o erro (loss) só é calculado sobre a resposta: o modelo aprende a responder,
    não a repetir a pergunta.
    """
    prompt = tokenizer.apply_chat_template(
        mensagens(item["pergunta"]), tokenize=False, add_generation_prompt=True
    )
    completo = tokenizer.apply_chat_template(
        mensagens(item["pergunta"], item["tela"]), tokenize=False
    )
    assert completo.startswith(prompt), "o template de chat mudou o início da conversa"
    ids_prompt = tokenizer(prompt, add_special_tokens=False)["input_ids"]
    ids = tokenizer(completo, add_special_tokens=False)["input_ids"]
    rotulos = [-100] * len(ids_prompt) + ids[len(ids_prompt) :]
    return {"input_ids": ids, "labels": rotulos}


def juntar_lote(exemplos: list[dict], pad_id: int) -> dict:
    maior = max(len(e["input_ids"]) for e in exemplos)
    ids, rotulos, mascara = [], [], []
    for e in exemplos:
        falta = maior - len(e["input_ids"])
        ids.append(e["input_ids"] + [pad_id] * falta)
        rotulos.append(e["labels"] + [-100] * falta)
        mascara.append([1] * len(e["input_ids"]) + [0] * falta)
    return {
        "input_ids": torch.tensor(ids),
        "labels": torch.tensor(rotulos),
        "attention_mask": torch.tensor(mascara),
    }


def main() -> None:
    random.seed(SEMENTE)
    tokenizer, modelo = carregar()

    config = LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM",
    )
    modelo = get_peft_model(modelo, config)
    modelo.print_trainable_parameters()

    treino = [montar_exemplo(tokenizer, item) for item in ler_jsonl("treino.jsonl")]
    otimizador = torch.optim.AdamW(
        [p for p in modelo.parameters() if p.requires_grad], lr=TAXA_APRENDIZADO, weight_decay=0.01
    )
    passos_total = EPOCAS * ((len(treino) + LOTE - 1) // LOTE)
    agendador = torch.optim.lr_scheduler.LambdaLR(
        otimizador, lambda passo: 1 - passo / passos_total
    )

    historico = []
    modelo.train()
    inicio = time.time()
    passo = 0
    for epoca in range(1, EPOCAS + 1):
        random.shuffle(treino)
        for i in range(0, len(treino), LOTE):
            lote = juntar_lote(treino[i : i + LOTE], tokenizer.pad_token_id)
            perda = modelo(**lote).loss
            perda.backward()
            torch.nn.utils.clip_grad_norm_(modelo.parameters(), 1.0)
            otimizador.step()
            agendador.step()
            otimizador.zero_grad()
            passo += 1
            segundos = round(time.time() - inicio, 1)
            historico.append({"passo": passo, "epoca": epoca, "loss": round(perda.item(), 4), "segundos": segundos})
            print(f"época {epoca}  passo {passo}/{passos_total}  loss {perda.item():.4f}  ({segundos}s)")

    PASTA_ADAPTADOR.mkdir(parents=True, exist_ok=True)
    modelo.save_pretrained(str(PASTA_ADAPTADOR))
    tokenizer.save_pretrained(str(PASTA_ADAPTADOR))

    RESULTADOS.mkdir(exist_ok=True)
    (RESULTADOS / "treino_log.json").write_text(
        json.dumps(
            {
                "exemplos_treino": len(treino),
                "epocas": EPOCAS,
                "lote": LOTE,
                "taxa_aprendizado": TAXA_APRENDIZADO,
                "passos": passo,
                "tempo_total_segundos": round(time.time() - inicio, 1),
                "historico": historico,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"\nAdaptador salvo em {PASTA_ADAPTADOR}")


if __name__ == "__main__":
    main()
