from dynamic_case_runner import run_station  # <-- This is your MVP entry point
from kivy.app import App
from kivy.uix.button import Button
import sys
import os

# Add parent folder to Python path so your real app files can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class UKMLAApp(App):
    def build(self):
        return Button(text="🎤 Start UKMLA Station", on_press=self.start_mvp)

    def start_mvp(self, instance):
        run_station()


if __name__ == "__main__":
    UKMLAApp().run()
