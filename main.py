import cv2
import os
import time
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image

# Set modern theme
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


class DatasetCreator(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("AI Dataset Creator Pro by RAYTECH")
        self.geometry("1000x700")

        # --- State Variables ---
        self.video_path = ""
        self.save_path = ""
        self.cap = None
        self.is_running = False
        self.count = 0
        self.countSave = 0
        self.moduleVal = 10
        self.imgWidth, self.imgHeight = 640, 480
        self.current_session_dir = ""

        # --- UI Layout ---
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar for Controls
        self.sidebar = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        ctk.CTkLabel(self.sidebar, text="CONTROLS", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=20)

        self.btn_video = ctk.CTkButton(self.sidebar, text="1. Select Video", command=self.select_video)
        self.btn_video.pack(pady=10, padx=20)

        self.btn_folder = ctk.CTkButton(self.sidebar, text="2. Output Folder", command=self.select_output)
        self.btn_folder.pack(pady=10, padx=20)

        # FIXED: use 'from_' and 'to' (no underscore on 'to')
        self.label_thresh = ctk.CTkLabel(self.sidebar, text="Blur Threshold: 20")
        self.label_thresh.pack(pady=(20, 0))
        self.slider_blur = ctk.CTkSlider(self.sidebar, from_=0, to=255, command=self.update_thresh)
        self.slider_blur.set(20)
        self.slider_blur.pack(pady=10, padx=20)

        self.btn_start = ctk.CTkButton(self.sidebar, text="START PROCESSING", fg_color="green",
                                       hover_color="#1e7b1e", command=self.toggle_process)
        self.btn_start.pack(pady=40, padx=20)

        self.stats_label = ctk.CTkLabel(self.sidebar, text="Saved: 0\nBlur Score: 0", justify="left")
        self.stats_label.pack(pady=20)

        # Main Preview Area
        self.preview_label = ctk.CTkLabel(self, text="Please select a video", fg_color="#121212",
                                          width=640, height=480, corner_radius=12)
        self.preview_label.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def select_video(self):
        file = filedialog.askopenfilename(filetypes=[("Video", "*.mp4 *.mov *.avi *.mkv")])
        if file:
            self.video_path = file
            self.cap = cv2.VideoCapture(self.video_path)
            # Show first frame
            ret, frame = self.cap.read()
            if ret:
                self.update_preview(frame)

    def select_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.save_path = folder

    def update_thresh(self, val):
        self.label_thresh.configure(text=f"Blur Threshold: {int(val)}")

    def toggle_process(self):
        if not self.video_path or not self.save_path:
            return

        if not self.is_running:
            # Setup session folder
            session_id = 0
            while os.path.exists(os.path.join(self.save_path, f"session_{session_id}")):
                session_id += 1
            self.current_session_dir = os.path.join(self.save_path, f"session_{session_id}")
            os.makedirs(self.current_session_dir)

            self.is_running = True
            self.btn_start.configure(text="STOP", fg_color="#a83232", hover_color="#822828")
            self.process_loop()
        else:
            self.is_running = False
            self.btn_start.configure(text="START PROCESSING", fg_color="green", hover_color="#1e7b1e")

    def update_preview(self, frame):
        # Resize and convert BGR -> RGB for display
        display_frame = cv2.resize(frame, (self.imgWidth, self.imgHeight))
        img_rgb = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_rgb)
        # Use CTkImage for high DPI support
        img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(self.imgWidth, self.imgHeight))
        self.preview_label.configure(image=img_ctk, text="")

    def process_loop(self):
        if self.is_running and self.cap:
            ret, frame = self.cap.read()
            if not ret:
                self.toggle_process()
                return

            # Blur Calculation
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            blur_score = int(cv2.Laplacian(gray, cv2.CV_64F).var())
            target_min = int(self.slider_blur.get())

            # Saving Logic
            if blur_score > target_min:
                if self.count % self.moduleVal == 0:
                    save_frame = cv2.resize(frame, (self.imgWidth, self.imgHeight))
                    fname = os.path.join(self.current_session_dir,
                                         f"img_{self.countSave}_{int(time.time() * 1000)}.jpg")
                    cv2.imwrite(fname, save_frame)
                    self.countSave += 1
                self.count += 1

            # UI Updates
            self.stats_label.configure(text=f"Saved: {self.countSave}\nBlur Score: {blur_score}")
            self.update_preview(frame)

            # Schedule next frame - keep GUI responsive
            self.after(1, self.process_loop)


if __name__ == "__main__":
    app = DatasetCreator()
    app.mainloop()
