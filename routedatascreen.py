import time

from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.properties import ObjectProperty
from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.label import MDLabel
from kivymd.uix.screen import MDScreen
from kivy.properties import StringProperty
from kivy_garden.mapview import MapMarkerPopup
from kivymd.uix.widget import MDWidget


class RouteDataScreen(MDScreen):
    name_list = StringProperty("Добавление маршрута")
    start_move_clock = None
    info_dialog = None
    update_line_1 = None

    def __init__(self, id, name):
        super().__init__()
        setattr(self, 'name', name)
        self.id = id
        self.app = MDApp.get_running_app()
        self.cursor = self.app.cursor
        self.connect = self.app.connect
        query = self.cursor.execute(f"SELECT name_list FROM list_name_data WHERE id={self.id}")
        name_list = query.fetchone()
        self.name_list = str(name_list[0])
        self.gps_point = list()
        self.data_gir_point = list()
        self.line_points = list()
        self.marker_point = list()
        self.mapview = self.ids.map
        query = self.cursor.execute(f"SELECT data FROM data_gps_list WHERE id_list={self.id}")
        self.data = query.fetchall()
        if len(self.data) == 0:
            self.ids.stop.disabled = 'True'
        else:
            self.ids.add.disabled = 'True'
            self.ids.stop.disabled = 'True'

            data = self.data[0][0].split(' ')
            min_lat, min_lon, max_lat, max_lon = self.mapview.get_bbox()

            for i in data:
                i = i.split(":")
                if len(i) > 1:
                    self.gps_point.append(i[0])
                    gps_data = i[0].split(",")
                    gir_data = i[1].split(",")
                    datetime_data = i[2].split(".")

                    lat = float(gps_data[0])
                    lon = float(gps_data[1])

                    marker = MapMarkerPopup(lat=lat, lon=lon, source='marker.png')

                    widget = MDWidget(
                        size_hint=[0.9, None],
                        height=self.width,
                        md_bg_color="black"
                    )

                    label = MDLabel(
                        text=f"X: {gir_data[0]}, Y: {gir_data[1]}, Z: {gir_data[2]}\n"
                             f"Дата: {datetime_data[0]}.{datetime_data[1]}.{datetime_data[2]} "
                             f"{datetime_data[3]}:{datetime_data[4]}:{datetime_data[5]}"
                    )

                    widget.add_widget(label)

                    marker.add_widget(widget)

                    self.mapview.add_widget(marker)
                    self.marker_point.append(marker)

            # Clock.schedule_once(self.get_point, 2)

    def back_main_screen(self):
        self.manager.current = 'main_screen'
        self.manager.transition.direction = 'right'

    def clear_list(self):
        if len(self.marker_point) > 0:
            if self.update_line_1 is not None:
                self.update_line_1.cancel()
            for i in self.marker_point:
                self.mapview.remove_marker(i)

            for i in self.line_points:
                self.canvas.remove(i)

            self.line_points = []
            self.marker_point = []

            self.cursor.execute(f"DELETE FROM data_gps_list WHERE id_list={self.id}")
            self.connect.commit()
            self.ids.add.disabled = not self.ids.add.disabled
        else:
            self.info_dialog = MDDialog(
                title="Записей нет",
                text="Зaписей в базе данных нет по данному маршруту",
                buttons=[
                    MDFlatButton(
                        text='Назад',
                        theme_text_color="Custom",
                        text_color='#009688',
                        on_release=self.close_info_dialog,
                    ),
                ],
                auto_dismiss=False,
            )
            self.info_dialog.open()

    def get_point(self, dt):
        with self.canvas:
            Color(1, 0, 0.3, 0.6)
            for i in range(0, len(self.marker_point) - 1):
                line = Line(points=(
                self.marker_point[i].center_x, self.marker_point[i].y, self.marker_point[i + 1].center_x, self.marker_point[i + 1].y), width=5)
                self.line_points.append(line)
        self.update_line_1 = Clock.schedule_interval(self.update_line, 1 / 60)

    def update_line(self, dt):
        for i in range(0, len(self.line_points), 1):
            self.line_points[i - 1].points = [self.marker_point[i - 1].center_x, self.marker_point[i - 1].y,
                                              self.marker_point[i].center_x, self.marker_point[i].y]

    def start_moving(self):
        if self.info_dialog is None:
            self.info_dialog = MDDialog(
                title="Вы нажали кнопку 'Начать движение'",
                text="После нажатия кнопки 'Продолжить' запуститья гироскоп и gps, "
                     "закрепите ваш телефон на одном месте и постарайтесь его не трогать до окончания движения. \n"
                     "После достижения конечной точки не забудьте нажать кнопку 'Закончить движение'.",
                buttons=[
                    MDFlatButton(
                        text='Продолжить',
                        theme_text_color="Custom",
                        text_color='#009688',
                        on_release=self.start_move_gps,
                    ),
                    MDFlatButton(
                        text='Назад',
                        theme_text_color="Custom",
                        text_color='#009688',
                        on_release=self.close_info_dialog,
                    ),
                ],
                auto_dismiss=False,
            )
            self.info_dialog.open()

    def stop_moving(self):
        if self.info_dialog is None:
            self.info_dialog = MDDialog(
                title="Вы нажали кнопку 'Закончить движение'",
                text="После нажатия кнопки 'Продолжить' запись данных остановиться. "
                     "Добавить новые данные будет не возможно. Для их добавления придется очистить базу этого марщрута. \n"
                     "Вы уверены, что хотите остановить запись?",
                buttons=[
                    MDFlatButton(
                        text='Продолжить',
                        theme_text_color="Custom",
                        text_color='#009688',
                        on_release=self.stop_move_gps,
                    ),
                    MDFlatButton(
                        text='Назад',
                        theme_text_color="Custom",
                        text_color='#009688',
                        on_release=self.close_info_dialog,
                    ),
                ],
                auto_dismiss=False,
            )
            self.info_dialog.open()

    def close_info_dialog(self, *args):
        self.info_dialog.dismiss()
        self.info_dialog = None

    def start_move_gps(self, *args):
        self.close_info_dialog()
        self.ids.add.disabled = "True"
        self.ids.stop.disabled = not self.ids.stop.disabled
        self.start_move_clock = Clock.schedule_interval(self.add_data_gps_gir, 1)

    def stop_move_gps(self, *args):
        self.close_info_dialog()
        self.ids.stop.disabled = "True"
        data = ""
        for i in range(0, len(self.gps_point)):
            data += self.gps_point[i] + ":" + self.data_gir_point[i] + " "
        self.cursor.execute(
            f"INSERT INTO data_gps_list (id_list, data) VALUES ({int(self.id)}, '{data}')"
        )
        self.gps_point = []
        self.data_gir_point = []
        # self.update_line_1 = Clock.schedule_interval(self.get_point, 3)
        self.start_move_clock.cancel()
        self.connect.commit()

    def add_data_gps_gir(self, dt):
        lat = self.app.gps_lat
        lon = self.app.gps_lon
        if f"{lat},{lon}" not in self.gps_point:
            x, y, z = self.app.gir_x, self.app.gir_y, self.app.gir_z
            x, y, z = round(x, 4), round(y, 4), round(z, 4)
            year, month, day, hour, minute, second = time.localtime()[:6]
            marker = MapMarkerPopup(
                lat=lat,
                lon=lon,
                source="marker.png",
            )

            widget = MDWidget(
                size_hint=[1, 0.9],
                md_bg_color="black"
            )

            label = MDLabel(
                text=f"X: {x}, Y: {y}, Z: {z}\n"
                     f"Дата: {day}.{month}.{year} "
                     f"{hour}:{minute}:{second}"
            )

            widget.add_widget(label)

            marker.add_widget(widget)
            self.marker_point.append(marker)
            self.mapview.add_widget(marker)
            self.gps_point.append(f"{lat},{lon}")
            self.data_gir_point.append(f"{x},{y},{z}:{day}.{month}.{year}.{hour}.{minute}.{second}")
