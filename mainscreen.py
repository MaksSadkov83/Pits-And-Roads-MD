from kivymd.uix.screen import MDScreen


class MainScreen(MDScreen):
    def add_new_route(self):
        self.manager.current = 'add_route'
        self.manager.transition.direction = 'left'
