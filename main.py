# pyrefly: ignore [missing-import]
import minecraft_launcher_lib
import subprocess
import customtkinter as ctk
import tkinter
import threading
import queue
import os
import requests
import zipfile
import shutil
import uuid
import sys

# ── Path logic (works both as .py and compiled .exe) ──────────────────────────
if getattr(sys, "frozen", False):
    BASE_PATH  = os.path.dirname(sys.executable)
    BUNDLE_DIR = sys._MEIPASS
else:
    BASE_PATH  = os.path.dirname(os.path.abspath(__file__))
    BUNDLE_DIR = BASE_PATH

def resource_path(rel):
    return os.path.join(BUNDLE_DIR, rel)

# ── Paths ─────────────────────────────────────────────────────────────────────
MC_DIR    = os.path.join(BASE_PATH, "GengarFiles")
MODS_DIR  = os.path.join(BASE_PATH, "GengarMods")
JAVA_DIR  = os.path.join(BASE_PATH, "GengarJDK")
JAVA_BIN  = os.path.join(JAVA_DIR, "bin", "java.exe")
ICON_NAME = resource_path("Gengar.ico")

# Ensure GengarMods exists with subfolders for organization
os.makedirs(MODS_DIR, exist_ok=True)
for loader_name in ["Fabric", "Forge", "NeoForge"]:
    os.makedirs(os.path.join(MODS_DIR, loader_name), exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BG          = "#1a1020"        # deep dark background
CARD        = "#251630"        # card surface
BORDER      = "#3d2550"        # subtle border
PURPLE      = "#7b52ab"        # Gengar purple (primary)
PURPLE_H    = "#5e3e84"        # hover
PURPLE_DIM  = "#4a2f6b"        # pressed / disabled tint
MUTED       = "#a188be"        # secondary text
SUCCESS     = "#4caf82"
WARN        = "#e07b39"
WHITE       = "#f0eaf8"        # near-white text


# ── Helpers ───────────────────────────────────────────────────────────────────
def _divider(parent):
    """Thin horizontal separator."""
    ctk.CTkFrame(parent, height=1, fg_color=BORDER).pack(fill="x", padx=24, pady=6)


class CTkScrollableDropdown(tkinter.Toplevel):
    def __init__(self, attach_to, values=None, command=None, **kwargs):
        super().__init__(takefocus=True)
        self.attach_to = attach_to
        self.values = values or []
        self.command = command

        self.overrideredirect(True)
        self.attributes("-transparentcolor", "#000001")
        self.configure(bg="#000001")

        self.transient(self.attach_to.winfo_toplevel())

        self.update_idletasks()

        x = self.attach_to.winfo_rootx()
        y = self.attach_to.winfo_rooty() + self.attach_to.winfo_height() + 4
        width = self.attach_to.winfo_width()

        # Show 6 items max, scroll for more
        item_height = 26
        visible_items = min(len(self.values), 6)
        calculated_height = (visible_items * item_height) + 8

        # Outer container - dark with rounded corners and subtle border
        self.container = ctk.CTkFrame(
            self,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
            fg_color=CARD
        )
        self.container.pack(fill="both", expand=False)

        # Scrollable frame - thin dark scrollbar
        self.scroll_frame = ctk.CTkScrollableFrame(
            self.container,
            corner_radius=8,
            fg_color=CARD,
            scrollbar_fg_color=BG,
            scrollbar_button_color=PURPLE,
            scrollbar_button_hover_color=PURPLE_H,
            orientation="vertical"
        )
        self.scroll_frame._parent_canvas.configure(height=calculated_height - 8)
        self.scroll_frame.pack(fill="both", padx=2, pady=2)
        self.scroll_frame.pack_propagate(False)

        super().geometry(f"{width}x{calculated_height}+{x}+{y}")

        # Populate with version buttons - tech aesthetic
        self.buttons = []
        for value in self.values:
            btn = ctk.CTkButton(
                self.scroll_frame,
                text=value,
                anchor="w",
                height=24,
                corner_radius=6,
                fg_color=BG,
                text_color=WHITE,
                hover_color=PURPLE,
                border_width=0,
                font=("Segoe UI", 11),
                command=lambda val=value: self._on_select(val)
            )
            btn.pack(fill="x", pady=1, padx=2)
            self.buttons.append(btn)

        # Global bindings to auto-close
        self.root = self.attach_to.winfo_toplevel()

        self._root_click_bind = self.root.bind("<Button-1>", self._check_click_outside, add="+")
        self._root_configure_bind = self.root.bind("<Configure>", lambda e: self.destroy(), add="+")
        self.bind("<FocusOut>", lambda e: self.destroy())
        self.bind("<Escape>", lambda e: self.destroy())

    def _on_select(self, value):
        self.attach_to._just_closed = True
        self.attach_to.after(200, lambda: setattr(self.attach_to, "_just_closed", False))
        if self.command:
            self.command(value)
        self.destroy()

    def _check_click_outside(self, event):
        if not self.winfo_exists():
            return

        x, y = event.x_root, event.y_root

        dx = self.winfo_rootx()
        dy = self.winfo_rooty()
        dw = self.winfo_width()
        dh = self.winfo_height()

        ax = self.attach_to.winfo_rootx()
        ay = self.attach_to.winfo_rooty()
        aw = self.attach_to.winfo_width()
        ah = self.attach_to.winfo_height()

        click_on_combo = (ax <= x <= ax + aw and ay <= y <= ay + ah)
        click_on_dropdown = (dx <= x <= dx + dw and dy <= y <= dy + dh)

        if not click_on_dropdown:
            if click_on_combo:
                self.attach_to._just_closed = True
                self.attach_to.after(200, lambda: setattr(self.attach_to, "_just_closed", False))
            self.destroy()

    def destroy(self):
        try:
            self.root.unbind("<Button-1>", self._root_click_bind)
        except Exception:
            pass
        try:
            self.root.unbind("<Configure>", self._root_configure_bind)
        except Exception:
            pass
        super().destroy()


class GengarLauncher(ctk.CTk):
    def __init__(self):
        self.queue = queue.Queue()
        super().__init__()
        self._process_queue()
        self.title("GengarLauncher")
        self.geometry("420x540")
        self.resizable(False, False)
        self.configure(fg_color=BG)

        if os.path.exists(ICON_NAME):
            try: self.iconbitmap(ICON_NAME)
            except Exception: pass

        self._releases: list[str] = []
        self._max_progress = 1
        self.loader_var = ctk.StringVar(value="Vanilla")

        self._build_ui()
        self.after(100, lambda: threading.Thread(target=self._fetch_versions, daemon=True).start())

    def _process_queue(self):
        try:
            while True:
                callback = self.queue.get_nowait()
                try:
                    callback()
                except Exception as e:
                    print(f"Error executing queued callback: {e}")
        except queue.Empty:
            pass
        super().after(100, self._process_queue)

    def after(self, delay, callback, *args):
        if threading.current_thread() is threading.main_thread():
            return super().after(delay, callback, *args)
        else:
            if delay == 0:
                self.queue.put(lambda: callback(*args))
            else:
                self.queue.put(lambda: super().after(delay, callback, *args))

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        # ── Header card ───────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=CARD, corner_radius=0)
        header.pack(fill="x")

        ctk.CTkLabel(
            header, text="GengarLauncher",
            font=("Segoe UI", 22, "bold"), text_color=PURPLE
        ).pack(pady=(18, 2))

        ctk.CTkLabel(
            header, text="Minecraft  ·  Cracked Edition",
            font=("Segoe UI", 10), text_color=MUTED
        ).pack(pady=(0, 14))

        # ── Main card ─────────────────────────────────────────────────────────
        card = ctk.CTkFrame(self, fg_color=CARD, corner_radius=14)
        card.pack(fill="both", expand=True, padx=20, pady=(14, 0))

        # Username
        self._field_label(card, "USERNAME")
        self.username_input = ctk.CTkEntry(
            card,
            placeholder_text="Your nickname…",
            height=34, corner_radius=8,
            fg_color=BG, border_color=BORDER, border_width=1,
            text_color=WHITE, placeholder_text_color=MUTED,
            font=("Segoe UI", 12)
        )
        self.username_input.pack(fill="x", padx=16, pady=(3, 10))

        _divider(card)

        # Version
        self._field_label(card, "VERSION")

        self.version_var = ctk.StringVar(value="Loading…")
        self.version_combo = ctk.CTkComboBox(
            card,
            variable=self.version_var,
            values=["Loading…"],
            command=lambda v: self._check_installed(v),
            width=180, height=30, corner_radius=8,
            fg_color=BG, border_color=BORDER, border_width=1,
            button_color=PURPLE, button_hover_color=PURPLE_H,
            dropdown_fg_color="#1e1228",
            dropdown_hover_color=PURPLE_DIM,
            dropdown_text_color=WHITE,
            text_color=WHITE, font=("Segoe UI", 12),
            dropdown_font=("Segoe UI", 11),
            state="readonly"
        )
        self.version_combo.pack(anchor="w", padx=16, pady=(3, 4))
        self.version_combo._entry.configure(exportselection=False)

        def custom_open(event=None):
            try:
                if getattr(self.version_combo, "_just_closed", False):
                    return

                if hasattr(self.version_combo, "_active_dropdown") and self.version_combo._active_dropdown and self.version_combo._active_dropdown.winfo_exists():
                    self.version_combo._active_dropdown.destroy()
                    self.version_combo._active_dropdown = None
                    return

                values = self.version_combo.cget("values")
                if not values or values == ["Loading…"]:
                    return

                self.version_combo._active_dropdown = CTkScrollableDropdown(
                    attach_to=self.version_combo,
                    values=values,
                    command=self.version_combo._dropdown_callback
                )
            except Exception as e:
                import traceback
                with open("dropdown_error.log", "w") as f:
                    traceback.print_exc(file=f)
                print(f"Error in custom_open: {e}")

        self.version_combo._clicked = custom_open

        # Installed badge
        self.installed_label = ctk.CTkLabel(
            card, text="", font=("Segoe UI", 10), text_color=MUTED, anchor="w"
        )
        self.installed_label.pack(fill="x", padx=18, pady=(0, 2))

        # Loader Selection
        self._field_label(card, "MOD LOADER")
        self.loader_menu = ctk.CTkOptionMenu(
            card,
            variable=self.loader_var,
            values=["Vanilla", "Fabric", "Forge", "NeoForge"],
            command=lambda _: self._update_version_list(),
            width=140, height=28, corner_radius=8,
            fg_color=BG, button_color=PURPLE, button_hover_color=PURPLE_H,
            dropdown_fg_color="#1e1228",
            dropdown_hover_color=PURPLE_DIM,
            text_color=WHITE, font=("Segoe UI", 11),
            dropdown_font=("Segoe UI", 11)
        )
        self.loader_menu.pack(anchor="w", padx=16, pady=(3, 10))

        _divider(card)

        # Progress + status
        self.progress_bar = ctk.CTkProgressBar(
            card, height=5, corner_radius=4,
            fg_color=BORDER, progress_color=PURPLE
        )
        self.progress_bar.set(0)
        self.progress_bar.pack(fill="x", padx=16, pady=(6, 2))

        self.status_label = ctk.CTkLabel(
            card, text="Fetching versions…",
            font=("Segoe UI", 10), text_color=MUTED, anchor="w"
        )
        self.status_label.pack(fill="x", padx=18, pady=(2, 12))

        # Play button
        self.play_button = ctk.CTkButton(
            card, text="▶   PLAY",
            command=self._start_launch_thread,
            fg_color=PURPLE, hover_color=PURPLE_H,
            font=("Segoe UI", 13, "bold"),
            height=40, corner_radius=10
        )
        self.play_button.pack(fill="x", padx=16, pady=(0, 16))

        # ── Footer ───────────────────────────────────────────────────────────
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(8, 10))
        ctk.CTkLabel(
            footer, text="BillyHz", font=("Segoe UI", 10, "italic"),
            text_color=PURPLE
        ).pack(side="left")
        ctk.CTkLabel(
            footer, text="Alpha 0.6.0", font=("Segoe UI", 10),
            text_color=MUTED
        ).pack(side="right")

    def _field_label(self, parent, text: str):
        ctk.CTkLabel(
            parent, text=text,
            font=("Segoe UI", 9, "bold"), text_color=MUTED, anchor="w"
        ).pack(fill="x", padx=18, pady=(10, 0))

    # ── Version list ──────────────────────────────────────────────────────────

    def _fetch_versions(self):
        try:
            all_v = minecraft_launcher_lib.utils.get_version_list()
            self._releases = [v["id"] for v in all_v if v["type"] == "release"]
            if not self._releases:
                self._releases = ["No versions found"]
            self.after(0, self._update_version_list)
            self.after(0, lambda: self.status_label.configure(text="Ready"))
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(
                text=f"Error fetching versions: {e}"
            ))

    def _update_version_list(self):
        """Filters the version dropdown based on the selected mod loader."""
        loader_name = self.loader_var.get().lower()
        self.status_label.configure(text=f"Updating {loader_name} versions…")

        def task():
            try:
                if loader_name == "vanilla":
                    versions = self._releases
                else:
                    from minecraft_launcher_lib import mod_loader
                    ml = mod_loader.get_mod_loader(loader_name)
                    versions = ml.get_minecraft_versions(True)

                self.after(0, lambda: self._populate_menu(versions))
                self.after(0, lambda: self.status_label.configure(text="Ready"))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(text=f"Filter Error: {e}"))

        threading.Thread(target=task, daemon=True).start()

    def _populate_menu(self, versions):
        self.version_combo.configure(values=versions)
        if versions:
            self.version_combo.set(versions[0])
            self._check_installed(versions[0])

    def _get_installed(self) -> list[str]:
        vdir = os.path.join(MC_DIR, "versions")
        if not os.path.isdir(vdir):
            return []
        found = []
        for name in os.listdir(vdir):
            if (os.path.exists(os.path.join(vdir, name, f"{name}.jar")) and
                    os.path.exists(os.path.join(vdir, name, f"{name}.json"))):
                found.append(name)
        return found

    def _check_installed(self, version_id: str):
        if version_id in self._get_installed():
            self.installed_label.configure(
                text=f"✔  {version_id} already installed", text_color=SUCCESS
            )
        else:
            self.installed_label.configure(
                text=f"⬇  Will download on first launch", text_color=WARN
            )

    def _sync_mods(self, loader_type: str, mc_version: str):
        source_dir = os.path.join(MODS_DIR, loader_type.capitalize(), mc_version)
        os.makedirs(source_dir, exist_ok=True)

        mc_mods_dir = os.path.join(MC_DIR, "mods")
        os.makedirs(mc_mods_dir, exist_ok=True)

        for item in os.listdir(mc_mods_dir):
            path = os.path.join(mc_mods_dir, item)
            if os.path.isfile(path) and path.endswith(".jar"):
                try: os.remove(path)
                except Exception: pass

        for item in os.listdir(source_dir):
            src = os.path.join(source_dir, item)
            dst = os.path.join(mc_mods_dir, item)
            if os.path.isfile(src) and src.endswith(".jar"):
                try: shutil.copy2(src, dst)
                except Exception: pass

    # ── JDK ───────────────────────────────────────────────────────────────────

    def _download_jdk(self):
        if os.path.exists(JAVA_BIN):
            return
        self.after(0, lambda: self.status_label.configure(text="Downloading Java 21…"))
        url = (
            "https://github.com/adoptium/temurin21-binaries/releases/download/"
            "jdk-21.0.2%2B13/OpenJDK21U-jdk_x64_windows_hotspot_21.0.2_13.zip"
        )
        zip_tmp = os.path.join(BASE_PATH, "jdk.zip")
        r = requests.get(url, stream=True)
        total = int(r.headers.get("content-length", 0))
        done = 0
        with open(zip_tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                f.write(chunk)
                done += len(chunk)
                if total:
                    self.after(0, lambda p=done / total: self.progress_bar.set(p))

        self.after(0, lambda: self.status_label.configure(text="Extracting Java…"))
        with zipfile.ZipFile(zip_tmp, "r") as z:
            z.extractall(BASE_PATH)

        extracted = [
            d for d in os.listdir(BASE_PATH)
            if "jdk-21" in d and os.path.isdir(os.path.join(BASE_PATH, d))
        ][0]
        if os.path.exists(JAVA_DIR):
            shutil.rmtree(JAVA_DIR)
        shutil.move(os.path.join(BASE_PATH, extracted), JAVA_DIR)
        os.remove(zip_tmp)
        self.after(0, lambda: self.progress_bar.set(0))

    # ── Launch ───────────────────────────────────────────────────────────────

    def _start_launch_thread(self):
        user = self.username_input.get().strip()
        if not user:
            self.status_label.configure(text="⚠  Enter a username first!")
            return
        version = self.version_var.get()
        if version in ("Loading…", "No versions found"):
            self.status_label.configure(text="⚠  Select a valid version.")
            return
        self.play_button.configure(state="disabled")
        threading.Thread(target=self._launch_game, args=(user, version), daemon=True).start()

    def _launch_game(self, username: str, version: str):
        try:
            self._download_jdk()
            os.makedirs(MC_DIR, exist_ok=True)

            def set_status(t):
                self.after(0, lambda _t=t: self.status_label.configure(text=_t))

            def set_progress(v):
                self.after(0, lambda _v=v: self.progress_bar.set(
                    _v / max(self._max_progress, 1)
                ))

            def set_max(v):
                self._max_progress = v or 1

            self._max_progress = 1
            set_status(f"Installing {version}…")
            minecraft_launcher_lib.install.install_minecraft_version(
                version, MC_DIR,
                callback={"setStatus": set_status, "setProgress": set_progress, "setMax": set_max}
            )

            launch_version = version

            selected_loader = self.loader_var.get().lower()
            if selected_loader != "vanilla":
                from minecraft_launcher_lib import mod_loader
                try:
                    ml = mod_loader.get_mod_loader(selected_loader)
                    if ml.is_minecraft_version_supported(version):
                        set_status(f"Installing {selected_loader.capitalize()}…")
                        loader_ver = ml.get_latest_loader_version(version)
                        ml.install(version, MC_DIR, loader_version=loader_ver, callback={"setStatus": set_status, "setProgress": set_progress, "setMax": set_max})
                        launch_version = ml.get_id(version, loader_version=loader_ver)

                        set_status(f"Syncing mods for {version}…")
                        self._sync_mods(selected_loader, version)
                    else:
                        self.after(0, lambda: self.status_label.configure(
                            text=f"⚠ {selected_loader.capitalize()} not supported for {version}. Vanilla launch."
                        ))
                        import time
                        time.sleep(1.5)
                except Exception as e:
                    self.after(0, lambda: self.status_label.configure(text=f"Mod Loader Error: {e}"))
                    import time
                    time.sleep(2)

            self.after(0, lambda: self.progress_bar.set(1))
            set_status(f"Launching {launch_version}…")

            cmd = minecraft_launcher_lib.command.get_minecraft_command(
                launch_version, MC_DIR,
                {
                    "username": username,
                    "uuid": str(uuid.uuid4()),
                    "token": "0",
                    "executablePath": JAVA_BIN,
                    "jvmArguments": ["-Xmx4G", "-Xms2G"],
                }
            )

            self.after(0, self.withdraw)
            if os.name == "nt":
                subprocess.run(cmd, creationflags=0x08000000)
            else:
                subprocess.run(cmd)
            self.after(0, self.deiconify)

        except Exception as err:
            self.after(0, self.deiconify)
            self.after(0, lambda e=str(err): self.status_label.configure(text=f"Error: {e}"))
        finally:
            self.after(0, lambda: self.progress_bar.set(0))
            self.after(0, lambda: self.status_label.configure(text="Ready"))
            self.after(0, lambda: self.play_button.configure(state="normal"))
            self.after(0, lambda v=version: self._check_installed(v))


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    app = GengarLauncher()
    app.mainloop()