# Comparação: modelo original x modelo ajustado com LoRA

Perguntas de teste (fora do treino): **24**

| Modelo | Acertos | Taxa de acerto |
|---|---|---|
| Qwen2.5-0.5B-Instruct original | 4/24 | 16.7% |
| Qwen2.5-0.5B-Instruct + LoRA | 18/24 | 75.0% |

## Resposta a resposta

| Pergunta | Tela esperada | Original | Com LoRA |
|---|---|---|---|
| Acabaram de chegar livros novos que a escola comprou. | Cadastro de livros | ❌ Abra a tela Consulta de leitores. | ✅ Abra a tela Cadastro de livros. |
| O título de um livro foi cadastrado com erro de digitação. | Cadastro de livros | ✅ Abra a tela Cadastro de livros. | ✅ Abra a tela Cadastro de livros. |
| Quero cadastrar a escritora Clarice Lispector no sistema. | Cadastro de autores | ✅ Abra a tela Cadastro de autores. | ✅ Abra a tela Cadastro de autores. |
| Falta a data de nascimento de um autor. | Cadastro de autores | ✅ Abra a tela Cadastro de autores. | ✅ Abra a tela Cadastro de autores. |
| Uma moça nova no bairro quer se tornar leitora da biblioteca. | Cadastro de leitores | ❌ Abra a tela Consulta de leitores. | ✅ Abra a tela Cadastro de leitores. |
| O leitor casou e mudou o sobrenome. | Cadastro de leitores | ❌ Abra a tela Consulta de leitores. | ✅ Abra a tela Cadastro de leitores. |
| Preciso achar o cadastro de um leitor pelo telefone. | Consulta de leitores | ❌ Abra a tela Cadastro de leitores. | ✅ Abra a tela Consulta de leitores. |
| Esse aluno é leitor da biblioteca? | Consulta de leitores | ✅ Abra a tela Consulta de leitores. | ✅ Abra a tela Consulta de leitores. |
| Tem algum livro de receitas aqui? | Catálogo do acervo | ❌ Abra a tela Cadastro de livros. | ✅ Abra a tela Catálogo do acervo. |
| Onde fica o livro O Pequeno Príncipe? | Catálogo do acervo | ❌ Abra a tela Cadastro de livros. | ✅ Abra a tela Catálogo do acervo. |
| A Júlia quer levar dois livros emprestados. | Empréstimo de livros | ❌ Abra a tela Consulta de empréstimos. | ✅ Abra a tela Empréstimo de livros. |
| Vou liberar um livro para um leitor agora. | Empréstimo de livros | ❌ Abra a tela Consulta de leitores. | ✅ Abra a tela Empréstimo de livros. |
| O menino está devolvendo o gibi. | Devolução de livros | ❌ Abra a tela Consulta de empréstimos. | ✅ Abra a tela Devolução de livros. |
| Recebi de volta o livro de História. | Devolução de livros | ❌ Abra a tela Catálogo do acervo. | ❌ Abra a tela Empréstimo de livros. |
| Quais livros a professora Carla está com ela agora? | Consulta de empréstimos | ❌ Abra a tela Consulta de leitores. | ✅ Abra a tela Consulta de empréstimos. |
| Quero saber quem pegou o livro de Física. | Consulta de empréstimos | ❌ Abra a tela Consulta de leitores. | ✅ Abra a tela Consulta de empréstimos. |
| Uma leitora quer ser avisada quando o livro voltar. | Reserva de livros | ❌ Abra a tela Consulta de leitores. | ❌ Abra a tela Consulta de empréstimos. |
| Quero segurar o último exemplar para um professor. | Reserva de livros | ❌ Abra a tela Consulta de empréstimos. | ❌ Abra a tela Empréstimo de livros. |
| O leitor veio quitar o que deve. | Cobrança de multas | ❌ Abra a tela Consulta de empréstimos. | ❌ Abra a tela Devolução de livros. |
| Quanto custa a multa desse aluno? | Cobrança de multas | ❌ Abra a tela Consulta de multas. | ✅ Abra a tela Cobrança de multas. |
| Um usuário quer saber quais leitores têm livros atrasados. | Relatório de empréstimos em atraso | ❌ Abra a tela Consulta de empréstimos. | ❌ Abra a tela Consulta de empréstimos. |
| Quero mandar e-mail para todo mundo que está com livro vencido. | Relatório de empréstimos em atraso | ❌ Abra a tela Consulta de empréstimos. | ❌ Abra a tela Reserva de livros. |
| Quantos livros de poesia temos comparado com os de suspense? | Relatório de livros por categoria | ❌ Abra a tela Consulta de empréstimos. | ✅ Abra a tela Relatório de livros por categoria. |
| Quero um resumo do acervo separado por tema. | Relatório de livros por categoria | ❌ Abra a tela Catálogo do acervo. | ✅ Abra a tela Relatório de livros por categoria. |
