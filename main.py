from App import App
from components import Login
import json

if __name__ == "__main__":
    login = Login()
    login.run()

    if login.authenticated:
        app = App()
        app.run()
