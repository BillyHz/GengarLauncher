import minecraft_launcher_lib
import subprocess
import customtkinter as ctk
import threading
import os
import requests
import zipfile
import shutil
import time
import uuid
import sys

# --- LOGIC FOR PATHS IN THE EXE ---
if getattr(sys, 'frozen', False):
    BASE_PATH = os.path.dirname(sys.executable)
    BUNDLE_DIR = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_PATH

def resource_path(relative_path):
    return os.path.join(BUNDLE_DIR, relative_path)

# --- SETTINGS ---
VERSION = "1.21.11"
MC_DIR = os.path.join(BASE_PATH, "GengarFiles")
JAVA_DIR = os.path.join(BASE_PATH, "GengarJDK")
JAVA_BIN = os.path.join(JAVA_DIR, "bin", "java.exe")
ICON_NAME = resource_path("Gengar.ico") 

# Colores Gengar
BG_COLOR = "#211522" 
GENGAR_PURPLE = "#7b52ab"
GENGAR_HOVER = "#5e3e84"

class GengarLauncher(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("GengarLauncher")
        self.geometry("450x380") 
        self.configure(fg_color=BG_COLOR)
        
        if os.path.exists(ICON_NAME):
            try: self.iconbitmap(ICON_NAME)
            except: pass

        self.main_label = ctk.CTkLabel(self, text="GengarLauncher", font=("Segoe UI", 24, "bold"), text_color=GENGAR_PURPLE)
        self.main_label.pack(pady=(25, 10))

        self.username_input = ctk.CTkEntry(self, placeholder_text=" Enter Nickname...", width=300, fg_color="#311f33", border_color=GENGAR_PURPLE)
        self.username_input.pack(pady=15)

        self.play_button = ctk.CTkButton(self, text="Play Minecraft", command=self.start_launch_thread, fg_color=GENGAR_PURPLE, hover_color=GENGAR_HOVER, font=("Segoe UI", 14, "bold"))
        self.play_button.pack(pady=20)

        self.status_text = ctk.CTkLabel(self, text="Ready", font=("Segoe UI", 12), text_color="#a188be")
        self.status_text.pack(pady=5)

        # Footer
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.pack(side="bottom", fill="x", padx=15, pady=10)
        ctk.CTkLabel(self.footer_frame, text="BillyHz", font=("Segoe UI", 11, "italic"), text_color=GENGAR_PURPLE).pack(side="left")
        ctk.CTkLabel(self.footer_frame, text=f"MC: {VERSION} | Alpha 0.5.0", font=("Segoe UI", 11), text_color="#a188be").pack(side="right")

    def download_jdk(self):
        if os.path.exists(JAVA_BIN): return
        self.status_text.configure(text="Downloading GengarJDK...")
        url = "https://github.com/adoptium/temurin21-binaries/releases/download/jdk-21.0.2%2B13/OpenJDK21U-jdk_x64_windows_hotspot_21.0.2_13.zip"
        zip_temp = os.path.join(BASE_PATH, "jdk.zip")
        r = requests.get(url, stream=True)
        with open(zip_temp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024*1024): f.write(chunk)
        with zipfile.ZipFile(zip_temp, 'r') as zip_ref:
            zip_ref.extractall(BASE_PATH)
        extracted = [d for d in os.listdir(BASE_PATH) if "jdk-21" in d and os.path.isdir(os.path.join(BASE_PATH, d))][0]
        if os.path.exists(JAVA_DIR): shutil.rmtree(JAVA_DIR)
        shutil.move(os.path.join(BASE_PATH, extracted), JAVA_DIR)
        os.remove(zip_temp)

    def start_launch_thread(self):
        user = self.username_input.get()
        if not user: return
        self.play_button.configure(state="disabled")
        threading.Thread(target=self.launch_game, args=(user,), daemon=True).start()

    def launch_game(self, username):
        try:
            self.download_jdk()
            if not os.path.exists(MC_DIR): os.makedirs(MC_DIR)
            self.status_text.configure(text="Gengaring Minecraft...")
            minecraft_launcher_lib.install.install_minecraft_version(VERSION, MC_DIR)

            launch_options = {
                "username": username,
                "uuid": str(uuid.uuid4()),
                "token": "0",
                "executablePath": JAVA_BIN,
                "jvmArguments": ["-Xmx4G", "-Xms2G"], 
            }
            
            launch_command = minecraft_launcher_lib.command.get_minecraft_command(VERSION, MC_DIR, launch_options)
            
            self.after(0, self.withdraw) 
            
            # --- NO BLACK SCREEN ---
            if os.name == 'nt': # ONLY FOR Windows
                subprocess.run(launch_command, creationflags=0x08000000)
            else:
                subprocess.run(launch_command)
                
            self.after(0, self.deiconify) 
            
        except Exception as error:
            self.after(0, self.deiconify)
            self.status_text.configure(text=f"Error: {str(error)}")
        finally:
            self.status_text.configure(text="Ready")
            self.play_button.configure(state="normal")

if __name__ == "__main__":
    app = GengarLauncher()
    app.mainloop()