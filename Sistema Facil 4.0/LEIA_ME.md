# Sistema Facil (SF) — Plataforma Educacional

Sistema completo de gestao educacional construido em **Python + Tkinter**, com banco de dados MySQL. Inclui pagina inicial vitrine, login/cadastro de alunos, area do aluno e dashboard administrativo CRM completo.

---

## ✨ Funcionalidades

### Para Visitantes / Alunos
- Pagina inicial com vitrine de cursos
- Login e cadastro com validacoes
- Area do aluno: perfil, cursos, calendario, materiais, notas, mensagens, certificados, financeiro
- Email institucional gerado automaticamente: `aluno{8digitos}@edu.pa.sistemafacil.br`

### Para Administrador
- Acesso restrito (login fixo)
- Dashboard com KPIs, graficos e lista de leads recentes
- CRUD completo: Leads, Vendas, Pagamentos, Turmas, Aulas, Frequencia
- Funil de conversao com analise de origens
- Relatorios com filtros por periodo
- Configuracoes do perfil e dados da instituicao
- Sistema de notificacoes em tempo real

---

## 📋 Requisitos

- **Python 3.9+**
- **WampServer** (com MySQL ativo)
- **MySQL Workbench** (opcional, para visualizar/manipular o banco)

---

## 🚀 Instalacao

### 1. Clone ou descompacte o projeto

```bash
cd projeto_sf
```

### 2. Instale as dependencias Python

```bash
pip install -r requisitos.txt
```

### 3. Configure o banco MySQL (opcional)

Se quiser usar MySQL/WampServer:

1. Inicie o WampServer (icone deve ficar verde)
2. Abra o phpMyAdmin (`http://localhost/phpmyadmin`)
3. Crie um banco chamado `sistema_facil` (ou deixe que o sistema crie automaticamente)
4. Se usar credenciais diferentes do padrao (root sem senha), copie `.env.exemplo` para `.env` e ajuste

**Schema completo:** veja `banco_de_dados/esquema.sql` (pode importar no MySQL Workbench).

### 4. Execute o sistema

```bash
python principal.py
```

A pagina inicial sera aberta. Voce pode:
- **Cadastrar-se** como aluno ou visitante
- **Fazer login** com a conta criada
- Clicar em **"Acesso Administrativo"** (no canto inferior do login) para entrar no painel admin

---

## 🔐 Credenciais Administrativas Padrao

| Campo | Valor |
|-------|-------|
| Email | `admin@sistemafacil.pa.br` |
| Senha | `admin123` |

> ⚠️ **IMPORTANTE:** Para alterar a senha do administrador, edite o arquivo `configuracoes_admin/credenciais_admin.py`. A senha pode ser alterada pelo proprio dashboard (em Configuracoes), e ficara salva no banco com hash bcrypt.

### Como gerar um novo hash bcrypt para a senha admin

```python
import bcrypt
nova_senha = "minha_nova_senha"
hash_gerado = bcrypt.hashpw(nova_senha.encode("utf-8"), bcrypt.gensalt())
print(hash_gerado.decode("utf-8"))
# Cole o resultado em SENHA_ADMIN_HASH dentro de credenciais_admin.py
```

---

## 📁 Estrutura do Projeto

```
projeto_sf/
├── principal.py                    # Ponto de entrada
├── requisitos.txt                  # Dependencias Python
├── .env.exemplo                    # Modelo de configuracao
├── LEIA_ME.md                      # Este arquivo
│
├── configuracoes_admin/            # Credenciais do admin
│   └── credenciais_admin.py
│
├── banco_de_dados/                 # Conexao e schema
│   ├── conexao.py                  # MySQL
│   ├── inicializar.py              # Cria tabelas
│   ├── esquema.sql                 # SQL para Workbench
│   └── sistema_facil.db            # (criado em runtime)
│
├── componentes/                    # UI reusavel
│   ├── cores.py                    # Paleta hex 6 digitos
│   ├── logo_sf.py                  # Logo SF (Canvas vetorial)
│   ├── botao_moderno.py            # Botao bordas arredondadas
│   ├── campo_entrada.py            # Input com label/icone/senha
│   ├── notificacao.py              # Toast auto-destrutivo (2s)
│   ├── card.py                     # Card reusavel
│   ├── mascaras.py                 # CPF/Data/Telefone/Dinheiro
│   └── cursor_customizado.py       # Cursor personalizado
│
├── app/
│   ├── modelo/                     # Camada Modelo (CRUD)
│   │   ├── modelo_usuario.py
│   │   ├── modelo_lead.py
│   │   ├── modelo_venda.py
│   │   ├── modelo_pagamento.py
│   │   ├── modelo_turma.py
│   │   ├── modelo_aula.py
│   │   └── modelo_geral.py
│   │
│   ├── controlador/                # Camada Controlador
│   │   ├── controlador_autenticacao.py
│   │   ├── controlador_dashboard.py
│   │   └── listas_constantes.py
│   │
│   └── visao/                      # Camada Visao (Tkinter)
│       ├── tela_pagina_inicial.py
│       ├── tela_login.py
│       ├── tela_registro.py
│       ├── tela_login_admin.py
│       ├── tela_area_aluno.py
│       ├── tela_dashboard.py
│       └── paginas_dashboard/      # 10 secoes do admin
│           ├── pagina_inicio.py
│           ├── pagina_leads.py
│           ├── pagina_vendas.py
│           ├── pagina_pagamentos.py
│           ├── pagina_turmas.py
│           ├── pagina_aulas.py
│           ├── pagina_frequencia.py
│           ├── pagina_funil.py
│           ├── pagina_relatorios.py
│           └── pagina_configuracoes.py
│
└── recursos/imagens/               # Imagens estaticas (opcional)
```

---

## 🎨 Paleta de Cores

| Cor | Hex | Uso |
|-----|-----|-----|
| Azul Primario | `#3C507D` | Logo SF, botoes principais |
| Azul Escuro | `#112250` | Textos escuros |
| Amarelo Vibrante | `#F5C518` | Destaques, CTA |
| Amarelo Dourado | `#E0C58F` | Logo SF |
| Verde Sucesso | `#10B981` | Estados positivos |
| Vermelho Erro | `#EF4444` | Erros, exclusoes |

---

## 🔧 Resolucao de Problemas

### O sistema nao abre / da erro de import
- Verifique se esta na raiz do projeto: `cd projeto_sf`
- Confirme Python 3.9+: `python --version`
- Reinstale dependencias: `pip install -r requisitos.txt --upgrade`

---

## 📝 Notas Tecnicas

- **MVC:** Codigo separado em Modelo (banco), Controlador (logica) e Visao (Tkinter)
- **Sem HTML/CSS/JS:** Tudo desenhado em Tkinter usando Canvas para elementos visuais avancados
- **Logo vetorial:** Desenhado em Canvas (sem PNG, sem fundo recortado)
- **Cursor customizado:** Configurado por widget para nao bloquear cliques
- **Mascaras automaticas:** CPF, data, telefone e dinheiro aplicadas em tempo real
- **Hex 6 digitos:** Todas as cores em formato compativel com Tkinter
- **Notificacoes toast:** Auto-destruem apos 2 segundos
- **Cores e fontes:** Centralizadas em `componentes/cores.py`

---

## 📄 Licenca

Sistema desenvolvido para fins educacionais. Livre para uso e modificacao.

---

**Sistema Facil — Educacao que Transforma 🎓**
