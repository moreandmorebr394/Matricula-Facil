# Sistema Fácil (SF) — Sistema Educacional

Sistema de Gestão Educacional desenvolvido em **Python / Tkinter** com
arquitetura **MVC** (Models, Views, Controllers) e banco de dados
**MySQL** (com fallback automático para SQLite caso o MySQL não esteja
disponível).

---

## 1) Requisitos

* **Python 3.10 ou superior**
* **MySQL** (via WampServer ou MySQL Workbench) — opcional
  (se ausente, o sistema usa SQLite automaticamente)
* Bibliotecas listadas em `requirements.txt`:
  - `mysql-connector-python`
  - `bcrypt`
  - `Pillow`

---

## 2) Instalação

### 2.1) Clonar/baixar o projeto

Extraia o conteúdo deste ZIP em uma pasta de sua escolha.

### 2.2) Instalar dependências

```bash
pip install -r requirements.txt
```

### 2.3) Configurar o banco de dados (opcional, mas recomendado)

1. Inicie o **WampServer** (Windows) ou o serviço **MySQL** (Linux/Mac).
2. Verifique que o MySQL está escutando na porta padrão **3306**.
3. As credenciais padrão usadas pelo sistema estão em
   `configuracoes_admin/configuracao_banco.py`:

   ```python
   HOST_BANCO       = "localhost"
   PORTA_BANCO      = 3306
   USUARIO_BANCO    = "root"
   SENHA_BANCO      = ""             # padrão do WampServer
   NOME_BANCO       = "sistema_facil_sf"
   ```

   Edite-as caso seu MySQL use credenciais diferentes.

4. **Não é preciso criar o banco manualmente.** Na primeira execução,
   o sistema cria o banco `sistema_facil_sf` e todas as tabelas
   automaticamente.

> **Sem MySQL?** O sistema cai automaticamente em modo SQLite,
> criando o arquivo `banco_de_dados/sf_local.db`. Todas as
> funcionalidades continuam disponíveis.

---

## 3) Execução

A partir da raiz do projeto:

```bash
python principal.py
```

A tela de **login do aluno/cliente** será exibida.

---

## 4) Credenciais

### 4.1) Administrador (acesso ao Dashboard)

| Campo  | Valor                              |
|--------|-------------------------------------|
| E-mail | `admin@sistemafacil.pa.br`         |
| Senha  | `Admin@SF2026`                      |

> Para acessar o painel administrativo: na tela de login, clique em
> **"Acesso administrativo →"** (link discreto no rodapé).

### 4.2) Aluno / Cliente

Crie sua conta no botão **"Cadastre-se"** da tela de login.
O sistema gera automaticamente um e-mail institucional no formato:

```
aluno53756265@edu.pa.sistemafacil.br
```

---

## 5) Como alterar as credenciais administrativas

Edite o arquivo `configuracoes_admin/credenciais_admin.py`:

```python
EMAIL_ADMIN = "novo.admin@sistemafacil.pa.br"
NOME_ADMIN  = "Novo Administrador"
SENHA_ADMIN_HASH = b"$2b$12$..."   # gerar com bcrypt
```

Para gerar um novo hash de senha:

```python
import bcrypt
print(bcrypt.hashpw(b"NovaSenha@2026", bcrypt.gensalt(12)))
```

---

## 6) Estrutura do projeto

```
projeto_sf/
├── principal.py                    # Ponto de entrada
├── requirements.txt
├── LEIA-ME.md
│
├── recursos/                        # Logo SF e imagens
│
├── configuracoes_admin/             # Credenciais e config do banco
│   ├── credenciais_admin.py
│   └── configuracao_banco.py
│
├── banco_de_dados/                  # Camada de persistência
│   ├── conexao.py                   # Adaptador MySQL/SQLite
│   ├── inicializador.py             # Cria tabelas e popula dados
│   └── esquema.sql
│
├── modelos/                         # MODEL (regras de dados)
│   ├── modelo_usuario.py
│   ├── modelo_aluno.py              # Lead/Aluno (CRUD)
│   ├── modelo_venda.py
│   └── modelo_academico.py          # Turma, Aula, Frequência, Pagamento, Funil
│
├── controladores/                   # CONTROLLER (regras de negócio)
│   ├── controlador_autenticacao.py
│   ├── controlador_aluno.py
│   └── controlador_academico.py
│
├── utilitarios/                     # Helpers reutilizáveis
│   ├── criptografia.py              # bcrypt + criptografia simétrica
│   ├── validadores.py               # CPF, e-mail, data, telefone
│   ├── geradores.py                 # E-mail institucional, IDs
│   └── sessao.py
│
├── componentes/                     # Widgets visuais reutilizáveis
│   ├── tema.py                      # Cores, fontes, paleta
│   ├── botao_arredondado.py
│   ├── campo_entrada.py
│   ├── combo_arredondado.py
│   ├── logo_sf.py
│   ├── notificacoes.py              # Toasts e animações
│   └── painel_visual.py
│
└── telas/                           # VIEW (Tkinter)
    ├── tela_login.py
    ├── tela_registro.py
    ├── tela_login_admin.py          # Tela exclusiva do admin
    ├── tela_recuperacao_senha.py
    ├── tela_dashboard.py            # Janela principal
    └── paineis_dashboard/
        ├── painel_alunos.py         # Cadastro de Lead + Funil + Origem
        ├── painel_vendas.py
        ├── painel_pagamentos.py
        ├── painel_turmas.py
        ├── painel_aulas.py
        ├── painel_frequencia.py
        ├── painel_funil.py
        ├── painel_relatorios.py
        └── painel_configuracoes.py
```

---

## 7) Funcionalidades

### Tela de Login
* Login com e-mail/usuário institucional ou pessoal
* Botão "Continuar com Google" (mock, integração OAuth em produção)
* Lembrar-me, recuperação de senha, link para registro
* Acesso administrativo discreto no rodapé

### Tela de Registro
* Campos: nome completo, e-mail, repetir e-mail, senha, repetir senha,
  telefone (com formatação automática)
* Geração automática de e-mail institucional
  (`aluno12345678@edu.pa.sistemafacil.br`)
* Validação de força de senha (bcrypt cost=12)

### Dashboard Administrativo
Sidebar com 10 itens + botão Sair:
1. **Dashboard** — Visão geral
2. **Leads / Alunos** — Cadastro completo de leads:
   - Formulário com formatação automática (CPF, data, telefone)
   - **Jornada do Aluno** (8 etapas)
   - **Funil de Origem** (visualização gráfica)
   - **Pizza de origem dos leads**
   - Tabela de leads recentes com edição/exclusão (clique direito)
   - Resumo geral
3. **Vendas** — CRUD completo
4. **Pagamentos** — Vinculados a vendas
5. **Turmas** — CRUD completo
6. **Aulas** — Vinculadas a turma
7. **Frequência** — Chamada por aula com toggle de presença
8. **Funil de Origem** (badge "novo") — Editar números do funil
   (visitantes, leads, negociações, vendas, alunos ativos) e origens
9. **Relatórios** — Filtros por ano/trimestre/mês/semana, exportação CSV
10. **Configurações** — Foto do administrador, info do sistema

### Animações e UX
* Rastro do cursor com partículas amarelas
* Fade-in das janelas
* Notificações flutuantes (toasts) com auto-close em 2 segundos
* Hover suave em botões
* Bordas arredondadas em campos e botões (Canvas custom)

### Segurança
* Senhas com **bcrypt** (cost=12)
* Dados sensíveis (CPF) com criptografia simétrica reversível
* Credenciais administrativas FIXAS no arquivo `credenciais_admin.py`
  (não criáveis via UI)
* Bloqueio após 5 tentativas inválidas no login admin

---

## 8) Solução de problemas

### "Não foi possível conectar ao MySQL"
O sistema iniciará automaticamente em modo SQLite. Para usar MySQL:
1. Verifique se o WampServer está ativo (ícone verde).
2. Confira as credenciais em `configuracoes_admin/configuracao_banco.py`.

### Logo não aparece
O logo está em `recursos/logo_sf.png`. Caso esteja faltando, o sistema
exibe um logo gerado em runtime com as iniciais "SF".

### Erro ao instalar `bcrypt` ou `Pillow`
Em alguns sistemas Linux, instale primeiro:
```bash
sudo apt install python3-dev libffi-dev
```
Depois reexecute `pip install -r requirements.txt`.

---

## 9) Cursos cadastrados por padrão

* Técnico em Enfermagem
* Técnico em Segurança do Trabalho
* Técnico em Informática
* Técnico em Administração
* Técnico em Secretaria Escolar
* Administração
* Bombeiro Civil

---

## 10) Suporte

Sistema desenvolvido como projeto educacional. Para dúvidas, consulte
os comentários no código (todos os módulos estão documentados em
português) e a estrutura MVC organizada por pastas.

---

© 2026 Sistema Fácil — Educação Profissional. Todos os direitos
reservados.
