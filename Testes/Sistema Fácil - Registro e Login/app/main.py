from app.controller.auth_controller import AuthController
from app.view.auth_view import AuthView

def main():
    # 1. Instancia o Controller
    controller = AuthController()
    
    # 2. Instancia a View passando o Controller
    view = AuthView(controller)
    
    # 3. Informa ao Controller qual é a View (Injeção de dependência)
    controller.set_view(view)
    
    # 4. Roda o loop principal do Tkinter
    view.mainloop()

if __name__ == "__main__":
    main()