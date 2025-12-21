import time
import tkinter as tk
from tkinter import ttk
import threading
import keyboard
import win32api
import win32con
from pynput import mouse
import random

# ---------------- AutoClicker ULTRA HUMAIN ----------------
class AutoClicker:
    def __init__(self):
        self.enabled = False
        self.cps = 17
        self.clicking = False
        self.event_history = []
        
        # Paramètres d'humanisation
        self.delay_variation = 15  # % de variation du délai
        self.micro_pause_chance = 2  # % de chance de micro-pause
        self.cps_drift = 10        # % de dérive du CPS
        self.click_duration_var = 50  # % variation durée clic
        
        # Stats
        self.total_clicks = 0
        self.clicks_since_drift = 0
        self.current_cps_modifier = 1.0
        
        # GUI
        self.root = tk.Tk()
        self.root.title("Autoclicker PvP - ULTRA HUMAIN")
        self.root.geometry("450x480")
        self.root.resizable(False, False)
        self.setup_ui()
        
        # Hotkey R
        keyboard.add_hotkey('r', self.toggle)
        
        # Listener souris
        self.mouse_listener = mouse.Listener(on_click=self.on_mouse_event)
        self.mouse_listener.start()
        
        # Thread click
        threading.Thread(target=self.main_loop, daemon=True).start()
    
    def setup_ui(self):
        # Frame principal avec scroll
        main_frame = ttk.Frame(self.root, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Titre
        ttk.Label(main_frame, text="⚔️ Autoclicker PvP", font=("Arial", 18, "bold")).pack(pady=10)
        
        # Statut
        self.status_label = ttk.Label(main_frame, text="🔴 DÉSACTIVÉ", font=("Arial", 13, "bold"), foreground="red")
        self.status_label.pack(pady=5)
        
        # === CPS ===
        cps_frame = ttk.LabelFrame(main_frame, text="⚡ CPS (Clics par seconde)", padding=10)
        cps_frame.pack(fill=tk.X, pady=10)
        
        self.cps_label = ttk.Label(cps_frame, text=f"{self.cps} CPS", font=("Arial", 11, "bold"))
        self.cps_label.pack()
        
        self.cps_slider = ttk.Scale(cps_frame, from_=1, to=100, orient=tk.HORIZONTAL,
                                    command=self.update_cps, length=350)
        self.cps_slider.set(self.cps)
        self.cps_slider.pack(pady=5)
        
        # Presets CPS
        preset_frame = ttk.Frame(cps_frame)
        preset_frame.pack(pady=5)
        for text, value in [("10", 10), ("20", 20), ("50", 50), ("100", 100)]:
            ttk.Button(preset_frame, text=text, command=lambda v=value: self.set_cps(v), width=8).pack(side=tk.LEFT, padx=2)
        
        # === HUMANISATION ===
        human_frame = ttk.LabelFrame(main_frame, text="🤖➡️👤 Humanisation", padding=10)
        human_frame.pack(fill=tk.X, pady=10)
        
        # Variation de délai
        ttk.Label(human_frame, text="Variation du délai entre clics").pack(anchor=tk.W)
        self.delay_var_label = ttk.Label(human_frame, text=f"{self.delay_variation}%")
        self.delay_var_label.pack()
        delay_slider = ttk.Scale(human_frame, from_=0, to=50, orient=tk.HORIZONTAL,
                                command=self.update_delay_var, length=350)
        delay_slider.set(self.delay_variation)
        delay_slider.pack(pady=(0, 10))
        
        # Dérive du CPS
        ttk.Label(human_frame, text="Dérive naturelle du CPS (fatigue)").pack(anchor=tk.W)
        self.cps_drift_label = ttk.Label(human_frame, text=f"{self.cps_drift}%")
        self.cps_drift_label.pack()
        drift_slider = ttk.Scale(human_frame, from_=0, to=30, orient=tk.HORIZONTAL,
                                command=self.update_cps_drift, length=350)
        drift_slider.set(self.cps_drift)
        drift_slider.pack(pady=(0, 10))
        
        # Micro-pauses
        ttk.Label(human_frame, text="Chance de micro-pause (0.1-0.3s)").pack(anchor=tk.W)
        self.pause_label = ttk.Label(human_frame, text=f"{self.micro_pause_chance}%")
        self.pause_label.pack()
        pause_slider = ttk.Scale(human_frame, from_=0, to=10, orient=tk.HORIZONTAL,
                                command=self.update_pause, length=350)
        pause_slider.set(self.micro_pause_chance)
        pause_slider.pack(pady=(0, 10))
        

        
        # Stats
        self.stats_label = ttk.Label(main_frame, text="Clics totaux: 0", font=("Arial", 9), foreground="gray")
        self.stats_label.pack(pady=5)
        
        # Instructions
        ttk.Label(main_frame, text="R = Activer/Désactiver | Maintenez clic gauche", 
                 font=("Arial", 9)).pack(pady=5)
    
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
        
        # Variation de la durée du clic (temps entre DOWN et UP)
        down_up_delay = 0.001
        if self.click_duration_var > 0:
            variation = down_up_delay * (self.click_duration_var / 100.0)
            down_up_delay = max(0.001, down_up_delay + random.uniform(-variation, variation))
        
        # Clic avec durée variable
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(down_up_delay)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
    
    def get_humanized_delay(self):
        # Appliquer la dérive du CPS (fatigue)
        self.clicks_since_drift += 1
        if self.clicks_since_drift >= random.randint(15, 30):
            # Changer légèrement le CPS modifier
            drift_amount = self.cps_drift / 100.0
            self.current_cps_modifier = random.uniform(1.0 - drift_amount, 1.0 + drift_amount)
            self.clicks_since_drift = 0
        
        # CPS effectif avec dérive
        effective_cps = self.cps * self.current_cps_modifier
        base_delay = 1.0 / effective_cps
        
        # Variation aléatoire du délai
        if self.delay_variation > 0:
            variation_amount = base_delay * (self.delay_variation / 100.0)
            random_offset = random.gauss(0, variation_amount / 2)  # Distribution normale
            final_delay = max(0.001, base_delay + random_offset)
        else:
            final_delay = base_delay
        
        return final_delay
    
    def main_loop(self):
        while True:
            if self.enabled and self.clicking:
                # Micro-pause aléatoire
                if self.micro_pause_chance > 0 and random.randint(1, 100) <= self.micro_pause_chance:
                    pause_duration = random.uniform(0.1, 0.3)
                    time.sleep(pause_duration)
                
                # Faire le clic humanisé
                self.humanized_click()
                self.total_clicks += 1
                
                # Mettre à jour les stats (pas trop souvent)
                if self.total_clicks % 10 == 0:
                    self.stats_label.config(text=f"Clics totaux: {self.total_clicks}")
                
                # Délai humanisé
                time.sleep(self.get_humanized_delay())
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
    print("🚀 Autoclicker PvP ULTRA HUMAIN")
    print("📌 Toutes les techniques d'humanisation activées")
    app = AutoClicker()
    app.run()
