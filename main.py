# main.py
from model import Database
from controller import Controller
from view import MainView

def main():
    model = Database()
    controller = Controller(model)
    app = MainView(controller)
    app.mainloop()
    model.close()

#Commentaire
if __name__ == '__main__':
    main()

