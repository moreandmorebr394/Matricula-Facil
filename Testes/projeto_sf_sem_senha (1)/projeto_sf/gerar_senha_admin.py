"""
=============================================================================
   GERADOR DE HASH DE SENHA PARA ADMINISTRADORES
=============================================================================

Use este script SEMPRE que precisar:
   - Cadastrar uma senha de um novo administrador
   - Trocar a senha de um administrador existente

Como usar:

   1. Abra o terminal/CMD na pasta do projeto.
   2. Execute:

         python gerar_senha_admin.py

   3. Digite a senha desejada (ela nao aparece na tela enquanto digita).
   4. Confirme a senha.
   5. Copie o bloco que aparece e cole no arquivo:

         configuracoes_admin/credenciais_admin.py

      dentro da lista ADMINISTRADORES.

=============================================================================
"""
import os
import sys
import getpass

# Garante que o pacote utilitarios esta no PATH
DIRETORIO = os.path.dirname(os.path.abspath(__file__))
if DIRETORIO not in sys.path:
    sys.path.insert(0, DIRETORIO)

try:
    from utilitarios.criptografia import gerar_hash_senha, calcular_forca_senha
except ImportError as exc:
    print()
    print("ERRO: nao foi possivel importar o modulo de criptografia.")
    print(f"Detalhes: {exc}")
    print()
    print("Execute este script de dentro da pasta do projeto.")
    sys.exit(1)


def linha(c="="):
    print(c * 75)


def main():
    linha()
    print("   GERADOR DE HASH DE SENHA - SISTEMA FACIL")
    linha()
    print()
    print("Este utilitario gera o hash bcrypt da senha de um administrador.")
    print("O hash e seguro de armazenar (nao pode ser revertido).")
    print()

    # Coleta dados do admin
    nome = input("Nome do administrador: ").strip()
    if not nome:
        nome = "Administrador"

    while True:
        email = input("E-mail do administrador (ex: joao@sistemafacil.pa.br): ").strip()
        if email and "@" in email:
            break
        print("  -> E-mail invalido. Tente novamente.")

    print()
    print("Agora digite a senha (nao sera exibida enquanto digita):")

    while True:
        try:
            senha = getpass.getpass("  Senha:           ")
            senha_conf = getpass.getpass("  Confirme a senha: ")
        except KeyboardInterrupt:
            print("\nCancelado pelo usuario.")
            sys.exit(0)

        if not senha:
            print("  -> Senha vazia. Tente novamente.")
            continue
        if len(senha) < 8:
            print("  -> Senha muito curta (minimo 8 caracteres).")
            continue
        if senha != senha_conf:
            print("  -> As senhas nao conferem. Tente novamente.")
            continue

        forca, descricao = calcular_forca_senha(senha)
        if forca < 2:
            print(f"  -> Senha fraca: {descricao}")
            resp = input("     Deseja continuar mesmo assim? (s/N): ").strip().lower()
            if resp != "s":
                continue
        else:
            print(f"  -> Forca da senha: {descricao}")
        break

    print()
    print("Gerando hash bcrypt (cost=12)... aguarde alguns segundos...")
    hash_bytes = gerar_hash_senha(senha)
    hash_str = hash_bytes.decode() if isinstance(hash_bytes, bytes) else str(hash_bytes)

    print()
    linha()
    print("   PRONTO! HASH GERADO COM SUCESSO")
    linha()
    print()
    print("Copie o bloco abaixo e cole-o na lista ADMINISTRADORES do arquivo:")
    print("   configuracoes_admin/credenciais_admin.py")
    print()
    linha("-")
    print("    {")
    print(f'        "email": "{email}",')
    print(f'        "nome":  "{nome}",')
    print(f'        "senha_hash": b"{hash_str}",')
    print("    },")
    linha("-")
    print()
    print("Lembre-se de manter a virgula no final da chave } da entrada anterior")
    print("e da nova entrada se houver outras depois.")
    print()
    print("Apos colar, salve o arquivo e reinicie o sistema.")
    print()

    # Oferece copia automatica para a area de transferencia (se possivel)
    bloco = (
        "    {\n"
        f'        "email": "{email}",\n'
        f'        "nome":  "{nome}",\n'
        f'        "senha_hash": b"{hash_str}",\n'
        "    },"
    )
    try:
        # Tenta copiar para a area de transferencia (Windows)
        if sys.platform == "win32":
            import subprocess
            subprocess.run(
                ["clip"], input=bloco.encode("utf-8"), check=True,
            )
            print(">>> Bloco copiado automaticamente para a area de transferencia! <<<")
            print("    (use Ctrl+V para colar no arquivo)")
            print()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelado pelo usuario.")
        sys.exit(0)
