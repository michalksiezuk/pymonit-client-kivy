import asyncio

import aiohttp
import kivy
from kivy.app import App as KivyApp
from kivy.clock import Clock
from kivy.config import Config
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label

kivy.require('1.11.1')

Config.read("config.ini")

# TODO private members, extract all widgets as classes, organize App


class Formatters:
    @staticmethod
    def format_temp(value):
        return f"{str(round(value))}\u00b0"

    @staticmethod
    def format_name(text):
        words = text.split()
        brand = words.pop(0)
        model = " ".join(words)
        return f"[b]{brand}[/b]\n{model}"

    @staticmethod
    def format_load(values):
        load_current = round(values["val"], 1)
        load_min = round(values["min"], 1)
        load_max = round(values["max"], 1)
        return f"{load_current} / {load_min} / {load_max}"


class Api:
    def __init__(self, hostname, port, protocol):
        self._endpoint = f"{protocol}://{hostname}:{port}"
        self._loop = asyncio.get_event_loop()

    async def _async_get(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self._endpoint) as response:
                    return await response.json()
            except aiohttp.ClientConnectorError as error:
                print('Connection Error', str(error))

    def get(self):
        return self._loop.run_until_complete(self._async_get())


class ConnectionInfo(Label):
    def __init__(self, hostname, **kwargs):
        super(ConnectionInfo, self).__init__(**kwargs)

        self.text = f"Connected to: [b]{hostname}[/b]"
        self.font_size = "12sp"
        self.pos_hint = {"x": 0, "y": -.415}
        self.halign = "center"
        self.color = (.3, .55, 0.689, .5)
        self.markup = True


class Background(Image):
    def __init__(self, src, **kwargs):
        super(Background, self).__init__(**kwargs)

        self._size = (
            Config.get("graphics", "width"),
            Config.get("graphics", "height")
        )
        self.texture_size = self._size
        self.source = src


class App(FloatLayout):
    def __init__(self, **kwargs):
        super(App, self).__init__(**kwargs)

        self._api = Api(
            Config.get("server", "hostname"),
            Config.getint("server", "port"),
            Config.get("server", "protocol")
        )
        self._vitals = self._api.get()

        self.add_widget(
            Background(src=Config.get("theme", "background_image"))
        )

        self.add_widget(
            ConnectionInfo(hostname=Config.get("server", "hostname"))
        )

        # CPU section
        self.cpu_name = Label(
            text=Formatters.format_name(self._vitals[0]["name"]),
            font_size="18sp",
            pos_hint={"x": -.225, "y": .155},
            halign="center",
            color=(.3, .55, 0.689, 1),
            markup=True
        )
        self.add_widget(self.cpu_name)

        self.cpu_temp = Label(
            text=Formatters.format_temp(0),
            font_size="110sp",
            pos_hint={"x": -.21, "y": -.0195},
            halign="center",
            color=(.3, .55, 0.689, 1),
        )
        self.add_widget(self.cpu_temp)

        self.cpu_load = Label(
            text=f"[b]Load:[/b] 0/0/0",
            font_size="14sp",
            pos_hint={"x": -.195, "y": -.175},
            color=(.3, .55, 0.689, 1),
            markup=True,
            text_size=(180, None)
        )
        self.add_widget(self.cpu_load)

        # GPU section
        self.gpu_name = Label(
            text=Formatters.format_name(self._vitals[1]["name"]),
            font_size="18sp",
            pos_hint={"x": .225, "y": .155},
            halign="center",
            color=(.3, .55, 0.689, 1),
            markup=True
        )
        self.add_widget(self.gpu_name)

        self.gpu_temp = Label(
            text=Formatters.format_temp(0),
            font_size="110sp",
            pos_hint={"x": .24, "y": -.0195},
            halign="center",
            color=(.3, .55, 0.689, 1)
        )
        self.add_widget(self.gpu_temp)

        self.gpu_load = Label(
            text=f"[b]Load:[/b] 0 / 0 / 0",
            font_size="14sp",
            pos_hint={"x": .255, "y": -.175},
            color=(.3, .55, 0.689, 1),
            markup=True,
            text_size=(180, None)
        )
        self.add_widget(self.gpu_load)

    def update(self, *args):
        self._vitals = self._api.get()
        self.cpu_temp.text = Formatters.format_temp(self._vitals[0]["sensors"][0]["val"])
        self.cpu_load.text = f"[b]Load [/b] " + Formatters.format_load(self._vitals[0]["sensors"][1])
        self.gpu_temp.text = Formatters.format_temp(self._vitals[1]["sensors"][0]["val"])
        self.gpu_load.text = f"[b]Load [/b] " + Formatters.format_load(self._vitals[1]["sensors"][1])


class PymonitClient(KivyApp):
    def build(self):
        app = App()
        Clock.schedule_interval(app.update, 1)
        return app


if __name__ == '__main__':
    PymonitClient().run()
