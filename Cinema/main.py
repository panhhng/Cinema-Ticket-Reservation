from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
import sqlite3

class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super(MenuScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text='Welcome to Cinema Booking System', font_size=70, size_hint_y=None, height=70))
        layout.add_widget(Label(text='Select a Film', font_size=60, size_hint_y=None, height=60))

        self.film_spinner = Spinner(text='Choose a film', values=['Film 1', 'Film 2', 'Film 3'], size_hint_y=None, height=40)
        layout.add_widget(self.film_spinner)

        next_button = Button(text='Next', size_hint_y=None, height=50)
        next_button.bind(on_release=lambda x: self.next_screen())
        layout.add_widget(next_button)

        self.add_widget(layout)

    def next_screen(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'seats'

class SeatSelectionScreen(Screen):
    def __init__(self, **kwargs):
        super(SeatSelectionScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        layout.add_widget(Label(text='Select Your Seats', font_size=24, size_hint_y=None, height=40))

        self.seat_grid = GridLayout(cols=10, rows=10, spacing=10, padding=10)
        layout.add_widget(self.seat_grid)

        bottom_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.total_price_label = Label(text='Total Price: $0', font_size=20)
        bottom_layout.add_widget(self.total_price_label)

        next_button = Button(text='Next', size_hint_x=None, width=100)
        next_button.bind(on_release=lambda x: self.next_screen())
        bottom_layout.add_widget(next_button)

        layout.add_widget(bottom_layout)
        self.add_widget(layout)

        self.selected_seats = []
        self.price_per_seat = 10 
        self.total_price = 0
        self.populate_seats()

    def populate_seats(self):
        self.seat_grid.clear_widgets()
        for row in range(10):
            for col in range(10):
                seat_button = Button(text=f'{row+1},{col+1}', on_release=self.select_seat)
                seat_button.background_color = (1, 1, 1, 1)
                seat_button.price = self.calculate_price(row, col)
                self.seat_grid.add_widget(seat_button)

    def select_seat(self, instance):
        if instance.background_color == [1, 1, 1, 1]: 
            instance.background_color = (0, 1, 0, 1) 
            self.selected_seats.append(instance)
            self.total_price += instance.price
        else:  
            instance.background_color = (1, 1, 1, 1)
            self.selected_seats.remove(instance)
            self.total_price -= instance.price
        self.update_total_price()

    def calculate_price(self, row, col):
        if row < 2:
            return self.price_per_seat * 1.5
        elif row < 4:
            return self.price_per_seat * 1.2
        else:
            return self.price_per_seat

    def update_total_price(self):
        self.total_price_label.text = f'Total Price: ${self.total_price}'

    def next_screen(self):
        self.manager.transition.direction = 'left'
        self.manager.current = 'confirmation'

class ConfirmationScreen(Screen):
    def __init__(self, **kwargs):
        super(ConfirmationScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        layout.add_widget(Label(text='Confirm Your Reservation', font_size=24, size_hint_y=None, height=40))

        self.customer_name_input = TextInput(hint_text='Enter your name', size_hint_y=None, height=40)
        layout.add_widget(self.customer_name_input)

        confirm_button = Button(text='Confirm', size_hint_y=None, height=50)
        confirm_button.bind(on_release=lambda x: self.confirm_reservation())
        layout.add_widget(confirm_button)

        self.add_widget(layout)

    def confirm_reservation(self):
        app = App.get_running_app()
        film = app.root.get_screen('menu').film_spinner.text
        seats = ','.join([btn.text for btn in app.root.get_screen('seats').selected_seats])
        customer_name = self.customer_name_input.text
        cursor = app.conn.cursor()
        cursor.execute('INSERT INTO reservations (film, seats, customer_name) VALUES (?, ?, ?)', (film, seats, customer_name))
        app.conn.commit()
        app.root.current = 'menu'

class CinemaApp(App):
    def build(self):
        self.conn = sqlite3.connect('cinema.db')
        self.create_tables()
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(SeatSelectionScreen(name='seats'))
        sm.add_widget(ConfirmationScreen(name='confirmation'))
        return sm

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS reservations (
            id INTEGER PRIMARY KEY,
            film TEXT,
            seats TEXT,
            customer_name TEXT
        )''')
        self.conn.commit()

if __name__ == '__main__':
    CinemaApp().run()