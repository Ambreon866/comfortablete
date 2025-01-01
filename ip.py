import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from playsound import playsound
import threading
from datetime import datetime
import os
import json

kivy.require('2.0.0')

# Получаем путь к AppData
APPDATA_DIR = os.path.join(os.path.expanduser("~"), "AppData", "Local", "ComfortableTE")
SETTINGS_FILE = os.path.join(APPDATA_DIR, 'settings.json')

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {'first_run': True}

def save_settings(settings):
    os.makedirs(APPDATA_DIR, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)

class Desktop(BoxLayout):
    def __init__(self, **kwargs):
        super(Desktop, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.settings = load_settings()
        if self.settings['first_run']:
            self.open_initial_setup()
        else:
            self.create_main_interface()

    def create_main_interface(self):
        self.clear_widgets()
        
        self.status_bar = BoxLayout(size_hint_y=None, height=50)
        self.add_widget(self.status_bar)

        self.time_label = Label(text='Время: --:--:--', color=(1, 1, 1, 1))
        self.status_bar.add_widget(self.time_label)

        self.app_button_bar = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.add_widget(self.app_button_bar)

        self.app_button_bar.add_widget(self.create_shortcut_button('MP3 Плеер', self.open_mp3_player))
        self.app_button_bar.add_widget(self.create_shortcut_button('Настройки', self.open_settings))
        self.app_button_bar.add_widget(self.create_shortcut_button('Мои файлы', self.open_file_manager))

        self.content_container = BoxLayout(orientation='vertical', spacing=10)
        self.add_widget(self.content_container)

        # Обновляем время каждую секунду
        Clock.schedule_interval(self.update_time, 1)
        self.update_time(0)

    def create_shortcut_button(self, text, callback):
        button = Button(text=text, on_press=callback, size_hint=(1, None), height=50)
        button.color = (1, 1, 1, 1)
        button.background_color = (0.2, 0.6, 0.8, 1)
        return button

    def update_time(self, dt):
        now = datetime.now()
        msk_time = now.strftime("%H:%M:%S")
        self.time_label.text = f'Время: {msk_time}'

    def open_initial_setup(self):
        self.clear_widgets()
        self.content_container = InitialSetup(self)
        self.add_widget(self.content_container)

    def open_mp3_player(self, instance):
        self.clear_widgets()
        self.content_container = MP3Player()
        self.add_widget(self.content_container)

    def open_settings(self, instance):
        self.clear_widgets()
        self.content_container = Settings()
        self.add_widget(self.content_container)

    def open_file_manager(self, instance):
        self.clear_widgets()
        self.content_container = FileManager()
        self.add_widget(self.content_container)

class InitialSetup(BoxLayout):
    def __init__(self, desktop, **kwargs):
        super(InitialSetup, self).__init__(**kwargs)
        self.desktop = desktop
        self.orientation = 'vertical'

        self.add_widget(Label(text='Первоначальная настройка', font_size=24))

        self.license_label = Label(text='Лицензионное соглашение GNU GPL v3:\n\n'
                                         'Это программное обеспечение лицензируется под лицензией GNU GPL v3. '
                                         'Вы можете свободно использовать, изменять и распространять его, '
                                         'при условии соблюдения условий лицензии.\nБлог в ТГ: t.me/blogkvazi2, блог в Blogger: https://ambreon866.blogspot.com/', size_hint_y=None, height=200)
        self.add_widget(self.license_label)

        self.accept_button = Button(text='Принять и продолжить', on_press=self.accept_license, size_hint=(1, None), height=50)
        self.add_widget(self.accept_button)

    def accept_license(self, instance):
        self.desktop.settings['first_run'] = False
        save_settings(self.desktop.settings)
        self.desktop.create_main_interface()

class MP3Player(BoxLayout):
    def __init__(self, **kwargs):
        super(MP3Player, self).__init__(**kwargs)
        self.orientation = 'vertical'

        self.label = Label(text='Выберите MP3 файл', color=(1, 1, 1, 1))
        self.add_widget(self.label)

        self.file_chooser = FileChooserListView(filters=['*.mp3'], size_hint_y=None, height=300)
        self.file_chooser.bind(on_selection=self.load_mp3)
        self.add_widget(self.file_chooser)

        self.button_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        self.add_widget(self.button_layout)

        self.play_button = Button(text='Играть', on_press=self.play_music, size_hint=(1, None), height=50)
        self.button_layout.add_widget(self.play_button)

        self.stop_button = Button(text='Стоп', on_press=self.stop_music, size_hint=(1, None), height=50)
        self.button_layout.add_widget(self.stop_button)

        self.current_file = None

    def load_mp3(self, filechooser, selection):
        if selection:
            self.current_file = selection[0]
            self.label.text = f'Выбран файл: {self.current_file}'

    def play_music(self, instance):
        if self.current_file:
            try:
                threading.Thread(target=self._play_sound).start()
                self.label.text = f'Воспроизводится: {self.current_file}'
            except Exception as e:
                self.label.text = f'Ошибка воспроизведения: {str(e)}'

    def _play_sound(self):
        try:
            playsound(self.current_file)
        except Exception as e:
            self.label.text = f'Ошибка воспроизведения: {str(e)}'

    def stop_music(self, instance):
        self.label.text = 'Стоп'

class Settings(BoxLayout):
    def __init__(self, **kwargs):
        super(Settings, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.add_widget(Label(text='Настройки', color=(1, 1, 1, 1)))

        self.secret_input = TextInput(hint_text='Введите код для пасхалки', size_hint_y=None, height=50)
        self.add_widget(self.secret_input)

        self.check_button = Button(text='Проверить код', on_press=self.check_secret, size_hint=(1, None), height=50)
        self.add_widget(self.check_button)

    def check_secret(self, instance):
        if self.secret_input.text == 'секрет':
            popup = Popup(title='Пасхалка', content=Label(text='Вы нашли пасхалку!'), size_hint=(0.6, 0.4))
            popup.open()
        else:
            popup = Popup(title='Ошибка', content=Label(text='Неверный код!'), size_hint=(0.6, 0.4))
            popup.open()

class FileManager(BoxLayout):
    def __init__(self, **kwargs):
        super(FileManager, self).__init__(**kwargs)
        self.orientation = 'vertical'
        self.file_chooser = FileChooserListView(size_hint_y=None, height=300)
        self.add_widget(self.file_chooser)

        self.open_button = Button(text='Открыть', on_press=self.open_file, size_hint=(1, None), height=50)
        self.add_widget(self.open_button)

    def open_file(self, instance):
        selected = self.file_chooser.selection
        if selected:
            try:
                os.startfile(selected[0])  # Это работает только на Windows
            except Exception as e:
                popup = Popup(title='Ошибка', content=Label(text=f'Не удалось открыть файл: {str(e)}'), size_hint=(0.6, 0.4))
                popup.open()

class comfortablete(App):
    def build(self):
        return Desktop()

if __name__ == '__main__':
   comfortablete().run()
