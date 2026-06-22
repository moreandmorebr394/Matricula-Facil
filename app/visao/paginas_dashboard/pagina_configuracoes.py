"""
Pagina Configuracoes - editar perfil do admin, foto, senha
e dados da instituicao.
"""
import tkinter as tk
from tkinter import filedialog
import base64
import hashlib
import io

try:
    from PIL import Image, ImageTk
    _PIL_OK = True
except ImportError:
    _PIL_OK = False

from componentes.cores import (
    AZUL_PRIMARIO, AZUL_ESCURO, AZUL_HOVER, BRANCO, BRANCO_GELO,
    CINZA_CLARO, CINZA_MEDIO, CINZA_ESCURO, PRETO_TEXTO,
    AMARELO_VIBRANTE, VERDE_SUCESSO, VERMELHO_ERRO,
    FONTE_TITULO, FONTE_TEXTO
)
from componentes.botao_moderno import BotaoModerno
from componentes.card import Card
from componentes.notificacao import Notificacao
from componentes.mascaras import aplicar_mascara_telefone
from app.modelo import modelo_geral

try:
    import bcrypt
    _BCRYPT_OK = True
except ImportError:
    _BCRYPT_OK = False


class PaginaConfiguracoes(tk.Frame):
    def __init__(self, parent, dashboard=None):
        super().__init__(parent, bg=BRANCO_GELO)
        self.dashboard = dashboard
        self.entries = {}
        # Referências do avatar para atualização dinâmica
        self._avatar_frame = None
        self._avatar_label = None
        self._avatar_photo_img = None  # mantém referência para evitar GC
        self._construir()

    def _construir(self):
        topo = tk.Frame(self, bg=BRANCO_GELO, padx=24, pady=14)
        topo.pack(fill="x")
        tk.Label(topo, text="Configuracoes",
                 font=(FONTE_TITULO, 18, "bold"),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO).pack(anchor="w")
        tk.Label(topo,
                 text="Gerencie seu perfil e dados da instituicao",
                 font=(FONTE_TEXTO, 9),
                 fg=CINZA_ESCURO, bg=BRANCO_GELO).pack(anchor="w")

        canvas_main = tk.Canvas(self, bg=BRANCO_GELO, highlightthickness=0)
        canvas_main.pack(side="left", fill="both", expand=True)
        sb = tk.Scrollbar(self, orient="vertical", command=canvas_main.yview)
        sb.pack(side="right", fill="y")
        canvas_main.configure(yscrollcommand=sb.set)

        cont = tk.Frame(canvas_main, bg=BRANCO_GELO)
        window_id = canvas_main.create_window((0, 0), window=cont, anchor="n",
                                   width=1140)

        def ar(_=None):
            bbox = canvas_main.bbox("all")
            if bbox:
                canvas_main.configure(scrollregion=(0, 0, 0, bbox[3]))
        cont.bind("<Configure>", ar)

        def ao_redimensionar_canvas(e):
            nova_largura = min(1140, e.width - 40)
            if nova_largura < 300:
                nova_largura = 300
            canvas_main.itemconfig(window_id, width=nova_largura)
            canvas_main.coords(window_id, e.width // 2, 0)
        canvas_main.bind("<Configure>", ao_redimensionar_canvas, add="+")
        canvas_main.bind_all("<MouseWheel>",
                             lambda e: canvas_main.yview_scroll(
                                 int(-1 * (e.delta / 120)), "units"), add="+")

        # Layout grid - 2 colunas
        grid = tk.Frame(cont, bg=BRANCO_GELO, padx=24, pady=10)
        grid.pack(fill="both", expand=True)

        # Coluna 1
        col1 = tk.Frame(grid, bg=BRANCO_GELO)
        col1.grid(row=0, column=0, sticky="nsew", padx=4)
        grid.columnconfigure(0, weight=1)

        self._construir_perfil(col1)
        self._construir_senha(col1)

        # Coluna 2
        col2 = tk.Frame(grid, bg=BRANCO_GELO)
        col2.grid(row=0, column=1, sticky="nsew", padx=4)
        grid.columnconfigure(1, weight=1)

        self._construir_instituicao(col2)
        self._construir_sistema(col2)

    def _construir_perfil(self, parent):
        card = Card(parent, titulo="👤  Meu Perfil", padding=14, raio=12)
        card.pack(fill="x", pady=6)
        cont = card.interno

        # Avatar com botao de upload
        avatar_wrap = tk.Frame(cont, bg=BRANCO)
        avatar_wrap.pack(pady=(0, 14))

        avatar = tk.Frame(avatar_wrap, bg=AMARELO_VIBRANTE,
                          width=110, height=110,
                          highlightbackground=AZUL_PRIMARIO,
                          highlightthickness=3)
        avatar.pack()
        avatar.pack_propagate(False)
        self._avatar_frame = avatar

        # Tenta carregar foto salva; se não houver, exibe emoji padrão
        try:
            foto_b64 = modelo_geral.obter_configuracao("foto_admin", "")
        except Exception:
            foto_b64 = ""
        if foto_b64 and _PIL_OK:
            self._avatar_label = tk.Label(avatar, bg=AMARELO_VIBRANTE)
            self._avatar_label.pack(expand=True)
            self._aplicar_foto_label(foto_b64)
        else:
            self._avatar_label = tk.Label(
                avatar, text="👨‍💼", font=("Segoe UI Emoji", 50),
                bg=AMARELO_VIBRANTE)
            self._avatar_label.pack(expand=True)

        BotaoModerno(avatar_wrap, texto="📷  Trocar Foto",
                     comando=self._trocar_foto,
                     largura=160, altura=32,
                     cor_normal=BRANCO, cor_hover=CINZA_CLARO,
                     cor_texto=AZUL_PRIMARIO,
                     fonte_tamanho=9,
                     cor_fundo=BRANCO).pack(pady=(8, 0))

        # Campos
        try:
            nome_atual = modelo_geral.obter_configuracao(
                "nome_admin", "Administrador")
            email_atual = modelo_geral.obter_configuracao(
                "email_admin", "admin@sistemafacil.pa.br")
            tel_atual = modelo_geral.obter_configuracao("telefone_admin", "")
        except Exception:
            nome_atual = "Administrador"
            email_atual = "admin@sistemafacil.pa.br"
            tel_atual = ""

        self._campo_config(cont, "nome_admin", "Nome Completo",
                           valor_inicial=nome_atual)
        self._campo_config(cont, "email_admin", "Email Institucional",
                           valor_inicial=email_atual)
        self._campo_config(cont, "telefone_admin", "Telefone",
                           valor_inicial=tel_atual,
                           mascara="telefone")

        BotaoModerno(cont, texto="💾  Salvar Perfil",
                     comando=self._salvar_perfil,
                     largura=200, altura=36,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     fonte_tamanho=10,
                     cor_fundo=BRANCO).pack(pady=(12, 4))

    def _construir_senha(self, parent):
        card = Card(parent, titulo="🔐  Alterar Senha", padding=14, raio=12)
        card.pack(fill="x", pady=6)
        cont = card.interno

        self._campo_config(cont, "senha_atual", "Senha Atual",
                           senha=True)
        self._campo_config(cont, "senha_nova", "Nova Senha",
                           senha=True)
        self._campo_config(cont, "senha_repetir", "Repetir Nova Senha",
                           senha=True)

        BotaoModerno(cont, texto="🔒  Alterar Senha",
                     comando=self._alterar_senha,
                     largura=200, altura=36,
                     cor_normal=VERMELHO_ERRO, cor_hover="#DC2626",
                     fonte_tamanho=10,
                     cor_fundo=BRANCO).pack(pady=(12, 4))

    def _construir_instituicao(self, parent):
        card = Card(parent, titulo="🏢  Dados da Instituicao", padding=14, raio=12)
        card.pack(fill="x", pady=6)
        cont = card.interno

        # Carrega valores atuais
        try:
            nome = modelo_geral.obter_configuracao(
                "nome_instituicao", "Sistema Facil Educacao")
            email_c = modelo_geral.obter_configuracao(
                "email_contato", "contato@sistemafacil.pa.br")
            tel_c = modelo_geral.obter_configuracao(
                "telefone_contato", "(91) 3000-0000")
            end = modelo_geral.obter_configuracao(
                "endereco_instituicao", "Belem, Para - Brasil")
        except Exception:
            nome = "Sistema Facil Educacao"
            email_c = "contato@sistemafacil.pa.br"
            tel_c = "(91) 3000-0000"
            end = "Belem, Para - Brasil"

        self._campo_config(cont, "nome_instituicao",
                           "Nome da Instituicao",
                           valor_inicial=nome)
        self._campo_config(cont, "email_contato", "Email de Contato",
                           valor_inicial=email_c)
        self._campo_config(cont, "telefone_contato", "Telefone de Contato",
                           valor_inicial=tel_c, mascara="telefone")
        self._campo_config(cont, "endereco_instituicao", "Endereco",
                           valor_inicial=end)

        BotaoModerno(cont, texto="💾  Salvar Dados",
                     comando=self._salvar_instituicao,
                     largura=200, altura=36,
                     cor_normal=AZUL_PRIMARIO, cor_hover=AZUL_HOVER,
                     fonte_tamanho=10,
                     cor_fundo=BRANCO).pack(pady=(12, 4))

    def _construir_sistema(self, parent):
        card = Card(parent, titulo="⚙  Configuracoes do Sistema", padding=14, raio=12)
        card.pack(fill="x", pady=6)
        cont = card.interno

        try:
            total_notif = str(modelo_geral.contar_notificacoes_nao_lidas())
        except Exception:
            total_notif = "0"

        infos = [
            ("Versao", "1.0.0"),
            ("Banco de Dados", "MySQL (WampServer)"),
            ("Suporte", "suporte@sistemafacil.pa.br"),
            ("Total de Notificacoes", total_notif),
        ]

        for rotulo, valor in infos:
            linha = tk.Frame(cont, bg=BRANCO)
            linha.pack(fill="x", pady=3)
            tk.Label(linha, text=rotulo,
                     font=(FONTE_TEXTO, 9, "bold"),
                     fg=CINZA_MEDIO, bg=BRANCO).pack(side="left")
            tk.Label(linha, text=valor,
                     font=(FONTE_TEXTO, 10),
                     fg=AZUL_ESCURO, bg=BRANCO).pack(side="right")

        # Sobre
        sobre = tk.Frame(cont, bg=BRANCO_GELO,
                         highlightbackground=AMARELO_VIBRANTE,
                         highlightthickness=2)
        sobre.pack(fill="x", pady=(14, 4))
        tk.Label(sobre,
                 text="ℹ Sistema Facil Educacao\n\n"
                      "Plataforma educacional completa com\n"
                      "gestao de leads, vendas, turmas e mais.\n"
                      "Desenvolvido em Python + Tkinter.",
                 font=(FONTE_TEXTO, 9),
                 fg=AZUL_ESCURO, bg=BRANCO_GELO,
                 justify="center", padx=14, pady=12).pack()

    def _campo_config(self, parent, chave, label, valor_inicial="",
                      senha=False, mascara=None):
        wrap = tk.Frame(parent, bg=BRANCO)
        wrap.pack(fill="x", pady=4)

        tk.Label(wrap, text=label,
                 font=(FONTE_TEXTO, 8, "bold"),
                 fg=CINZA_MEDIO, bg=BRANCO).pack(anchor="w")
        entry = tk.Entry(wrap, font=(FONTE_TEXTO, 10),
                         bg=BRANCO_GELO, fg=PRETO_TEXTO,
                         relief="flat",
                         highlightbackground=CINZA_CLARO,
                         highlightthickness=1,
                         show="•" if senha else "")
        entry.pack(fill="x", ipady=6)
        if valor_inicial:
            entry.insert(0, valor_inicial)
        if mascara == "telefone":
            aplicar_mascara_telefone(entry)
        self.entries[chave] = entry

    def _aplicar_foto_label(self, b64: str):
        """Decodifica o base64 e atualiza o Label do avatar com a imagem."""
        if not _PIL_OK or not self._avatar_label:
            return
        try:
            dados = base64.b64decode(b64)
            img = Image.open(io.BytesIO(dados))
            img = img.resize((110, 110), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self._avatar_photo_img = photo  # evita garbage collection
            self._avatar_label.configure(image=photo, text="",
                                         bg=AMARELO_VIBRANTE)
        except Exception:
            # Se falhar, mantém o emoji padrão
            self._avatar_label.configure(
                image="", text="👨‍💼",
                font=("Segoe UI Emoji", 50), bg=AMARELO_VIBRANTE)

    def _trocar_foto(self):
        caminho = filedialog.askopenfilename(
            title="Selecione uma imagem",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.gif *.webp"),
                ("Todos os arquivos", "*.*")
            ]
        )
        if not caminho:
            return

        try:
            with open(caminho, "rb") as f:
                dados = f.read()
            # Limita tamanho (2MB)
            if len(dados) > 2 * 1024 * 1024:
                Notificacao.aviso(
                    self, "Imagem muito grande. Maximo 2MB.")
                return

            b64 = base64.b64encode(dados).decode("utf-8")
            modelo_geral.salvar_configuracao("foto_admin", b64)

            # Atualiza o avatar na tela imediatamente
            if _PIL_OK and self._avatar_label:
                self._aplicar_foto_label(b64)
            else:
                # Sem PIL: apenas informa que foi salvo
                Notificacao.aviso(
                    self,
                    "Foto salva! Instale Pillow (pip install Pillow) "
                    "para visualizar a foto aqui.")
                return

            Notificacao.sucesso(self, "Foto atualizada com sucesso!")
            if self.dashboard:
                try:
                    self.dashboard.atualizar_perfil_header()
                except Exception:
                    pass
        except Exception as e:
            Notificacao.erro(self, f"Erro ao salvar foto: {e}")

    def _salvar_perfil(self):
        try:
            modelo_geral.salvar_configuracao(
                "nome_admin", self.entries["nome_admin"].get())
            modelo_geral.salvar_configuracao(
                "email_admin", self.entries["email_admin"].get())
            modelo_geral.salvar_configuracao(
                "telefone_admin", self.entries["telefone_admin"].get())

            modelo_geral.criar_notificacao(
                "Perfil Atualizado",
                "Suas informacoes de perfil foram salvas",
                "sucesso"
            )
            Notificacao.sucesso(self, "Perfil salvo com sucesso!")
            if self.dashboard:
                try:
                    self.dashboard.atualizar_contador_notificacoes()
                    self.dashboard.atualizar_perfil_header()
                except Exception:
                    pass
        except Exception as e:
            Notificacao.erro(self, f"Erro ao salvar: {e}")

    def _salvar_instituicao(self):
        try:
            for chave in ("nome_instituicao", "email_contato",
                          "telefone_contato", "endereco_instituicao"):
                modelo_geral.salvar_configuracao(
                    chave, self.entries[chave].get())

            modelo_geral.criar_notificacao(
                "Dados da Instituicao Atualizados",
                "Os dados da instituicao foram atualizados",
                "info"
            )
            Notificacao.sucesso(self, "Dados salvos com sucesso!")
            if self.dashboard:
                try:
                    self.dashboard.atualizar_contador_notificacoes()
                except Exception:
                    pass
        except Exception as e:
            Notificacao.erro(self, f"Erro: {e}")

    def _alterar_senha(self):
        atual = self.entries["senha_atual"].get()
        nova = self.entries["senha_nova"].get()
        repetir = self.entries["senha_repetir"].get()

        if not atual or not nova:
            Notificacao.erro(self, "Preencha todos os campos")
            return

        if nova != repetir:
            Notificacao.erro(self, "As novas senhas nao coincidem")
            return

        if len(nova) < 6:
            Notificacao.erro(
                self, "Nova senha deve ter pelo menos 6 caracteres")
            return

        # Gera novo hash e salva em configuracoes (override do credenciais.py)
        try:
            if _BCRYPT_OK:
                novo_hash = bcrypt.hashpw(
                    nova.encode("utf-8"),
                    bcrypt.gensalt()).decode("utf-8")
                modelo_geral.salvar_configuracao(
                    "senha_admin_hash", novo_hash)
            else:
                # SHA-256 fallback
                novo_hash = hashlib.sha256(nova.encode()).hexdigest()
                modelo_geral.salvar_configuracao(
                    "senha_admin_hash_sha256", novo_hash)

            modelo_geral.criar_notificacao(
                "Senha Alterada",
                "A senha do administrador foi alterada",
                "aviso"
            )

            # Limpa campos
            for k in ("senha_atual", "senha_nova", "senha_repetir"):
                self.entries[k].delete(0, "end")

            Notificacao.sucesso(self, "Senha alterada com sucesso!")
        except Exception as e:
            Notificacao.erro(self, f"Erro ao alterar senha: {e}")
