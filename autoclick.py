import time
import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import win32api
import win32con
from pynput import mouse

# ---------------- AutoClicker ----------------
class AutoClicker:
    def __init__(self):
        self.enabled = False
        self.cps = 20
        self.clicking = False
        self.event_history = []
        
        # GUI
        self.root = tk.Tk()
        self.root.title("Autoclicker PvP")
        self.root.geometry("350x200")
        self.root.resizable(False, False)
        self.setup_ui()
        
        # Hotkey R
        keyboard.add_hotkey('r', self.toggle)
        
        # Listener souris pour détecter les événements
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_event)
        self.mouse_listener.start()
        
        # Thread click
        threading.Thread(target=self.main_loop, daemon=True).start()
    
    def setup_ui(self):
        frame = ttk.Frame(self.root, padding=20)
        frame.pack(expand=True)
        
        ttk.Label(frame, text="⚔️ Autoclicker PvP", font=("Arial", 16, "bold")).pack(pady=10)
        
        self.status_label = ttk.Label(frame, text="🔴 DÉSACTIVÉ", font=("Arial", 12), foreground="red")
        self.status_label.pack(pady=5)
        
        ttk.Label(frame, text="CPS").pack()
        
        self.cps_label = ttk.Label(frame, text=f"{self.cps} CPS")
        self.cps_label.pack(pady=5)
        
        self.cps_slider = ttk.Scale(frame, from_=1, to=500, orient=tk.HORIZONTAL,
                                    command=self.update_cps, length=200)
        self.cps_slider.set(self.cps)
        self.cps_slider.pack(pady=5)
        
        ttk.Label(frame, text="R = Toggle | Maintenez clic gauche").pack(pady=10)
    
    def update_cps(self, value):
        self.cps = int(float(value))
        self.cps_label.config(text=f"{self.cps} CPS")
    
    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.status_label.config(text="🟢 ACTIVÉ", foreground="green")
            print("✅ ACTIVÉ")
        else:
            self.status_label.config(text="🔴 DÉSACTIVÉ", foreground="red")
            self.clicking = False
            print("❌ DÉSACTIVÉ")
    
    def on_mouse_event(self, x, y, button, pressed):
        # Détecter les événements DOWN et UP
        if button == mouse.Button.left:
            event = "DOWN" if pressed else "UP"
            self.event_history.append(event)
            
            # Garder seulement les 3 derniers
            if len(self.event_history) > 3:
                self.event_history.pop(0)
            
            # Si DOWN détecté et activé → commencer à cliquer
            if pressed and self.enabled:
                self.clicking = True
                print("🖱️  Autoclick ON")
            
            # Si 2 UP consécutifs → arrêter (TON IDÉE !)
            if len(self.event_history) >= 2:
                if self.event_history[-1] == "UP" and self.event_history[-2] == "UP":
                    self.clicking = False
                    print("⏹️  Autoclick OFF (2 UP détectés)")
    
    def click(self):
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    
    def main_loop(self):
        while True:
            if self.enabled and self.clicking:
                self.click()
                time.sleep(1.0 / self.cps)
            else:
                time.sleep(0.01)
    
    def run(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        self.enabled = False
        self.clicking = False
        keyboard.unhook_all()
        self.mouse_listener.stop()
        self.root.destroy()

# ---------------- main ----------------
if __name__ == "__main__":
    app = AutoClicker()
    app.run()
