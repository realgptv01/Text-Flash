import tkinter as tk
from tkinter import colorchooser, messagebox, ttk, filedialog
import cv2
import numpy as np
from PIL import Image, ImageTk
import time
import os

class TextFlashApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-Flash")
        
        # --- State Variables ---
        self.color1 = (255, 0, 0) # BGR Red
        self.color2 = (0, 0, 255) # BGR Blue
        self.res_options = {"720p": (1280, 720), "480p": (854, 480), "360p": (640, 360)}
        
        # --- UI Layout ---
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)

        control_panel = tk.Frame(main_frame, padx=15, pady=15, width=250)
        control_panel.pack(side=tk.LEFT, fill=tk.Y)

        # Text Input
        tk.Label(control_panel, text="Text Content:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.entry = tk.Entry(control_panel, width=25)
        self.entry.insert(0, "TEXT-FLASH")
        self.entry.pack(pady=(0, 15))

        # Font Selector
        tk.Label(control_panel, text="Font Style:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.font_var = tk.StringVar(value="SIMPLEX")
        self.font_dropdown = ttk.Combobox(control_panel, textvariable=self.font_var, state="readonly")
        self.font_dropdown['values'] = ("SIMPLEX", "COMPLEX", "ITALIC", "SCRIPT")
        self.font_dropdown.pack(pady=(0, 15))

        # Resolution Selector
        tk.Label(control_panel, text="Video Resolution:", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.res_var = tk.StringVar(value="360p")
        self.res_dropdown = ttk.Combobox(control_panel, textvariable=self.res_var, values=list(self.res_options.keys()), state="readonly")
        self.res_dropdown.pack(pady=(0, 15))

        # Fade/Speed Slider
        tk.Label(control_panel, text="Flash Speed (Seconds):", font=('Arial', 9, 'bold')).pack(anchor=tk.W)
        self.speed_slider = tk.Scale(control_panel, from_=0.1, to=5.0, resolution=0.1, orient=tk.HORIZONTAL)
        self.speed_slider.set(1.0)
        self.speed_slider.pack(pady=(0, 15), fill=tk.X)

        # Color Buttons
        tk.Button(control_panel, text="Set Color 1", command=self.choose_c1).pack(fill=tk.X, pady=2)
        tk.Button(control_panel, text="Set Color 2", command=self.choose_c2).pack(fill=tk.X, pady=2)
        
        # Export Button
        tk.Button(control_panel, text="EXPORT MP4", command=self.export_video, bg="#2ecc71", fg="white", font=('Arial', 10, 'bold'), height=2).pack(fill=tk.X, pady=20)

        # Right Preview Area
        preview_frame = tk.Frame(main_frame, bg="#222")
        preview_frame.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH)
        
        tk.Label(preview_frame, text="Live Preview (Green Screen)", bg="#222", fg="white").pack(pady=5)
        self.canvas = tk.Canvas(preview_frame, width=640, height=360, bg="black", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.update_preview()

    def get_cv_font(self):
        fonts = {
            "SIMPLEX": cv2.FONT_HERSHEY_SIMPLEX,
            "COMPLEX": cv2.FONT_HERSHEY_COMPLEX,
            "ITALIC": cv2.FONT_HERSHEY_SIMPLEX | cv2.FONT_ITALIC,
            "SCRIPT": cv2.FONT_HERSHEY_SCRIPT_SIMPLEX
        }
        return fonts.get(self.font_var.get(), cv2.FONT_HERSHEY_SIMPLEX)

    def choose_c1(self):
        c = colorchooser.askcolor(title="Choose Color 1")[0]
        if c: self.color1 = (int(c[2]), int(c[1]), int(c[0]))

    def choose_c2(self):
        c = colorchooser.askcolor(title="Choose Color 2")[0]
        if c: self.color2 = (int(c[2]), int(c[1]), int(c[0]))

    def lerp_color(self, t):
        c1 = np.array(self.color1)
        c2 = np.array(self.color2)
        mix = (np.sin(t * (2 * np.pi) / self.speed_slider.get()) + 1) / 2
        return tuple((c1 * (1 - mix) + c2 * mix).astype(int).tolist())

    def create_frame(self, color, text, res):
        w, h = res
        frame = np.full((h, w, 3), (0, 255, 0), dtype=np.uint8) 
        f_scale = h / 250 
        thickness = max(1, int(f_scale * 2))
        font_face = self.get_cv_font()
        text_size = cv2.getTextSize(text, font_face, f_scale, thickness)[0]
        tx = (w - text_size[0]) // 2
        ty = (h + text_size[1]) // 2
        cv2.putText(frame, text, (tx, ty), font_face, f_scale, color, thickness, cv2.LINE_AA)
        return frame

    def update_preview(self):
        res = self.res_options[self.res_var.get()]
        color = self.lerp_color(time.time())
        frame = self.create_frame(color, self.entry.get(), res)
        display_frame = cv2.resize(frame, (640, 360))
        img = Image.fromarray(cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB))
        self.imgtk = ImageTk.PhotoImage(image=img)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.imgtk)
        self.root.after(30, self.update_preview)

    def export_video(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("MP4 Video", "*.mp4")])
        if not file_path: return

        res = self.res_options[self.res_var.get()]
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(file_path, fourcc, 30.0, res)
        
        for i in range(300): # 10 seconds
            t = i / 30.0 
            color = self.lerp_color(t)
            frame = self.create_frame(color, self.entry.get(), res)
            out.write(frame)
        
        out.release()
        messagebox.showinfo("Success", "Video Exported!")

if __name__ == "__main__":
    root = tk.Tk()
    root.minsize(900, 450)
    app = TextFlashApp(root)
    root.mainloop()
