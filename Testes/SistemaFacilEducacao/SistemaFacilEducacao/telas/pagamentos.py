"""Tela de Pagamentos: registrar e listar pagamentos."""
import tkinter as tk
from typing import Callable

from componentes.botao import BotaoPrimario, BotaoSucesso
from componentes.campo_entrada import CampoEntrada, CampoSelecao
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from dados.modelos import Pagamento


FORMAS = ["PIX", "Boleto", "Cartao Credito", "Cartao Debito",
          "Dinheiro", "Transferencia"]


class TelaPagamentos(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self.filtro_status = tk.StringVar(value="Todos")
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)
        wrapper.grid_columnconfigure(0, weight=1, uniform="p")
        wrapper.grid_columnconfigure(1, weight=2, uniform="p")
        wrapper.grid_rowconfigure(1, weight=1)

        # Indicadores
        ind = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        ind.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        for i in range(4):
            ind.grid_columnconfigure(i, weight=1, uniform="i")

        recebido = sum(p.valor for p in self.banco.pagamentos)
        pendentes = sum(v.valor for v in self.banco.vendas if not v.pago)
        qtd_pagos = len(self.banco.pagamentos)
        qtd_pend = sum(1 for v in self.banco.vendas if not v.pago)

        self._mini(ind, "Recebido", self._reais(recebido), "💰",
                   Cores.BOTAO_SUCESSO).grid(
            row=0, column=0, sticky="nsew", padx=(0, 6))
        self._mini(ind, "Pendente", self._reais(pendentes), "⏳",
                   Cores.NOTIF_AVISO_FUNDO).grid(
            row=0, column=1, sticky="nsew", padx=6)
        self._mini(ind, "Pagamentos", str(qtd_pagos), "✓",
                   Cores.BOTAO_PRIMARIO).grid(
            row=0, column=2, sticky="nsew", padx=6)
        self._mini(ind, "Em aberto", str(qtd_pend), "!",
                   Cores.BOTAO_PERIGO).grid(
            row=0, column=3, sticky="nsew", padx=(6, 0))

        # ----- Form registrar pagamento -----
        form_card = CardComCabecalho(wrapper, titulo="Registrar Pagamento",
                                     icone="💳")
        form_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        c = form_card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)

        self.campo_aluno = CampoEntrada(c, rotulo="Nome do aluno",
                                        obrigatorio=True,
                                        placeholder="Ex.: Joao da Silva")
        self.campo_aluno.pack(fill="x", pady=4)

        self.campo_valor = CampoEntrada(c, rotulo="Valor (R$)",
                                        obrigatorio=True, placeholder="0,00")
        self.campo_valor.pack(fill="x", pady=4)

        self.campo_forma = CampoSelecao(c, rotulo="Forma de pagamento",
                                        opcoes=FORMAS, obrigatorio=True)
        self.campo_forma.pack(fill="x", pady=4)

        self.campo_comp = CampoEntrada(c, rotulo="Comprovante / Codigo",
                                       placeholder="Numero da transacao")
        self.campo_comp.pack(fill="x", pady=4)

        botoes = tk.Frame(c, bg=Cores.CARD_FUNDO)
        botoes.pack(fill="x", pady=(14, 0))
        BotaoSucesso(botoes, texto="Confirmar Pagamento",
                     comando=self._registrar, largura=200).pack(side="right")

        # ----- Lista de pagamentos -----
        lista_card = CardComCabecalho(wrapper,
                                      titulo="Historico de Pagamentos",
                                      icone="📜")
        lista_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        ct = lista_card.conteudo()
        ct.configure(bg=Cores.CARD_FUNDO)

        # filtros
        topo = tk.Frame(ct, bg=Cores.CARD_FUNDO)
        topo.pack(fill="x", pady=(0, 8))
        tk.Label(topo, text="Filtrar:", bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_SECUNDARIO,
                 font=Fontes.PEQUENO).pack(side="left", padx=(0, 8))
        for op in ["Todos", "Pagos", "Pendentes"]:
            tk.Radiobutton(topo, text=op, variable=self.filtro_status,
                           value=op, bg=Cores.CARD_FUNDO,
                           fg=Cores.TEXTO_SECUNDARIO,
                           selectcolor=Cores.CARD_FUNDO,
                           activebackground=Cores.CARD_FUNDO,
                           font=Fontes.PEQUENO,
                           cursor="hand2",
                           command=self._renderizar).pack(side="left",
                                                          padx=4)

        self.area_lista = tk.Frame(ct, bg=Cores.CARD_FUNDO)
        self.area_lista.pack(fill="both", expand=True)
        self._renderizar()

    def _mini(self, parent, rotulo, valor, icone, cor):
        card = Card(parent, padding=16)
        c = card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)
        tk.Label(c, text=icone, bg=Cores.CARD_FUNDO,
                 fg=cor, font=(Fontes.FAMILIA, 18, "bold")
                 ).pack(anchor="w")
        tk.Label(c, text=valor, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.NUMERO_MEDIO).pack(anchor="w", pady=(6, 0))
        tk.Label(c, text=rotulo, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO).pack(anchor="w")
        return card

    def _reais(self, valor):
        return ("R$ " + f"{valor:,.2f}".replace(",", "X")
                .replace(".", ",").replace("X", "."))

    def _registrar(self):
        nome = self.campo_aluno.obter()
        valor_txt = self.campo_valor.obter().replace(",", ".").strip()
        forma = self.campo_forma.obter()
        if not nome:
            self.mostrar_notificacao("Informe o nome do aluno.", "ERRO")
            return
        if not forma:
            self.mostrar_notificacao("Selecione a forma de pagamento.",
                                     "ERRO")
            return
        try:
            valor = float(valor_txt)
        except ValueError:
            self.mostrar_notificacao("Valor invalido.", "ERRO")
            return

        p = Pagamento(nome_aluno=nome, valor=valor,
                      forma_pagamento=forma,
                      comprovante=self.campo_comp.obter())
        self.banco.adicionar_pagamento(p)
        self.mostrar_notificacao(
            f"Pagamento de {self._reais(valor)} confirmado.",
            "SUCESSO", titulo="Pagamento registrado")
        for c in (self.campo_aluno, self.campo_valor, self.campo_comp):
            c.limpar()
        self._renderizar()

    def _renderizar(self):
        for w in self.area_lista.winfo_children():
            w.destroy()

        filtro = self.filtro_status.get()
        if filtro == "Pagos":
            itens = [(p.nome_aluno, p.valor, p.forma_pagamento,
                      p.data, True) for p in self.banco.pagamentos]
        elif filtro == "Pendentes":
            itens = [(v.nome_aluno, v.valor, v.forma_pagamento or "-",
                      v.data, False)
                     for v in self.banco.vendas if not v.pago]
        else:
            itens = [(p.nome_aluno, p.valor, p.forma_pagamento,
                      p.data, True) for p in self.banco.pagamentos]
            itens += [(v.nome_aluno, v.valor, v.forma_pagamento or "-",
                       v.data, False)
                      for v in self.banco.vendas if not v.pago]

        if not itens:
            tk.Label(self.area_lista, text="Nenhum pagamento encontrado.",
                     bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.CORPO).pack(pady=30)
            return

        cab = tk.Frame(self.area_lista, bg=Cores.CARD_FUNDO)
        cab.pack(fill="x", pady=(0, 6))
        for i, p in enumerate((3, 2, 2, 2, 2)):
            cab.grid_columnconfigure(i, weight=p)
        for i, t in enumerate(["Aluno", "Valor", "Forma", "Data", "Status"]):
            tk.Label(cab, text=t, bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_TERCIARIO, font=Fontes.MICRO_NEGRITO,
                     anchor="w").grid(row=0, column=i, sticky="w", padx=4)
        tk.Frame(self.area_lista, bg=Cores.CARD_BORDA, height=1).pack(
            fill="x", pady=(0, 4))

        for idx, (nome, valor, forma, data, pago) in enumerate(itens):
            cor = Cores.CARD_FUNDO if idx % 2 == 0 else "#f8fafc"
            linha = tk.Frame(self.area_lista, bg=cor)
            linha.pack(fill="x", pady=3)
            for i, p in enumerate((3, 2, 2, 2, 2)):
                linha.grid_columnconfigure(i, weight=p)
            tk.Label(linha, text=nome, bg=cor, fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").grid(row=0, column=0, sticky="w",
                                      padx=4, pady=8)
            tk.Label(linha, text=self._reais(valor), bg=cor,
                     fg=Cores.TEXTO_PRIMARIO, font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").grid(row=0, column=1, sticky="w", padx=4)
            tk.Label(linha, text=forma, bg=cor, fg=Cores.TEXTO_SECUNDARIO,
                     font=Fontes.PEQUENO,
                     anchor="w").grid(row=0, column=2, sticky="w", padx=4)
            tk.Label(linha, text=data, bg=cor, fg=Cores.TEXTO_SECUNDARIO,
                     font=Fontes.PEQUENO,
                     anchor="w").grid(row=0, column=3, sticky="w", padx=4)
            cor_st = (Cores.STATUS_PAGO_TEXTO if pago
                      else Cores.STATUS_NAO_PAGO_TEXTO)
            tk.Label(linha,
                     text="✓ Pago" if pago else "● Pendente",
                     bg=cor, fg=cor_st, font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").grid(row=0, column=4, sticky="w", padx=4)
