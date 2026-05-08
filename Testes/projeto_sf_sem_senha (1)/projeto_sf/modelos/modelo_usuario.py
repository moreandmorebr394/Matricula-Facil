"""
Modelo de Usuário (alunos e clientes registrados no site público).

Camada Model do MVC: faz CRUD direto no banco e nada mais.
"""
from banco_de_dados.conexao import obter_conexao
from utilitarios.criptografia import gerar_hash_senha, verificar_senha
from utilitarios.geradores import gerar_email_institucional, gerar_id_usuario


class ModeloUsuario:

    @staticmethod
    def cadastrar(
        nome_completo: str,
        email_pessoal: str,
        telefone: str,
        senha_pura: str,
        tipo_conta: str = "aluno",
    ) -> dict:
        """Cadastra novo usuário e retorna o registro criado.

        Levanta ValueError se houver e-mail duplicado.
        """
        bd = obter_conexao()

        existente = bd.consultar_um(
            "SELECT id FROM usuarios WHERE email_pessoal = ?",
            (email_pessoal.lower().strip(),),
        )
        if existente:
            raise ValueError("Já existe uma conta com este e-mail.")

        id_publico = gerar_id_usuario("ALN" if tipo_conta == "aluno" else "CLI")
        email_institucional = gerar_email_institucional(tipo_conta)
        senha_hash = gerar_hash_senha(senha_pura)

        bd.executar(
            "INSERT INTO usuarios "
            "(id_publico, nome_completo, email_pessoal, email_institucional, "
            " telefone, senha_hash, tipo_conta, primeiro_acesso, ativo) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 0, 1)",
            (
                id_publico,
                nome_completo.strip(),
                email_pessoal.lower().strip(),
                email_institucional,
                telefone.strip(),
                senha_hash,
                tipo_conta,
            ),
        )

        novo_id = bd.ultimo_id()
        return ModeloUsuario.buscar_por_id(novo_id)

    @staticmethod
    def autenticar(email_ou_inst: str, senha_pura: str) -> dict | None:
        """Autentica por e-mail pessoal OU institucional."""
        bd = obter_conexao()
        chave = email_ou_inst.lower().strip()
        usuario = bd.consultar_um(
            "SELECT * FROM usuarios "
            "WHERE email_pessoal = ? OR email_institucional = ?",
            (chave, chave),
        )
        if not usuario:
            return None
        if not verificar_senha(senha_pura, usuario["senha_hash"]):
            return None
        if usuario.get("bloqueado"):
            return None
        return usuario

    @staticmethod
    def buscar_por_id(id_usuario: int) -> dict | None:
        bd = obter_conexao()
        return bd.consultar_um(
            "SELECT * FROM usuarios WHERE id = ?", (id_usuario,)
        )

    @staticmethod
    def listar_todos() -> list:
        bd = obter_conexao()
        return bd.consultar(
            "SELECT id, id_publico, nome_completo, email_pessoal, "
            "email_institucional, telefone, tipo_conta, ativo, criado_em "
            "FROM usuarios ORDER BY criado_em DESC"
        )

    @staticmethod
    def alterar_senha(id_usuario: int, nova_senha_pura: str) -> bool:
        bd = obter_conexao()
        novo_hash = gerar_hash_senha(nova_senha_pura)
        bd.executar(
            "UPDATE usuarios SET senha_hash = ?, primeiro_acesso = 0 WHERE id = ?",
            (novo_hash, id_usuario),
        )
        return True
