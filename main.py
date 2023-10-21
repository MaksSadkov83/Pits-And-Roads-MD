import os
os.environ["KIVY_NO_CONSOLELOG"] = "1"

from kivymd.app import MDApp
from kivymd.uix.button import MDFlatButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineListItem, IconRightWidget, TwoLineAvatarIconListItem
import sqlite3
from plyer import gps, gyroscope
from kivy.clock import mainthread, Clock
from kivy.properties import NumericProperty
from routedatascreen import RouteDataScreen
from addroutescreen import AddRouteScreen
from mainscreen import MainScreen


class CheckerRoadApp(MDApp):
    connect = None
    cursor = None
    info_diolog = None
    gps_lat = 67.633
    gps_lon = 52.988
    gir_x = NumericProperty(0)
    gir_y = NumericProperty(0)
    gir_z = NumericProperty(0)

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Teal"

    def check_data(self, query):
        data = query.fetchmany(10)

        list_route = self.root.ids.main_screen.ids.list_route

        if len(data) == 0:
            list_route.clear_widgets()
            list_route.add_widget(
                OneLineListItem(text="База пуста")
            )
        else:
            list_route.clear_widgets()
            for i in data:
                right_icon = IconRightWidget(
                    id=str(i[1]),
                    icon="minus",
                    on_release=self.delete_road,
                )

                item = TwoLineAvatarIconListItem(
                    id=str(i[1]),
                    text=i[0],
                    secondary_text=f"Тип машины: {i[2]}",
                    on_release=self.open_road,
                )

                item.add_widget(right_icon)

                list_route.add_widget(item)

    def on_start(self):
        from android.permissions import request_permissions, Permission
        request_permissions([Permission.ACCESS_FINE_LOCATION, Permission.ACCESS_COARSE_LOCATION])
        self.connect = sqlite3.connect("test_checker.db")
        self.cursor = self.connect.cursor()

        query = self.cursor.execute("SELECT name_list, id, type_car FROM list_name_data ORDER BY ID DESC")
        self.check_data(query=query)

        try:
            gps.configure(on_location=self.on_location,
                          on_status=self.on_status)
            gps.start(minTime=1000, minDistance=0)
        except NotImplementedError:
            if self.info_diolog is None:
                self.info_diolog = MDDialog(
                    title='GPS не поддерживается вашей платформой',
                    text='GPS не подерживается вашей платформой так-что некоторые функции не будут работать',
                    buttons=[
                        MDFlatButton(
                            text='OK',
                            theme_text_color="Custom",
                            text_color='#009688',
                            on_release=self.close_info_dialog,
                        ),
                    ],
                    auto_dismiss=False,
                )
                self.info_diolog.open()

        try:
            gyroscope.enable()
            Clock.schedule_interval(self.get_rotation, 1)
        except NotImplementedError:
            if self.info_diolog is None:
                self.info_diolog = MDDialog(
                    title='Гироскоп не поддерживается вашей платформой',
                    text='Гироскоп не подерживается вашей платформой так-что некоторые функции не будут работать',
                    buttons=[
                        MDFlatButton(
                            text='OK',
                            theme_text_color="Custom",
                            text_color='#009688',
                            on_release=self.close_info_dialog,
                        ),
                    ],
                    auto_dismiss=False,
                )
                self.info_diolog.open()

    def delete_road(self, road):
        self.cursor.execute(f"DELETE FROM data_gps_list WHERE id_list={road.id}")
        self.cursor.execute(f"DELETE FROM list_name_data WHERE id={road.id}")

        self.connect.commit()

        query = self.cursor.execute("SELECT name_list, id, type_car FROM list_name_data ORDER BY ID DESC")

        self.check_data(query=query)

    @mainthread
    def on_location(self, **kwargs):
        self.gps_lat = round(kwargs['lat'], 4)
        self.gps_lon = round(kwargs['lon'], 4)

    @mainthread
    def on_status(self, stype, status):
        if stype == 'provider-disabled' and self.info_diolog is None:
            self.info_diolog = MDDialog(
                title='Пожалуйста включите геолакацию',
                buttons=[
                    MDFlatButton(
                        text='OK',
                        theme_text_color="Custom",
                        text_color='#009688',
                        on_release=self.close_info_dialog,
                    ),
                ],
                auto_dismiss=False,
            )
            self.info_diolog.open()

    def open_road(self, road):
        if self.root.has_screen(str(road.id)):
            self.root.current = str(road.id)
            self.root.transition.direction = 'left'
        else:
            screen_data = RouteDataScreen(name=str(road.id), id=road.id)
            self.root.add_widget(screen_data)
            self.root.current = str(road.id)
            self.root.transition.direction = 'left'

    def get_rotation(self, dt):
        if gyroscope.rotation != (None, None, None):
            self.gir_x, self.gir_y, self.gir_z = gyroscope.rotation

    def close_info_dialog(self, *args):
        self.info_diolog.dismiss()
        self.info_diolog = None


if __name__ == '__main__':
    CheckerRoadApp().run()
