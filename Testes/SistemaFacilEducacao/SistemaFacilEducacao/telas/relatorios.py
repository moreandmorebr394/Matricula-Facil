"""Tela de Relatorios: visao geral em graficos e indicadores."""
import tkinter as tk
from typing import Callable

from componentes.botao import BotaoPrimario, BotaoSecundario
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from utilitarios.graficos import GraficoPizza


class TelaRelatorios(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)

        # cabecalho
        topo = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        topo.pack(fill="x", pady=(0, 16))
        tk.Label(topo, text="Relatorios Gerais",
                 bg=Cores.FUNDO_PRINCIPAL, fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO).pack(side="left")
        BotaoSecundario(topo, texto="Exportar CSV",
                        comando=self._exportar,
                        largura=120).pack(side="right", padx=4)
        BotaoPrimario(topo, texto="Imprimir",
                      comando=lambda: self.mostrar_notificacao(
                          "Funcao de impressao iniciada.", "INFO"),
                      largura=110).pack(side="right", padx=4)

        # ---- KPIs ----
        kpis = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        kpis.pack(fill="x", pady=(0, 14))
        for i in range(4):
            kpis.grid_columnconfigure(i, weight=1, uniform="k")
        est = self.banco.estatisticas_dashboard()
        self._kpi(kpis, "Total de Leads", str(est["leads"]),
                  "👥", Cores.BOTAO_PRIMARIO).grid(
            row=0, column=0, sticky="nsew", padx=(0, 6))
        self._kpi(kpis, "Vendas Realizadas", str(est["vendas"]),
                  "🛒", Cores.BOTAO_SUCESSO).grid(
            row=0, column=1, sticky="nsew", padx=6)
        self._kpi(kpis, "Faturamento",
                  self._reais(est["faturamento"]),
                  "💰", Cores.NOTIF_AVISO_FUNDO).grid(
            row=0, column=2, sticky="nsew", padx=6)
        self._kpi(kpis, "Conversao",
                  f"{est['conversao']}%",
                  "📈", Cores.FUNIL_VENDAS).grid(
            row=0, column=3, sticky="nsew", padx=(6, 0))

        # ---- Linha 1: barras (vendas por curso) + pizza origem ----
        linha1 = tk.Frame(wrapper, bg=Cores.FUNDO_PRINCIPAL)
        linha1.pack(fill="both", expand=True, pady=(0, 14))
        linha1.grid_columnconfigure(0, weight=2, uniform="r")
        linha1.grid_columnconfigure(1, weight=1, uniform="r")

        barras_card = CardComCabecalho(linha1,
                                       titulo="Vendas por Curso",
                                       icone="📊")
        barras_card.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        cb = barras_card.conteudo()
        cb.configure(bg=Cores.CARD_FUNDO)
        self._barras_curso(cb)

        pizza_card = CardComCabecalho(linha1,
                                      titulo="Origem dos Leads",
                                      icone="🥧")
        pizza_card.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        cp = pizza_card.conteudo()
        cp.configure(bg=Cores.CARD_FUNDO)
        GraficoPizza(cp, self.banco.origem_dos_leads(),
                     largura=300, altura=240).pack(pady=10)

        # ---- Linha 2: tabela leads por status ----
        tab_card = CardComCabecalho(wrapper,
                                    titulo="Distribuicao por Status",
                                    icone="📑")
        tab_card.pack(fill="x")
        ct = tab_card.conteudo()
        ct.configure(bg=Cores.CARD_FUNDO)
        self._distribuicao_status(ct)

    def _kpi(self, parent, rotulo, valor, icone, cor):
        card = Card(parent, padding=18)
        c = card.conteudo()
        c.configure(bg=Cores.CARD_FUNDO)
        topo = tk.Frame(c, bg=Cores.CARD_FUNDO)
        topo.pack(fill="x")
        tk.Label(topo, text=icone, bg=Cores.CARD_FUNDO, fg=cor,
                 font=(Fontes.FAMILIA, 16, "bold")).pack(side="left")
        tk.Label(topo, text=rotulo, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO).pack(side="left", padx=(8, 0))
        tk.Label(c, text=valor, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.NUMERO_MEDIO).pack(anchor="w", pady=(8, 0))
        return card

    def _reais(self, valor):
        return ("R$ " + f"{valor:,.2f}".replace(",", "X")
                .replace(".", ",").replace("X", "."))

    def _barras_curso(self, parent):
        contagem = {}
        for v in self.banco.vendas:
            contagem[v.curso] = contagem.get(v.curso, 0) + 1
        if not contagem:
            contagem = {
                "Marketing Digital": 12, "Trafego Pago": 9,
                "Design Grafico": 7, "Social Media": 6,
                "Programacao Web": 4,
            }

        canvas = tk.Canvas(parent, height=240, bg=Cores.CARD_FUNDO,
                           highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=10, pady=10)
        canvas.update_idletasks()
        canvas.after(50, lambda: self._desenhar_barras(canvas, contagem))

    def _desenhar_barras(self, canvas, contagem):
        canvas.delete("all")
        largura = canvas.winfo_width() or 600
        altura = 240
        max_v = max(contagem.values()) or 1
        n = len(contagem)
        margem = 40
        espaco = (largura - 2 * margem) / max(n, 1)
        cores = [Cores.FUNIL_VISITANTES, Cores.FUNIL_LEADS,
                 Cores.FUNIL_NEGOCIACOES, Cores.FUNIL_VENDAS,
                 Cores.FUNIL_ALUNOS, Cores.PIZZA_OUTROS]

        # eixo
        canvas.create_line(margem, altura - 30, largura - 20,
                           altura - 30, fill=Cores.CARD_BORDA)

        for i, (curso, qtd) in enumerate(contagem.items()):
            x = margem + i * espaco + espaco * 0.15
            largura_barra = espaco * 0.7
            altura_barra = (qtd / max_v) * (altura - 70)
            y_top = altura - 30 - altura_barra
            cor = cores[i % len(cores)]
            self._anim_barra(canvas, x, altura - 30, largura_barra,
                             altura_barra, cor)
            canvas.create_text(x + largura_barra / 2, altura - 12,
                               text=curso[:12],
                               fill=Cores.TEXTO_SECUNDARIO,
                               font=Fontes.MICRO)
            canvas.create_text(x + largura_barra / 2, y_top - 10,
                               text=str(qtd),
                               fill=Cores.TEXTO_PRIMARIO,
                               font=Fontes.PEQUENO_NEGRITO)

    def _anim_barra(self, canvas, x, y_base, largura, altura_alvo,
                    cor, passo=0):
        passos = 18
        if passo > passos:
            return
        cur = altura_alvo * (passo / passos)
        canvas.create_rectangle(x, y_base - cur, x + largura, y_base,
                                fill=cor, outline="",
                                tags=f"b{int(x)}_{passo}")
        canvas.delete(f"b{int(x)}_{passo - 1}")
        canvas.after(15, lambda: self._anim_barra(
            canvas, x, y_base, largura, altura_alvo, cor, passo + 1))

    def _distribuicao_status(self, parent):
        status_count = {"LEAD": 0, "NEGOCIACAO": 0,
                        "PAGO": 0, "NAO_PAGO": 0,
                        "ALUNO_ATIVO": 0}
        for l in self.banco.leads:
            if l.status in status_count:
                status_count[l.status] += 1
        rotulos = {
            "LEAD": "Leads", "NEGOCIACAO": "Em Negociacao",
            "PAGO": "Pagos", "NAO_PAGO": "Nao Pagos",
            "ALUNO_ATIVO": "Alunos Ativos",
        }
        cores = {
            "LEAD": Cores.STATUS_LEAD_TEXTO,
            "NEGOCIACAO": Cores.STATUS_NEGOCIACAO_TEXTO,
            "PAGO": Cores.STATUS_PAGO_TEXTO,
            "NAO_PAGO": Cores.STATUS_NAO_PAGO_TEXTO,
            "ALUNO_ATIVO": Cores.FUNIL_ALUNOS,
        }

        cab = tk.Frame(parent, bg=Cores.CARD_FUNDO)
        cab.pack(fill="x", pady=(0, 6))
        for i, p in enumerate((3, 2, 4)):
            cab.grid_columnconfigure(i, weight=p)
        for i, t in enumerate(["Status", "Quantidade", "Distribuicao"]):
            tk.Label(cab, text=t, bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.MICRO_NEGRITO,
                     anchor="w").grid(row=0, column=i, sticky="ew",
                                      padx=4)

        tk.Frame(parent, bg=Cores.CARD_BORDA, height=1).pack(
            fill="x", pady=(0, 4))

        total = max(sum(status_count.values()), 1)
        for chave, qtd in status_count.items():
            pct = qtd / total
            linha = tk.Frame(parent, bg=Cores.CARD_FUNDO)
            linha.pack(fill="x", pady=4)
            for i, p in enumerate((3, 2, 4)):
                linha.grid_columnconfigure(i, weight=p)

            tk.Label(linha, text=rotulos[chave], bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").grid(row=0, column=0, sticky="w",
                                      padx=4, pady=6)
            tk.Label(linha, text=str(qtd), bg=Cores.CARD_FUNDO,
                     fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").grid(row=0, column=1, sticky="w", padx=4)

            barra_wrap = tk.Frame(linha, bg=Cores.BOTAO_SECUNDARIO,
                                  height=10)
            barra_wrap.grid(row=0, column=2, sticky="ew", padx=4)
            barra_wrap.grid_propagate(False)
            preench = tk.Frame(barra_wrap, bg=cores[chave], height=10)
            preench.place(x=0, y=0, relwidth=pct, relheight=1)

    def _exportar(self):
        try:
            import csv, os
            from config.configuracoes import Configuracoes
            os.makedirs(Configuracoes.PASTA_DADOS, exist_ok=True)
            arquivo = "{}/relatorio_leads.csv".format(
                Configuracoes.PASTA_DADOS)
            with open(arquivo, "w", encoding="utf-8", newline="") as fp:
                w = csv.writer(fp)
                w.writerow(["Nome", "Curso", "Captador",
                            "Status", "Origem", "Data"])
                for l in self.banco.leads:
                    w.writerow([l.nome, l.curso_interesse, l.captador,
                                l.status, l.como_conheceu,
                                l.data_cadastro])
            self.mostrar_notificacao(
                f"CSV exportado em {arquivo}.", "SUCESSO",
                titulo="Relatorio gerado")
        except Exception as e:
            self.mostrar_notificacao(f"Falha: {e}", "ERRO")
