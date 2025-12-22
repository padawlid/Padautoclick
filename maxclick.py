import time
import tkinter as tk
from tkinter import ttk
import threading
import win32api
import win32con
import ctypes
import sys
from pynput import mouse

# Vérifier et forcer les privilèges administrateur
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, " ".join(sys.argv), None, 1
    )
    sys.exit()

# ================= AUTOCLICKER =================
class AutoClicker:
    def __init__(self):
        self.enabled = False
        self.cps = 17
        self.clicking = False
        self.event_history = []

        # GUI minimale
        self.root = tk.Tk()
        self.root.title("Autoclicker CPS")
        self.root.geometry("350x200")
        self.root.resizable(False, False)

        self.setup_ui()

        # Listener souris
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_event)
        self.mouse_listener.start()

        # Thread clic
        threading.Thread(target=self.main_loop, daemon=True).start()

        # Thread détection touche R
        threading.Thread(target=self.keyboard_poll, daemon=True).start()

    # ---------------- UI ----------------
    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=15)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="Autoclicker CPS", font=("Arial", 16, "bold")).pack(pady=5)

        self.status_label = ttk.Label(frame, text="🔴 DÉSACTIVÉ", font=("Arial", 12, "bold"), foreground="red")
        self.status_label.pack(pady=5)

        ttk.Label(frame, text="CPS").pack()
        self.cps_label = ttk.Label(frame, text=f"{self.cps} CPS")
        self.cps_label.pack()

        self.cps_slider = ttk.Scale(frame, from_=1, to=1000, orient=tk.HORIZONTAL,
                                    command=self.update_cps, length=300)
        self.cps_slider.set(self.cps)
        self.cps_slider.pack(pady=10)

        ttk.Label(frame, text="R = Toggle | Maintenir clic gauche", font=("Arial", 9)).pack(pady=5)

    def update_cps(self, value):
        self.cps = int(float(value))
        self.cps_label.config(text=f"{self.cps} CPS")

    # ---------------- TOGGLE R ----------------
    def keyboard_poll(self):
        VK_R = 0x52
        last_state = False

        while True:
            state = (ctypes.windll.user32.GetAsyncKeyState(VK_R) & 0x8000) != 0

            if state and not last_state:
                self.toggle()

            last_state = state
            time.sleep(0.05)

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.status_label.config(text="🟢 ACTIVÉ", foreground="green")
        else:
            self.status_label.config(text="🔴 DÉSACTIVÉ", foreground="red")
            self.clicking = False

    # ---------------- SOURIS ----------------
    def on_mouse_event(self, x, y, button, pressed):
        if button == mouse.Button.left:
            event = "DOWN" if pressed else "UP"
            self.event_history.append(event)

            if len(self.event_history) > 3:
                self.event_history.pop(0)

            if pressed and self.enabled:
                self.clicking = True

            if len(self.event_history) >= 2:
                if self.event_history[-1] == "UP" and self.event_history[-2] == "UP":
                    self.clicking = False

    # ---------------- CLIC PUR ----------------
    def pure_click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)

    # ---------------- BOUCLE PRINCIPALE ----------------
    def main_loop(self):
        while True:
            if self.enabled and self.clicking:
                self.pure_click()

                delay = 1.0 / self.cps
                if delay > 0.001:
                    time.sleep(delay)
            else:
                time.sleep(0.01)

    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        self.enabled = False
        self.clicking = False
        self.mouse_listener.stop()
        self.root.destroy()

# ================= MAIN =================
if __name__ == "__main__":
    print("Autoclicker CPS - Version propre")
    app = AutoClicker()
    app.run()
