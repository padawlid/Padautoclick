import time
import tkinter as tk
from tkinter import ttk
import threading
import win32api
import win32con
from pynput import mouse
import random
import ctypes
import sys

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

# ============ AUTOCLICKER ============
class AutoClicker:
    def __init__(self):
        self.enabled = False
        self.cps = 17
        self.clicking = False
        self.event_history = []
        self.toggle_key_pressed = False
        
        # Paramètres d'humanisation
        self.delay_variation = 15
        self.micro_pause_chance = 2
        self.cps_drift = 10
        self.click_duration_var = 50
        
        # Stats
        self.total_clicks = 0
        self.clicks_since_drift = 0
        self.current_cps_modifier = 1.0
        
        # GUI
        self.root = tk.Tk()
        self.root.title("Autoclicker PvP")
        self.root.geometry("450x480")
        self.root.resizable(False, False)
        self.setup_ui()
        
        # Listener souris
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_event)
        self.mouse_listener.start()
        
        # Thread click
        threading.Thread(target=self.main_loop, daemon=True).start()
        
        # Thread pour détecter la touche R (polling direct)
        threading.Thread(target=self.keyboard_poll, daemon=True).start()
    
    def keyboard_poll(self):
        """Poll direct de la touche R avec GetAsyncKeyState"""
        VK_R = 0x52
        last_state = False
        
        while True:
            try:
                # Vérifier l'état de la touche R
                state = (ctypes.windll.user32.GetAsyncKeyState(VK_R) & 0x8000) != 0
                
                # Détecter l'appui (transition False -> True)
                if state and not last_state:
                    print("🔑 Touche R détectée")
                    self.toggle()
                
                last_state = state
                time.sleep(0.05)  # Vérifier toutes les 50ms
            except Exception as e:
                print(f"Erreur keyboard_poll: {e}")
                time.sleep(0.1)
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(pady=10)
        ttk.Label(title_frame, text="⚔️ Autoclicker PvP", font=("Arial", 18, "bold")).pack()
        ttk.Label(title_frame, text="⚡ Polling Direct", font=("Arial", 9), foreground="blue").pack()
        
        # Statut
        self.status_label = ttk.Label(main_frame, text="🔴 DÉSACTIVÉ", font=("Arial", 13, "bold"), foreground="red")
        self.status_label.pack(pady=5)
        
        # === CPS ===
        cps_frame = ttk.LabelFrame(main_frame, text="⚡ CPS", padding=10)
        cps_frame.pack(fill=tk.X, pady=10)
        
        self.cps_label = ttk.Label(cps_frame, text=f"{self.cps} CPS", font=("Arial", 11, "bold"))
        self.cps_label.pack()
        
        self.cps_slider = ttk.Scale(cps_frame, from_=1, to=100, orient=tk.HORIZONTAL,
                                    command=self.update_cps, length=350)
        self.cps_slider.set(self.cps)
        self.cps_slider.pack(pady=5)
        
        # Presets
        preset_frame = ttk.Frame(cps_frame)
        preset_frame.pack(pady=5)
        for text, value in [("10", 10), ("17", 17), ("20", 20), ("50", 50)]:
            ttk.Button(preset_frame, text=text, command=lambda v=value: self.set_cps(v), width=8).pack(side=tk.LEFT, padx=2)
        
        # === HUMANISATION ===
        human_frame = ttk.LabelFrame(main_frame, text="🤖➡️👤 Humanisation", padding=10)
        human_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(human_frame, text="Variation du délai").pack(anchor=tk.W)
        self.delay_var_label = ttk.Label(human_frame, text=f"{self.delay_variation}%")
        self.delay_var_label.pack()
        delay_slider = ttk.Scale(human_frame, from_=0, to=50, orient=tk.HORIZONTAL,
                                command=self.update_delay_var, length=350)
        delay_slider.set(self.delay_variation)
        delay_slider.pack(pady=(0, 10))
        
        ttk.Label(human_frame, text="Dérive CPS (fatigue)").pack(anchor=tk.W)
        self.cps_drift_label = ttk.Label(human_frame, text=f"{self.cps_drift}%")
        self.cps_drift_label.pack()
        drift_slider = ttk.Scale(human_frame, from_=0, to=30, orient=tk.HORIZONTAL,
                                command=self.update_cps_drift, length=350)
        drift_slider.set(self.cps_drift)
        drift_slider.pack(pady=(0, 10))
        
        ttk.Label(human_frame, text="Micro-pauses").pack(anchor=tk.W)
        self.pause_label = ttk.Label(human_frame, text=f"{self.micro_pause_chance}%")
        self.pause_label.pack()
        pause_slider = ttk.Scale(human_frame, from_=0, to=10, orient=tk.HORIZONTAL,
                                command=self.update_pause, length=350)
        pause_slider.set(self.micro_pause_chance)
        pause_slider.pack(pady=(0, 10))
        
        # Stats
        self.stats_label = ttk.Label(main_frame, text="Clics: 0", font=("Arial", 9), foreground="gray")
        self.stats_label.pack(pady=5)
        
        ttk.Label(main_frame, text="R = Toggle | Maintenir clic gauche", 
                 font=("Arial", 9, "bold")).pack(pady=5)
    
    def set_cps(self, value):
        self.cps = value
        self.cps_slider.set(value)
        self.cps_label.config(text=f"{self.cps} CPS")
    
    def update_cps(self, value):
        self.cps = int(float(value))
        self.cps_label.config(text=f"{self.cps} CPS")
    
    def update_delay_var(self, value):
        self.delay_variation = int(float(value))
        self.delay_var_label.config(text=f"{self.delay_variation}%")
    
    def update_cps_drift(self, value):
        self.cps_drift = int(float(value))
        self.cps_drift_label.config(text=f"{self.cps_drift}%")
    
    def update_pause(self, value):
        self.micro_pause_chance = int(float(value))
        self.pause_label.config(text=f"{self.micro_pause_chance}%")
    
    def toggle(self):
        """Toggle activé/désactivé"""
        self.enabled = not self.enabled
        if self.enabled:
            self.status_label.config(text="🟢 ACTIVÉ", foreground="green")
            print("✅ ACTIVÉ")
        else:
            self.status_label.config(text="🔴 DÉSACTIVÉ", foreground="red")
            self.clicking = False
            print("❌ DÉSACTIVÉ")
    
    def on_mouse_event(self, x, y, button, pressed):
        if button == mouse.Button.left:
            event = "DOWN" if pressed else "UP"
            self.event_history.append(event)
            
            if len(self.event_history) > 3:
                self.event_history.pop(0)
            
            if pressed and self.enabled:
                self.clicking = True
                print("🖱️  Autoclick ON")
            
            if len(self.event_history) >= 2:
                if self.event_history[-1] == "UP" and self.event_history[-2] == "UP":
                    self.clicking = False
                    print("⏹️  Autoclick OFF")
    
    def humanized_click(self):
        down_up_delay = 0.001
        if self.click_duration_var > 0:
            variation = down_up_delay * (self.click_duration_var / 100.0)
            down_up_delay = max(0.001, down_up_delay + random.uniform(-variation, variation))
        
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(down_up_delay)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    
    def get_humanized_delay(self):
        self.clicks_since_drift += 1
        if self.clicks_since_drift >= random.randint(15, 30):
            drift_amount = self.cps_drift / 100.0
            self.current_cps_modifier = random.uniform(1.0 - drift_amount, 1.0 + drift_amount)
            self.clicks_since_drift = 0
        
        effective_cps = self.cps * self.current_cps_modifier
        base_delay = 1.0 / effective_cps
        
        if self.delay_variation > 0:
            variation_amount = base_delay * (self.delay_variation / 100.0)
            random_offset = random.gauss(0, variation_amount / 2)
            final_delay = max(0.001, base_delay + random_offset)
        else:
            final_delay = base_delay
        
        return final_delay
    
    def main_loop(self):
        while True:
            if self.enabled and self.clicking:
                if self.micro_pause_chance > 0 and random.randint(1, 100) <= self.micro_pause_chance:
                    time.sleep(random.uniform(0.1, 0.3))
                
                self.humanized_click()
                self.total_clicks += 1
                
                if self.total_clicks % 10 == 0:
                    self.stats_label.config(text=f"Clics: {self.total_clicks}")
                
                time.sleep(self.get_humanized_delay())
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

# ============ MAIN ============
if __name__ == "__main__":
    print("🚀 Autoclicker PvP - Polling Direct")
    print("⚡ Détection directe de la touche R")
    app = AutoClicker()
    app.run()
