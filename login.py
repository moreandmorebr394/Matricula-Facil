import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class LoginApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Fácil de Matrículas (SF)")
        self.root.geometry("1200x700")
        self.root.config(bg="#f5e6cc")
        
        self.create_widgets()

    def create_widgets(self):
        # Frame Principal
        main_frame = tk.Frame(self.root, bg="#f5e6cc", width=1200, height=700)
        main_frame.pack_propagate(False)  # Impede que o frame redimensione
        main_frame.pack()

        # Divisão do conteúdo
        left_frame = tk.Frame(main_frame, bg="#F5FDE9", width=480, height=700)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        right_frame = tk.Frame(main_frame, bg="#3C507D", width=720, height=700)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Logo e Título
        logo_label = tk.Label(left_frame, text="Sistema Fácil de Matrículas", font=("Times New Roman", 24), bg="#F5FDE9", fg="#EDC58F")
        logo_label.pack(pady=(20, 0))

        # Formulário de Login
        welcome_label = tk.Label(left_frame, text="Bem-vindo visitante!", font=("Arial", 18, 'bold'), fg="#112250", bg="#F5FDE9")
        welcome_label.pack(pady=(40, 20))

        self.username_entry = tk.Entry(left_frame, width=30, font=("Arial", 14), bg="#D9CBC2", borderwidth=2)
        self.username_entry.insert(0, "Digite seu usuário")
        self.username_entry.pack(pady=(5, 10))

        self.password_entry = tk.Entry(left_frame, show='*', width=30, font=("Arial", 14), bg="#D9CBC2", borderwidth=2)
        self.password_entry.insert(0, "Digite sua senha")
        self.password_entry.pack(pady=(5, 10))

        self.remember_me = tk.BooleanVar()
        remember_me_checkbox = tk.Checkbutton(left_frame, text="Manter-me conectado", variable=self.remember_me, bg="#F5FDE9")
        remember_me_checkbox.pack(side=tk.LEFT)

        password_reset_link = tk.Label(left_frame, text="Esqueci minha senha", fg="#112250", bg="#F5FDE9")
        password_reset_link.pack(side=tk.RIGHT)

        login_button = tk.Button(left_frame, text="Entrar", command=self.login, bg="#EDC58F", fg="#112250", font=("Arial", 14))
        login_button.pack(pady=20)

        separator_label = tk.Label(left_frame, text="OU ENTRE COM SEU USUÁRIO", fg="#D9CBC2", bg="#F5FDE9")
        separator_label.pack(pady=10)

        google_button = tk.Button(left_frame, text="Entrar com Google", command=self.login, bg="#D9CBC2", fg="#112250", font=("Arial", 14))
        google_button.pack(pady=10)

        help_label = tk.Label(left_frame, text="Precisa de ajuda? Fale conosco", bg="#F5FDE9")
        help_label.pack(side=tk.LEFT, padx=(10, 0))

        register_label = tk.Label(left_frame, text="Não tem uma conta? Cadastre-se", fg="#112250", bg="#F5FDE9")
        register_label.pack(side=tk.RIGHT)

        # Espaço para a Ilustração
        self.draw_illustration(right_frame)

    def draw_illustration(self, frame):
        # Carregar imagem do notebook (supondo que você tenha uma imagem)
        # imagem = Image.open("caminho_para_imagem/notebook.png")
        # imagem = imagem.resize((400, 300), Image.ANTIALIAS)
        # img = ImageTk.PhotoImage(imagem)

        # Placeholder de texto
        title_label = tk.Label(frame, text="Seu futuro começa com uma escolha simples", fg="#EDC58F", bg="#3C507D", font=("Arial", 16))
        title_label.pack(pady=20)

        # Simula a ilustração
        self.notebook_simulation(frame)

    def notebook_simulation(self, frame):
        canvas = tk.Canvas(frame, width=600, height=500, bg="#3C507D")
        canvas.pack()

        # Desenhar um retângulo representando o notebook
        canvas.create_rectangle(150, 150, 450, 400, fill="#D9CBC2", outline="#FFFFFF")

        # Título da tela do notebook
        canvas.create_text(300, 150, text="SF", font=("Times New Roman", 30), fill="#123B5D")

        # Simula o chapéu de formatura
        canvas.create_polygon(285, 75, 315, 75, 300, 50, fill="#123B5D")

    def login(self):
        user = self.username_entry.get()
        password = self.password_entry.get()
        if user and password:
            messagebox.showinfo("Sucesso", "Login bem-sucedido!")
        else:
            messagebox.showwarning("Atenção", "Por favor, preencha usuário e senha para continuar.")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginApp(root)
    root.mainloop()
