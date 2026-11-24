"""Partes compartilhadas: dados, prompt, carregamento do modelo e correção das respostas."""

import json
import unicodedata
from pathlib import Path

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

RAIZ = Path(__file__).resolve().parent.parent
DADOS = RAIZ / "dados"
RESULTADOS = RAIZ / "resultados"
PASTA_ADAPTADOR = RAIZ / "saida" / "adaptador-lora"

MODELO_BASE = "Qwen/Qwen2.5-0.5B-Instruct"
SEMENTE = 3407

TELAS: list[str] = json.loads((DADOS / "telas.json").read_text(encoding="utf-8"))

# O mesmo prompt de sistema é usado no modelo original e no ajustado,
# para a comparação ser justa: os dois recebem a lista de telas.
PROMPT_SISTEMA = (
    "Você é o assistente de um sistema de biblioteca. "
    "Leia o pedido do funcionário e indique somente a tela mais adequada, "
    "no formato: Abra a tela <nome da tela>.\n"
    "Telas disponíveis: " + "; ".join(TELAS) + "."
)


def ler_jsonl(nome: str) -> list[dict]:
    linhas = (DADOS / nome).read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in linhas if l.strip()]


def resposta_esperada(tela: str) -> str:
    return f"Abra a tela {tela}."


def mensagens(pergunta: str, tela: str | None = None) -> list[dict]:
    msgs = [
        {"role": "system", "content": PROMPT_SISTEMA},
        {"role": "user", "content": pergunta},
    ]
    if tela is not None:
        msgs.append({"role": "assistant", "content": resposta_esperada(tela)})
    return msgs


def carregar(adaptador: Path | None = None):
    """Carrega o tokenizer e o modelo (opcionalmente com o adaptador LoRA)."""
    torch.manual_seed(SEMENTE)
    tokenizer = AutoTokenizer.from_pretrained(MODELO_BASE)
    modelo = AutoModelForCausalLM.from_pretrained(MODELO_BASE, dtype=torch.float32)
    if adaptador is not None:
        from peft import PeftModel

        modelo = PeftModel.from_pretrained(modelo, str(adaptador))
    modelo.eval()
    return tokenizer, modelo


@torch.no_grad()
def responder(tokenizer, modelo, perguntas: list[str], lote: int = 8) -> list[str]:
    """Gera a resposta (decodificação gulosa, sem sorteio) para cada pergunta."""
    tokenizer.padding_side = "left"
    saidas: list[str] = []
    for i in range(0, len(perguntas), lote):
        textos = [
            tokenizer.apply_chat_template(mensagens(p), tokenize=False, add_generation_prompt=True)
            for p in perguntas[i : i + lote]
        ]
        entrada = tokenizer(textos, return_tensors="pt", padding=True)
        gerado = modelo.generate(
            **entrada,
            max_new_tokens=32,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
        )
        novos = gerado[:, entrada["input_ids"].shape[1] :]
        saidas += [t.strip() for t in tokenizer.batch_decode(novos, skip_special_tokens=True)]
    return saidas


def _normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return " ".join(sem_acento.lower().split())


def tela_citada(resposta: str) -> str | None:
    """Devolve a primeira tela (da lista oficial) que aparece na resposta."""
    texto = _normalizar(resposta)
    achadas = [(texto.find(_normalizar(t)), t) for t in TELAS if _normalizar(t) in texto]
    return min(achadas)[1] if achadas else None
