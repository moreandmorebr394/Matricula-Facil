"""
Modelo de Lead / Aluno cadastrado pelo administrador.

Camada Model: CRUD puro com o banco de dados.
"""
from datetime import datetime
from banco_de_dados.conexao import obter_conexao
from utilitarios.criptografia import (
    criptografar_dado_sensivel,
    descriptografar_dado_sensivel,
)


CAMPOS_LEAD = (
    "id", "nome_completo", "data_nascimento", "cpf_cifrado", "email",
    "telefone", "endereco", "cidade", "estado", "curso_interesse",
    "como_conheceu", "captador", "observacoes", "status",
    "criado_em", "atualizado_em",
)


class ModeloLead:

    @staticmethod
    def inserir(dados: dict) -> int:
        """Insere um novo lead. Retorna o ID criado."""
        bd = obter_conexao()
        cpf_cifrado = criptografar_dado_sensivel(dados.get("cpf", ""))
        bd.executar(
            "INSERT INTO leads "
            "(nome_completo, data_nascimento, cpf_cifrado, email, telefone, "
            " endereco, cidade, estado, curso_interesse, como_conheceu, "
            " captador, observacoes, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                dados.get("nome_completo", "").strip(),
                dados.get("data_nascimento", ""),
                cpf_cifrado,
                dados.get("email", "").strip().lower(),
                dados.get("telefone", "").strip(),
                dados.get("endereco", "").strip(),
                dados.get("cidade", "").strip(),
                dados.get("estado", "").strip().upper()[:2],
                dados.get("curso_interesse", ""),
                dados.get("como_conheceu", ""),
                dados.get("captador", ""),
                dados.get("observacoes", ""),
                dados.get("status", "LEAD"),
            ),
        )
        return bd.ultimo_id()

    @staticmethod
    def listar(filtro_status: str = None, busca: str = None) -> list:
        bd = obter_conexao()
        condicoes = []
        parametros = []
        if filtro_status:
            condicoes.append("status = ?")
            parametros.append(filtro_status)
        if busca:
            condicoes.append(
                "(nome_completo LIKE ? OR email LIKE ? OR curso_interesse LIKE ?)"
            )
            curinga = f"%{busca}%"
            parametros.extend([curinga, curinga, curinga])

        sql = "SELECT * FROM leads"
        if condicoes:
            sql += " WHERE " + " AND ".join(condicoes)
        sql += " ORDER BY criado_em DESC"

        leads = bd.consultar(sql, tuple(parametros))
        # descriptografa CPF para exibição
        for l in leads:
            l["cpf"] = descriptografar_dado_sensivel(l.get("cpf_cifrado") or "")
        return leads

    @staticmethod
    def buscar_por_id(id_lead: int) -> dict | None:
        bd = obter_conexao()
        registro = bd.consultar_um("SELECT * FROM leads WHERE id = ?", (id_lead,))
        if registro:
            registro["cpf"] = descriptografar_dado_sensivel(
                registro.get("cpf_cifrado") or ""
            )
        return registro

    @staticmethod
    def atualizar(id_lead: int, dados: dict) -> bool:
        bd = obter_conexao()
        atualizaveis = {
            "nome_completo": dados.get("nome_completo"),
            "data_nascimento": dados.get("data_nascimento"),
            "cpf_cifrado": criptografar_dado_sensivel(dados.get("cpf", "")) or None,
            "email": (dados.get("email") or "").strip().lower(),
            "telefone": dados.get("telefone"),
            "endereco": dados.get("endereco"),
            "cidade": dados.get("cidade"),
            "estado": (dados.get("estado") or "").upper()[:2],
            "curso_interesse": dados.get("curso_interesse"),
            "como_conheceu": dados.get("como_conheceu"),
            "captador": dados.get("captador"),
            "observacoes": dados.get("observacoes"),
            "status": dados.get("status"),
        }
        # Remove None para não sobrescrever em branco
        atualizaveis = {
            k: v for k, v in atualizaveis.items()
            if v is not None and v != ""
        }
        if not atualizaveis:
            return False

        partes = ", ".join(f"{c} = ?" for c in atualizaveis.keys())
        # Atualiza atualizado_em manualmente (SQLite não tem ON UPDATE)
        partes += ", atualizado_em = ?"
        valores = list(atualizaveis.values())
        valores.append(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        valores.append(id_lead)

        bd.executar(f"UPDATE leads SET {partes} WHERE id = ?", tuple(valores))
        return True

    @staticmethod
    def excluir(id_lead: int) -> bool:
        bd = obter_conexao()
        bd.executar("DELETE FROM leads WHERE id = ?", (id_lead,))
        return True

    @staticmethod
    def alterar_status(id_lead: int, novo_status: str) -> bool:
        bd = obter_conexao()
        bd.executar(
            "UPDATE leads SET status = ?, atualizado_em = ? WHERE id = ?",
            (novo_status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), id_lead),
        )
        return True

    @staticmethod
    def contar_por_status() -> dict:
        bd = obter_conexao()
        registros = bd.consultar(
            "SELECT status, COUNT(*) AS total FROM leads GROUP BY status"
        )
        contagem = {}
        for r in registros:
            contagem[r["status"]] = r["total"]
        return contagem

    @staticmethod
    def total() -> int:
        bd = obter_conexao()
        r = bd.consultar_um("SELECT COUNT(*) AS c FROM leads")
        return r["c"] if r else 0

    @staticmethod
    def total_no_periodo(inicio: str, fim: str) -> int:
        """Conta leads criados entre duas datas (formato AAAA-MM-DD)."""
        bd = obter_conexao()
        r = bd.consultar_um(
            "SELECT COUNT(*) AS c FROM leads WHERE criado_em BETWEEN ? AND ?",
            (inicio, fim),
        )
        return r["c"] if r else 0
