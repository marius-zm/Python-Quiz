from App import App
from components import Login

if __name__ == "__main__":
    login = Login()
    login.run()

    if login.authenticated:
        app = App(login)
        app.run()
