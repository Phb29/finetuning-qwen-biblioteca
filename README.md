# Fine-tuning de um Qwen com LoRA, numa CPU sem placa de vídeo

Projeto de estudo: ensinar um modelo de linguagem pequeno a **indicar a tela certa de um sistema de biblioteca** a partir de um pedido em português, como faria um assistente de atendimento.

Exemplo: *"O leitor veio entregar o livro que pegou semana passada"* → **Abra a tela Devolução de livros.**

O treino foi feito **de verdade, num PC comum** (AMD Ryzen 5 5600GT, 32 GB de RAM, **sem GPU dedicada**), e levou cerca de **9 minutos**.

![Resultado](resultados/resultado.png)

## Resultado

Avaliação em **24 perguntas que não entraram no treino**:

| Modelo | Acertos | Taxa de acerto |
|---|---|---|
| Qwen2.5-0.5B-Instruct original | 4/24 | 16,7% |
| Qwen2.5-0.5B-Instruct + LoRA | 18/24 | **75,0%** |

Os dois modelos recebem **o mesmo prompt**, com a lista das 12 telas. A diferença está só no treino.

Mesmo com a lista na mão, o modelo original errava quase tudo e chegava a **inventar telas que não existem**, como "Consulta de multas". Depois do ajuste, ele passa a seguir o vocabulário do sistema.

A tabela resposta a resposta está em [resultados/comparacao.md](resultados/comparacao.md).

### O que ainda erra (e por quê)

Os 6 erros que sobraram estão nas telas mais "vizinhas" entre si:

- "avisar quando o livro voltar" (Reserva) foi confundido com Consulta de empréstimos;
- "quitar o que deve" (Multas) foi confundido com Devolução;
- "lista de quem está com livro vencido" (Relatório de atrasos) foi confundido com Consulta de empréstimos.

Com só 74 exemplos de treino, isso é esperado. O próximo passo natural seria mais exemplos dessas telas, e não ajustar o modelo olhando para o teste.

## Como funciona

| Conceito | O que é aqui |
|---|---|
| **Fine-tuning** | adaptar um modelo já treinado a uma tarefa específica |
| **LoRA** | congela os ~494 milhões de pesos originais e treina só pequenas matrizes extras: **8,8 milhões de parâmetros (1,75%)** |
| **SFT** (ajuste supervisionado) | cada exemplo é uma conversa: pergunta do usuário → resposta desejada |
| **Máscara de loss** | o erro só é calculado nos tokens da resposta, então o modelo aprende a responder e não a repetir a pergunta |

Configuração usada: LoRA `r=16`, `alpha=32`, em todas as projeções de atenção e MLP; 3 épocas, lote 8, `lr=2e-4`, 30 passos, float32 na CPU.

O resultado é um **adaptador de 34 MB** que se encaixa no modelo original. Ele não é uma cópia de 1 GB do modelo.

## Estrutura

```
dados/
  telas.json          12 telas do sistema fictício
  treino.jsonl        74 exemplos (pergunta -> tela)
  teste.jsonl         24 perguntas separadas, nunca vistas no treino
scripts/
  comum.py            prompt, carregamento do modelo e correção das respostas
  treinar.py          treino LoRA com laço PyTorch simples (sem Trainer)
  avaliar.py          taxa de acerto antes/depois e tabela comparativa
  perguntar.py        faz uma pergunta livre ao modelo
  grafico.py          gera resultados/resultado.png
colab/
  qlora_qwen3b_colab.ipynb   versão QLoRA (4 bits) com Qwen2.5-3B para GPU no Google Colab
resultados/           logs do treino, avaliações e gráfico
```

## Como rodar

Precisa só do [uv](https://docs.astral.sh/uv/). Ele instala o Python 3.12 e o PyTorch para CPU.

```bash
uv sync
uv run python scripts/avaliar.py              # 1. mede o modelo original
uv run python scripts/treinar.py              # 2. treina o adaptador (~9 min numa CPU de 6 núcleos)
uv run python scripts/avaliar.py --lora       # 3. mede o modelo ajustado
uv run python scripts/avaliar.py --comparar   # 4. gera resultados/comparacao.md
uv run python scripts/perguntar.py "O leitor quer pagar a multa"
```

O adaptador treinado também está disponível na aba **Releases** do repositório. Descompacte em `saida/adaptador-lora/` para pular o treino.

## E o Qwen 3B com QLoRA?

**QLoRA** é LoRA com o modelo base carregado em **4 bits**, o que reduz muito a memória de **GPU**. Numa CPU isso não ajuda, porque a quantização em 4 bits depende de CUDA.

Por isso, o projeto tem dois caminhos:

- **CPU (o que foi executado):** Qwen2.5-**0.5B** + LoRA em float32;
- **GPU (notebook pronto, não executado por mim):** Qwen2.5-**3B** + QLoRA com [Unsloth](https://github.com/unslothai/unsloth) no Google Colab, usando os mesmos dados e a mesma avaliação. Abra `colab/qlora_qwen3b_colab.ipynb` no Colab com GPU ativada.

## Limitações honestas

- Os dados são **sintéticos e poucos** (74 de treino e 24 de teste). O objetivo é aprender o fluxo, não ter um produto.
- 24 perguntas de teste é uma amostra pequena: cada pergunta vale 4,2 pontos percentuais.
- A correção é automática: conta como acerto se a **primeira tela citada** na resposta for a esperada.

## Licença

MIT
