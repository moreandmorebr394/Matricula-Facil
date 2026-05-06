"""Tela de Frequencia: marcar presenca por aula."""
import tkinter as tk
from typing import Callable

from componentes.botao import BotaoPrimario, BotaoSecundario
from componentes.card import Card, CardComCabecalho
from config.cores import Cores
from config.fontes import Fontes
from dados.banco_dados import BancoDados
from dados.modelos import Frequencia


class TelaFrequencia(tk.Frame):
    def __init__(self, master, banco: BancoDados,
                 mostrar_notificacao: Callable, navegar_para: Callable):
        super().__init__(master, bg=Cores.FUNDO_PRINCIPAL)
        self.banco = banco
        self.mostrar_notificacao = mostrar_notificacao
        self.aula_selecionada: int = 0
        self.presencas: dict = {}
        self._construir()

    def _construir(self):
        wrapper = tk.Frame(self, bg=Cores.FUNDO_PRINCIPAL)
        wrapper.pack(fill="both", expand=True, padx=24, pady=20)
        wrapper.grid_columnconfigure(0, weight=1, uniform="f")
        wrapper.grid_columnconfigure(1, weight=2, uniform="f")
        wrapper.grid_rowconfigure(0, weight=1)

        # ---- Lista de aulas ----
        card_aulas = CardComCabecalho(wrapper,
                                      titulo="Aulas Disponiveis",
                                      icone="📚")
        card_aulas.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.area_aulas = card_aulas.conteudo()
        self.area_aulas.configure(bg=Cores.CARD_FUNDO)

        # ---- Chamada ----
        card_chamada = CardComCabecalho(wrapper,
                                        titulo="Chamada / Presencas",
                                        icone="✓")
        card_chamada.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.area_chamada = card_chamada.conteudo()
        self.area_chamada.configure(bg=Cores.CARD_FUNDO)

        self._render_aulas()
        self._render_chamada()

    def _render_aulas(self):
        for w in self.area_aulas.winfo_children():
            w.destroy()
        if not self.banco.aulas:
            tk.Label(self.area_aulas,
                     text="Nenhuma aula cadastrada.",
                     bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.CORPO).pack(pady=40)
            return

        for aula in self.banco.aulas:
            ativa = (aula.id == self.aula_selecionada)
            cor_fundo = Cores.SIDEBAR_ATIVO if ativa else "#f8fafc"
            cor_txt = (Cores.BRANCO if ativa
                       else Cores.TEXTO_PRIMARIO)
            cor_sub = (Cores.BRANCO if ativa
                       else Cores.TEXTO_TERCIARIO)
            item = tk.Frame(self.area_aulas, bg=cor_fundo,
                            cursor="hand2")
            item.pack(fill="x", pady=3)

            turma = next((t for t in self.banco.turmas
                          if t.id == aula.turma_id), None)
            tnome = turma.nome if turma else "Turma desconhecida"

            tk.Label(item, text=aula.titulo, bg=cor_fundo,
                     fg=cor_txt, font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").pack(anchor="w", padx=12, pady=(8, 0))
            tk.Label(item, text=f"{tnome}  •  {aula.data}",
                     bg=cor_fundo, fg=cor_sub, font=Fontes.MICRO,
                     anchor="w").pack(anchor="w", padx=12, pady=(0, 8))

            for w in (item, *item.winfo_children()):
                w.bind("<Button-1>",
                       lambda e, aid=aula.id: self._selecionar_aula(aid))

    def _selecionar_aula(self, aula_id: int):
        self.aula_selecionada = aula_id
        # carregar presencas existentes
        existentes = [f for f in self.banco.frequencias
                      if f.aula_id == aula_id]
        self.presencas = {f.aluno_nome: f.presente for f in existentes}
        self._render_aulas()
        self._render_chamada()

    def _render_chamada(self):
        for w in self.area_chamada.winfo_children():
            w.destroy()
        if not self.aula_selecionada:
            tk.Label(self.area_chamada,
                     text="Selecione uma aula a esquerda\n"
                          "para fazer a chamada.",
                     bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.CORPO,
                     justify="center").pack(pady=80)
            return

        aula = next((a for a in self.banco.aulas
                     if a.id == self.aula_selecionada), None)
        if not aula:
            return
        turma = next((t for t in self.banco.turmas
                      if t.id == aula.turma_id), None)
        if not turma or not turma.alunos:
            tk.Label(self.area_chamada,
                     text="Esta turma nao possui alunos matriculados.",
                     bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                     font=Fontes.CORPO).pack(pady=40)
            return

        # cabecalho
        topo = tk.Frame(self.area_chamada, bg=Cores.CARD_FUNDO)
        topo.pack(fill="x", pady=(0, 10))
        tk.Label(topo, text=aula.titulo, bg=Cores.CARD_FUNDO,
                 fg=Cores.TEXTO_PRIMARIO,
                 font=Fontes.TITULO_CARD,
                 anchor="w").pack(anchor="w")
        tk.Label(topo, text=f"{turma.nome}  •  {aula.data}",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_TERCIARIO,
                 font=Fontes.PEQUENO,
                 anchor="w").pack(anchor="w")

        sep = tk.Frame(self.area_chamada, bg=Cores.CARD_BORDA, height=1)
        sep.pack(fill="x", pady=(0, 10))

        # alunos
        for nome in turma.alunos:
            self.presencas.setdefault(nome, False)

        self.var_check = {}
        for nome in turma.alunos:
            linha = tk.Frame(self.area_chamada, bg="#f8fafc")
            linha.pack(fill="x", pady=2)

            tk.Label(linha, text="👤  " + nome,
                     bg="#f8fafc", fg=Cores.TEXTO_PRIMARIO,
                     font=Fontes.PEQUENO_NEGRITO,
                     anchor="w").pack(side="left", padx=12, pady=10)

            var = tk.BooleanVar(value=self.presencas.get(nome, False))
            self.var_check[nome] = var
            tk.Checkbutton(linha, text="Presente",
                           variable=var,
                           bg="#f8fafc",
                           fg=Cores.TEXTO_SECUNDARIO,
                           selectcolor=Cores.CARD_FUNDO,
                           activebackground="#f8fafc",
                           font=Fontes.PEQUENO,
                           cursor="hand2").pack(side="right", padx=12)

        # estatisticas
        sep2 = tk.Frame(self.area_chamada, bg=Cores.CARD_BORDA, height=1)
        sep2.pack(fill="x", pady=10)

        total = len(turma.alunos)
        presentes = sum(1 for v in self.var_check.values() if v.get())
        info = tk.Frame(self.area_chamada, bg=Cores.CARD_FUNDO)
        info.pack(fill="x", pady=(0, 10))
        tk.Label(info,
                 text=f"Total: {total} alunos",
                 bg=Cores.CARD_FUNDO, fg=Cores.TEXTO_SECUNDARIO,
                 font=Fontes.PEQUENO).pack(side="left")
        pct = (presentes / total * 100) if total else 0
        tk.Label(info,
                 text=f"Frequencia inicial: {pct:.0f}%",
                 bg=Cores.CARD_FUNDO, fg=Cores.BOTAO_PRIMARIO,
                 font=Fontes.PEQUENO_NEGRITO).pack(side="right")

        botoes = tk.Frame(self.area_chamada, bg=Cores.CARD_FUNDO)
        botoes.pack(fill="x")
        BotaoSecundario(botoes, texto="Marcar todos",
                        comando=self._marcar_todos,
                        largura=120).pack(side="left")
        BotaoPrimario(botoes, texto="Salvar Chamada",
                      comando=self._salvar,
                      largura=140).pack(side="right")

    def _marcar_todos(self):
        for v in self.var_check.values():
            v.set(True)

    def _salvar(self):
        # remover frequencias antigas
        self.banco.frequencias = [f for f in self.banco.frequencias
                                  if f.aula_id != self.aula_selecionada]
        aula = next((a for a in self.banco.aulas
                     if a.id == self.aula_selecionada), None)
        for nome, var in self.var_check.items():
            self.banco.frequencias.append(Frequencia(
                id=len(self.banco.frequencias) + 1,
                aula_id=self.aula_selecionada,
                aluno_nome=nome,
                presente=var.get(),
                data=aula.data if aula else "",
            ))
        self.banco.salvar()
        self.banco.notificar_observadores()
        presentes = sum(1 for v in self.var_check.values() if v.get())
        self.mostrar_notificacao(
            f"Chamada salva. {presentes} presentes.",
            "SUCESSO", titulo="Frequencia atualizada")
        self._render_chamada()
