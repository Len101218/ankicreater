import tkinter as tk
from tkinter import filedialog, Canvas, Scrollbar, Frame
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import io

class PDFViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PDF Viewer")
        self.geometry("800x600")

        self.container = Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.canvas = Canvas(self.container, bg="gray")
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = Scrollbar(self.container, command=self.canvas.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.bind_mouse_wheel()
        self.canvas.focus_set()
        self.bind_keys()

        self.open_pdf_button = tk.Button(self, text="Open PDF", command=self.open_pdf)
        self.open_pdf_button.pack(side=tk.BOTTOM)

        self.doc = None
        self.images = []
        
        self.current_page = 0
        self.page_info = []
        self.zoom_factor = 1.0  # New attribute for zoom factor

        self.pdf_loaded = False

    # Existing methods up to load_visible_pages

    def load_visible_pages(self, event=None):
        if not self.doc:
            return
        self.canvas.delete("all")
        self.images = []

        self.page_info = [0]

        canvas_width = self.canvas.winfo_width()
        total_height = 0
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(144 / 72 * self.zoom_factor, 144 / 72 * self.zoom_factor))  # Adjust zoom here
            img = Image.open(io.BytesIO(pix.tobytes()))
            
            aspect_ratio = img.height / img.width
            new_width = canvas_width
            new_height = int(aspect_ratio * new_width)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            pil_img = ImageTk.PhotoImage(img)
            self.images.append(pil_img)

            self.canvas.create_image(0, total_height, anchor=tk.NW, image=pil_img)
            self.page_info.append(total_height)
            total_height += new_height

        self.canvas.configure(scrollregion=(0, 0, canvas_width, total_height))
        self.goto_page(self.current_page)

    # Existing methods up to bind_keys

    def bind_keys(self):
        super().bind_keys()  # Call the original bind_keys method
        self.bind("<Control-plus>", lambda event: self.adjust_zoom(1.1))  # Zoom in
        self.bind("<Control-minus>", lambda event: self.adjust_zoom(0.9))  # Zoom out
        self.bind("<Control-0>", lambda event: self.reset_zoom())  # Reset zoom

    def adjust_zoom(self, factor):
        self.zoom_factor *= factor
        self.load_visible_pages()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self.load_visible_pages()

    # Rest of your class implementation remains unchanged

if __name__ == "__main__":
    app = PDFViewer()
    app.mainloop()

