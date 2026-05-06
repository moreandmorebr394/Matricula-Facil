"""Tela de Vendas: registrar e listar vendas."""
import tkinter as tk
from typing import Callable

from componentes.botao import BotaoPrimario, BotaoSecundario
from componentes.campo_entrada import CampoEntrada, CampoSelecao
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from dados.modelos import Venda


CURSOS = ["Marketing Digital", "Social Media", "Trafego Pago",
          "Design Grafico", "Programacao Web", "UX/UI Design"]
PAGAMENTOS = ["PIX", "Boleto", "Cartao Credito", "Cartao Debito", "Dinheiro"]


class TelaVendas(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)
        wrapper.grid_columnconfigure(0, weight=1, uniform="v")
        wrapper.grid_columnconfigure(1, weight=2, uniform="v")

        # ----- Indicadores -----
        indicadores = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        indicadores.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 16))
        for i in range(3):
            indicadores.grid_columnconfigure(i, weight=1, uniform="ind")

        total = len(self.banco.vendas)
        faturamento = sum(v.valor for v in self.banco.vendas if v.pago)
        ticket = (faturamento / total) if total else 0.0

        self._card_indicador(
            indicadores, "Total de Vendas", str(total), "🛒",
        ).grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self._card_indicador(
            indicadores, "Faturamento",
            f"R$ {faturamento:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "💰",
        ).grid(row=0, column=1, sticky="nsew", padx=4)
        self._card_indicador(
            indicadores, "Ticket Medio",
            f"R$ {ticket:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."),
            "📈",
        ).grid(row=0, column=2, sticky="nsew", padx=(8, 0))

        # ----- Formulario nova venda -----
        form_card = CardComCabecalho(wrapper, titulo="Nova Venda", icone="➕")
        form_card.grid(row=1, column=0, sticky="nsew", padx=(0, 8))
        c = form_card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)

        self.campo_aluno = CampoEntrada(
            c, rotulo="Nome do aluno", obrigatorio=True,
            placeholder="Nome completo",
        )
        self.campo_aluno.pack(fill="x", pady=4)

        self.campo_curso = CampoSelecao(
            c, rotulo="Curso", opcoes=CURSOS, obrigatorio=True,
        )
        self.campo_curso.pack(fill="x", pady=4)

        self.campo_valor = CampoEntrada(
            c, rotulo="Valor (R$)", placeholder="0,00", obrigatorio=True,
        )
        self.campo_valor.pack(fill="x", pady=4)

        self.campo_captador = CampoEntrada(
            c, rotulo="Captador", placeholder="Nome do vendedor",
        )
        self.campo_captador.pack(fill="x", pady=4)

        self.campo_pgto = CampoSelecao(
            c, rotulo="Forma de pagamento", opcoes=PAGAMENTOS,
        )
        self.campo_pgto.pack(fill="x", pady=4)

        self.var_pago = tk.BooleanVar(value=False)
        check = tk.Checkbutton(
            c, text="Pagamento ja confirmado",
            variable=self.var_pago,
            bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_SECUNDARIO,
            font=Fontes.PEQUENO, activebackground=Cores.CARD_FUNDO,
            selectcolor=Cores.CARD_FUNDO, cursor="hand2",
        )
        check.pack(anchor="w", pady=(8, 14))

        botoes = tk.Frame(c, bg=Cores.CARD_FUNDO)
        botoes.pack(fill="x")
        BotaoPrimario(
            botoes, texto="Registrar Venda",
            comando=self._registrar_venda, largura=160,
        ).pack(side="right")

        # ----- Lista de vendas -----
        lista_card = CardComCabecalho(
            wrapper, titulo="Vendas Registradas", icone="📋",
        )
        lista_card.grid(row=1, column=1, sticky="nsew", padx=(8, 0))
        self.area_lista = lista_card.conteudo()
        self.area_lista.configure(bg=Cores.CARD_FUNDO)
        self._renderizar_lista()

    def _card_indicador(self, parent, rotulo, valor, icone):
        card = Card(parent, padding=18)
        c = card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)
        topo = tk.Frame(c, bg=Cores.CARD_FUNDO)
        topo.pack(fill="x")
        tk.Label(topo, text=icone, bg=Cores.CARD_FUNDO,
                 fg=Cores.BOTAO_PRIMARIO,
                 font=(Fontes.FAMILIA, 16)).pack(side="left")
        tk.Label(topo, text=rotulo, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO).pack(side="left", padx=(8, 0))
        tk.Label(c, text=valor, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.NUMERO_MEDIO).pack(anchor="w", pady=(8, 0))
        return card

    def _registrar_venda(self):
        nome = self.campo_aluno.obter()
        curso = self.campo_curso.obter()
        valor_txt = self.campo_valor.obter().replace(",", ".").replace("R$", "").strip()
        if not nome:
            self.mostrar_notificacao("Informe o nome do aluno.", "ERRO")
            return
        if not curso:
            self.mostrar_notificacao("Selecione o curso.", "ERRO")
            return
        try:
            valor = float(valor_txt)
        except ValueError:
            self.mostrar_notificacao("Valor invalido.", "ERRO")
            return

        venda = Venda(
            nome_aluno=nome, curso=curso, valor=valor,
            captador=self.campo_captador.obter(),
            pago=self.var_pago.get(),
            forma_pagamento=self.campo_pgto.obter(),
        )
        self.banco.adicionar_venda(venda)
        for c in (self.campo_aluno, self.campo_valor, self.campo_captador):
            c.limpar()
        self.var_pago.set(False)
        self.mostrar_notificacao(
            f"Venda de {nome} registrada!", "SUCESSO",
            titulo="Venda criada",
        )
        self._renderizar_lista()

    def _renderizar_lista(self):
        for w in self.area_lista.winfo_children():
            w.destroy()
        if not self.banco.vendas:
            tk.Label(
                self.area_lista, text="Nenhuma venda registrada ainda.",
                bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                font=Fontes.CORPO,
            ).pack(pady=30)
            return

        cabecalho = tk.Frame(self.area_lista, bg=Cores.CARD_FUNDO)
        cabecalho.pack(fill="x", pady=(0, 6))
        for i, peso in enumerate((3, 3, 2, 2, 2)):
            cabecalho.grid_columnconfigure(i, weight=peso)
        for i, c in enumerate(["Aluno", "Curso", "Valor", "Forma", "Pagamento"]):
            tk.Label(cabecalho, text=c, bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.MICRO_NEGRITO,
                     anchor="w").grid(row=0, column=i, sticky="w", padx=4)

        tk.Frame(self.area_lista, bg=Cores.CARD_BORDA, height=1).pack(
            fill="x", pady=(0, 4)
        )

        for idx, v in enumerate(self.banco.vendas):
            cor = Cores.CARD_FUNDO if idx % 2 == 0 else "#f8fafc"
            linha = tk.Frame(self.area_lista, bg=cor)
            linha.pack(fill="x", pady=4)
            for i, peso in enumerate((3, 3, 2, 2, 2)):
                linha.grid_columnconfigure(i, weight=peso)

            tk.Label(linha, text=v.nome_aluno, bg=cor,
                     fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").grid(row=0, column=0, sticky="w", padx=4, pady=8)
            tk.Label(linha, text=v.curso, bg=cor,
                     fg=Cores.TEXTO_SECUNDARIO,
                     font=Fontes.PEQUENO,
                     anchor="w").grid(row=0, column=1, sticky="w", padx=4)
            valor_fmt = (f"R$ {v.valor:,.2f}".replace(",", "X")
                         .replace(".", ",").replace("X", "."))
            tk.Label(linha, text=valor_fmt, bg=cor,
                     fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").grid(row=0, column=2, sticky="w", padx=4)
            tk.Label(linha, text=v.forma_pagamento or "-", bg=cor,
                     fg=Cores.TEXTO_SECUNDARIO,
                     font=Fontes.PEQUENO,
                     anchor="w").grid(row=0, column=3, sticky="w", padx=4)
            cor_status = (Cores.STATUS_PAGO_TEXTO if v.pago
                          else Cores.STATUS_NAO_PAGO_TEXTO)
            tk.Label(linha, text="✓ Pago" if v.pago else "● Pendente",
                     bg=cor, fg=cor_status,
                     font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").grid(row=0, column=4, sticky="w", padx=4)
