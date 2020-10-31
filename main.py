import kivy
from kivy.app import App as KivyApp
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

from modules.api import Api
from modules.utils import format_load, format_name, format_temp

kivy.require("1.11.1")

Config.read("config.ini")


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
    def __init__(self, pos_hint):
        super(Temperature, self).__init__()

        self.text = format_temp(0)
        self.font_size = "110sp"
        self.pos_hint = pos_hint
        self.halign = "center"
        self.color = (.3, .55, 0.689, 1)


class Name(Label):
    def __init__(self, name, pos_hint):
        super(Name, self).__init__()

        self.text = format_name(name)
        self.font_size = "18sp"
        self.pos_hint = pos_hint
        self.halign = "center"
        self.color = (.3, .55, 0.689, 1)
        self.markup = True


class Load(Label):
    def __init__(self, pos_hint):
        super(Load, self).__init__()

        self.text = f"[b]Load:[/b] 0/0/0"
        self.font_size = "14sp"
        self.pos_hint = pos_hint
        self.color = (.3, .55, 0.689, 1)
        self.markup = True
        self.text_size = (180, None)


class ConnectionInfo(Label):
    def __init__(self, hostname):
        super(ConnectionInfo, self).__init__()

        self.text = f"Connected to: [b]{hostname}[/b]"
        self.font_size = "12sp"
        self.pos_hint = {"x": 0, "y": -.415}
        self.halign = "center"
        self.color = (.3, .55, 0.689, .5)
        self.markup = True


class App(FloatLayout):
    def __init__(self):
        super(App, self).__init__()

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
                {"x": -.225, "y": .155}
            )
        )

        self.cpu_temp = Temperature({"x": -.21, "y": -.0195})
        self.add_widget(self.cpu_temp)

        self.cpu_load = Load({"x": -.195, "y": -.175})
        self.add_widget(self.cpu_load)

        # GPU section
        self.add_widget(
            Name(
                self._vitals[1]["name"],
                {"x": .225, "y": .155}
            )
        )

        self.gpu_temp = Temperature({"x": .24, "y": -.0195})
        self.add_widget(self.gpu_temp)

        self.gpu_load = Load({"x": .255, "y": -.175})
        self.add_widget(self.gpu_load)

        self.add_widget(
            ConnectionInfo(Config.get("server", "hostname"))
        )

    def update(self, *args):
        self._vitals = self._api.get()
        self.cpu_temp.text = format_temp(self._vitals[0]["sensors"][0]["val"])
        self.cpu_load.text = f"[b]Load [/b] " + format_load(self._vitals[0]["sensors"][1])
        self.gpu_temp.text = format_temp(self._vitals[1]["sensors"][0]["val"])
        self.gpu_load.text = f"[b]Load [/b] " + format_load(self._vitals[1]["sensors"][1])


class PymonitClient(KivyApp):
    def build(self):
        app = App()
        Clock.schedule_interval(app.update, 1)
        return app


if __name__ == '__main__':
    PymonitClient().run()
