import kivy
from kivy.app import App as KivyApp
from kivy.clock import Clock
from kivy.config import Config
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.utils import rgba

from modules.api import Api
from modules.utils import format_load, format_name, format_temp

kivy.require("1.11.1")

Config.read("config.ini")

Window.size = (
    int(Config.get("graphics", "width")),
    int(Config.get("graphics", "height"))
)


class Background(Image):
    def __init__(self, src):
        super(Background, self).__init__()

        self._size = (
            Config.get("graphics", "width"),
            Config.get("graphics", "height")
        )
        self.texture_size = self._size
        self.source = src


class Temperature(Label):
    def __init__(self, pos):
        super(Temperature, self).__init__()

        self.text = format_temp(0)
        self.font_name = Config.get("theme", "font_temperature")
        self.font_size = "160sp"
        self.pos = pos
        self.halign = "center"
        self.color = rgba(Config.get("theme", "color_main"))


class Name(Label):
    def __init__(self, name, pos):
        super(Name, self).__init__()

        self.text = format_name(name)
        self.font_name = Config.get("theme", "font_info")
        self.font_size = "18sp"
        self.pos = pos
        self.halign = "center"
        self.color = rgba(Config.get("theme", "color_main"))
        self.markup = True


class Load(Label):
    def __init__(self, pos):
        super(Load, self).__init__()

        self.text = f"[b]Load:[/b] 0/0/0"
        self.font_name = Config.get("theme", "font_info")
        self.font_size = "14sp"
        self.pos = pos
        self.halign = "center"
        self.color = rgba(Config.get("theme", "color_main"))
        self.markup = True
        self.text_size = (200, None)


class ConnectionInfo(Label):
    def __init__(self, hostname):
        super(ConnectionInfo, self).__init__()

        self.text = f"Connected to:\n[b]{hostname}[/b]"
        self.font_name = Config.get("theme", "font_info")
        self.font_size = "12sp"
        self.pos = (0, -377)
        self.halign = "center"
        self.color = rgba(Config.get("theme", "color_main"))
        self.markup = True


class App(RelativeLayout):
    def __init__(self):
        super(App, self).__init__()

        self.size = (480, 800)

        self._api = Api(
            Config.get("server", "hostname"),
            Config.getint("server", "port"),
            Config.get("server", "protocol")
        )
        self._vitals = self._api.get()

        self.add_widget(
            Background(Config.get("theme", "background_image"))
        )

        # CPU section
        self.add_widget(
            Name(
                self._vitals[0]["name"],
                (0, 240)
            )
        )

        self.cpu_temp = Temperature((0, 140))
        self.add_widget(self.cpu_temp)

        self.cpu_load = Load((0, 50))
        self.add_widget(self.cpu_load)

        # GPU section
        self.add_widget(
            Name(
                self._vitals[1]["name"],
                (0, -60)
            )
        )

        self.gpu_temp = Temperature((0, -160))
        self.add_widget(self.gpu_temp)

        self.gpu_load = Load((0, -250))
        self.add_widget(self.gpu_load)

        self.add_widget(
            ConnectionInfo(Config.get("server", "hostname"))
        )

    def update(self, *args):
        try:
            self._vitals = self._api.get()
            self.cpu_temp.text = format_temp(self._vitals[0]["sensors"][0]["val"])
            self.cpu_load.text = f"[b]Load [/b] " + format_load(self._vitals[0]["sensors"][1])
            self.gpu_temp.text = format_temp(self._vitals[1]["sensors"][0]["val"])
            self.gpu_load.text = f"[b]Load [/b] " + format_load(self._vitals[1]["sensors"][1])
        except:
            pass


class PymonitClient(KivyApp):
    def build(self):
        app = App()
        Clock.schedule_interval(app.update, 1)
        return app


if __name__ == '__main__':
    PymonitClient().run()
