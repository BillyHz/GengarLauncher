import customtkinter as ctk

root = ctk.CTk()
root.geometry('400x300')

values = [f'1.{x}.{y}' for x in range(20) for y in range(5)]

class TestDropdown(ctk.CTkToplevel):
    def __init__(self, values, command):
        super().__init__(takefocus=True)
        self.overrideredirect(True)
        self.attributes("-transparentcolor", "#000001")
        self.configure(bg="#000001")

        item_height = 28
        visible_items = 4
        calculated_height = (visible_items * item_height) + 10
        width = 180

        self.geometry(f'{width}x{calculated_height}+100+100')

        self.container = ctk.CTkFrame(self, corner_radius=10, fg_color='#251630', border_color='#3d2550', border_width=1)
        self.container.pack(fill='both', expand=False)

        self.scroll_frame = ctk.CTkScrollableFrame(
            self.container,
            corner_radius=8,
            fg_color='#251630',
            scrollbar_fg_color='#3d2550',
            scrollbar_button_color='#7b52ab',
            orientation='vertical'
        )
        self.scroll_frame.configure(height=calculated_height - 12)
        self.scroll_frame.pack(fill='both', padx=2, pady=2)
        self.scroll_frame.pack_propagate(False)

        for value in values:
            btn = ctk.CTkButton(
                self.scroll_frame,
                text=value,
                anchor='w',
                height=24,
                corner_radius=6,
                fg_color='#1a1020',
                text_color='#f0eaf8',
                hover_color='#4a2f6b',
                font=('Segoe UI', 11),
                command=lambda v=value: command(v)
            )
            btn.pack(fill='x', pady=1, padx=2)

        self.update_idletasks()
        print(f'Window geometry: {self.winfo_geometry()}')
        print(f'Container geometry: {self.container.winfo_geometry()}')
        print(f'ScrollFrame geometry: {self.scroll_frame.winfo_geometry()}')
        print(f'ScrollFrame desired size: {self.scroll_frame._desired_width}x{self.scroll_frame._desired_height}')
        print(f'Canvas geometry: {self.scroll_frame._parent_canvas.winfo_geometry()}')

d = TestDropdown(values, lambda v: print(v))
root.mainloop()