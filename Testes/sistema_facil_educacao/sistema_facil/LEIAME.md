# Sistema Fácil Educação — CRM de Alunos
## Dashboard em Tkinter

### Estrutura de Arquivos

```
sistema_facil/
│
├── main.py                      ← Ponto de entrada, rode este arquivo
├── requisitos.txt               ← Dependências (pip install -r requisitos.txt)
│
├── assets/
│   └── logo_sf.png              ← Logo do sistema (SF)
│
├── componentes/
│   ├── __init__.py
│   ├── sidebar.py               ← Sidebar lateral com navegação
│   ├── header.py                ← Barra superior com perfil e notificações
│   └── grafico_funil.py         ← Gráficos: funil de vendas e pizza
│
├── telas/
│   ├── __init__.py
│   └── dashboard.py             ← Tela principal do CRM (3 colunas)
│
└── utils/
    ├── __init__.py
    ├── tema.py                  ← Cores, fontes e constantes visuais
    └── helpers.py               ← Componentes reutilizáveis (cards, botões...)
```

### Como executar

1. **Instalar dependências:**
   ```bash
   pip install -r requisitos.txt
   ```

2. **Rodar o sistema:**
   ```bash
   python main.py
   ```

### Requisitos
- Python 3.9+
- Tkinter (já vem com o Python no Windows/Mac)
  - Linux: `sudo apt install python3-tk`
- Pillow (para a logo): `pip install Pillow`

### Resolução recomendada
1366×768 ou superior
