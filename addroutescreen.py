from kivy.properties import StringProperty
from kivymd.app import MDApp
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.screen import MDScreen


class AddRouteScreen(MDScreen):
    type_car = StringProperty("Выберите тип машины")

    def back_main_screen(self):
        self.manager.current = 'main_screen'
        self.manager.transition.direction = 'right'

    def clear_input(self):
        self.type_car = "Выберите тип машины"
        self.ids.out.text = ""
        self.ids.in_1.text = ""

    def type_car_choose(self):
        type_car_list = [
            "легковая",
            "внежорожник",
            "грузовик",
            "автобус",
            "трейлер",
        ]

        menu_items = [
            {
                "text": f"{i}",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=f"{i}": self.type_car_item(x=x),
            } for i in type_car_list
        ]
        MDDropdownMenu(
            caller=self.ids.button,
            items=menu_items,
            width_mult=4,
        ).open()

    def type_car_item(self, x):
        self.type_car = x

    def add_route(self):
        app = MDApp.get_running_app()
        connect = app.connect
        cursor = app.cursor

        in_1 = self.ids.in_1.text
        out = self.ids.out.text

        cursor.execute(f"INSERT INTO list_name_data (name_list, type_car) VALUES ('{out} - {in_1}', '{self.type_car}')")
        connect.commit()
        query = cursor.execute("SELECT name_list, id, type_car FROM list_name_data ORDER BY ID DESC")
        app.check_data(query=query)
        self.back_main_screen()
        self.clear_input()
