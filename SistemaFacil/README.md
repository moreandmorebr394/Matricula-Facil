# 🎓 Sistema Fácil (SF) — Plataforma Educacional

Sistema de cadastro e login para plataforma educacional, desenvolvido em Python com Tkinter.

---

## 📁 Estrutura do Projeto

```
SistemaFacil/
├── principal.py          ← Arquivo principal (execute este)
├── configuracoes.py      ← Cores, fontes e constantes
├── requisitos.txt        ← Dependências do projeto
├── README.md             ← Este arquivo
├── assets/
│   └── logo_sf.png       ← Logo do Sistema Fácil
├── componentes/
│   ├── __init__.py
│   ├── logo.py           ← Gerador da logo SF
│   ├── widgets.py        ← Campos, botões e links customizados
│   └── animacoes.py      ← Formas flutuantes, linhas pontilhadas
└── telas/
    ├── __init__.py
    ├── registro.py       ← Tela de cadastro (Sign Up)
    └── login.py          ← Tela de login (Sign In)
```

---

## 🚀 Como Rodar

### 1. Pré-requisitos
- Python 3.8 ou superior
- Tkinter (já vem com Python no Windows/Mac)
- Pillow (para imagens)

### 2. Instalar dependências

```bash
pip install Pillow
```

> No Linux, pode ser necessário instalar o tkinter separadamente:
> ```bash
> sudo apt-get install python3-tk
> ```

### 3. Executar

```bash
cd SistemaFacil
python principal.py
```

Ou no VSCode: abra `principal.py` e pressione `F5` ou `Ctrl+F5`.

---

## 🎨 Identidade Visual

| Elemento         | Cor        |
|------------------|------------|
| Azul escuro      | `#112250`  |
| Azul médio       | `#3C507D`  |
| Dourado          | `#E0C58F`  |
| Fundo formulário | `#FAFAFA`  |
| Branco           | `#FFFFFF`  |

---

## ✨ Funcionalidades

- Tela de Registro com validação de campos
- Tela de Login com opção Google
- Navegação entre telas (Entrar ↔ Cadastrar-se)
- Animações: formas geométricas flutuantes, linhas pontilhadas
- Efeito fade-in na abertura
- Hover nos botões e campos
- Logo SF com chapéu de formatura
- Design responsivo (redimensionável)

---

## ⚠️ Observações

- A logo é carregada do arquivo `assets/logo_sf.png`. Se não encontrada, uma versão é gerada automaticamente.
- Fontes: o sistema usa Segoe UI (Windows), SF Pro (Mac) ou DejaVu Sans (Linux) automaticamente.
- Este é um protótipo visual — os dados de cadastro/login não são salvos em banco de dados.
- Para integração real, seria necessário adicionar: banco de dados, hash de senhas, API de autenticação Google, etc.
