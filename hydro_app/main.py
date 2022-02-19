from kivy.app import App
from kivy.uix.gridlayout import GridLayout


class MainScreen(GridLayout):
    pass


class HydroApp(App):
    def build(self):
        return MainScreen()


def main():
    HydroApp().run()


if __name__ == "__main__":
    main()
