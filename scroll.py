import tkinter as tk
from tkinter import filedialog, Canvas, Scrollbar, Frame
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import io
import anki
import subprocess

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

        # Bind mouse wheel event for scrolling, with platform-specific adjustments
        self.bind_mouse_wheel()

        # Enable keyboard focus and bind key events for scrolling and page navigation
        self.canvas.focus_set()
        self.bind_keys()

        self.open_pdf_button = tk.Button(self, text="Open PDF", command=self.open_pdf)
        self.open_pdf_button.pack(side=tk.BOTTOM)

        self.doc = None
        self.images = []
        
        self.current_page = 0  # Track the current page index
        self.page_info = []  # Keep track of each page's starting y position in the canvas
        self.clicks = []  # To track the positions of clicks
        self.pdf_loaded = False

        self.front_img = None
        self.back_img = None
    
    def select_file(self):
        #filedialog.askopenfilename(initialdir = "/home/len1218")
        try:
            file_path = subprocess.check_output(["zenity", "--file-selection"]).decode().strip()
            return file_path
        except subprocess.CalledProcessError:
            # Handle cancellation or error
            return None

    def open_pdf(self):
        file_path = self.select_file()
        if file_path:
            self.doc = fitz.open(file_path)
            self.load_visible_pages()

    def load_visible_pages(self, event=None):
        if not self.doc:
            return
        self.canvas.delete("all")
        self.images = []

        self.page_info = [0]  # Reset for the new document

        canvas_width = self.canvas.winfo_width()
        total_height = 0
        for page_num in range(len(self.doc)):
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(144 / 72, 144 / 72))  # Adjust scale here as needed
            img = Image.open(io.BytesIO(pix.tobytes()))
            
            # Scale image to fit canvas width while maintaining aspect ratio
            aspect_ratio = img.height / img.width
            new_width = canvas_width
            new_height = int(aspect_ratio * new_width)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

            pil_img = ImageTk.PhotoImage(img)
            self.images.append(pil_img)

            self.canvas.create_image(0, total_height, anchor=tk.NW, image=pil_img)
            self.page_info.append(total_height)  # Record the starting position of the next page
            total_height += new_height

        self.canvas.configure(scrollregion=(0, 0, canvas_width, total_height))
        self.goto_page(self.current_page)
        self.pdf_loaded = True

    def bind_mouse_wheel(self):
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # For Windows and MacOS
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)  # For Linux, scroll up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)  # For Linux, scroll down
        self.canvas.bind("<Button-1>", self.handle_click)


    def on_mouse_wheel(self, event):
        if event.num == 4:  # Linux scroll up
            delta = -1
        elif event.num == 5:  # Linux scroll down
            delta = 1
        else:  # Windows and MacOS
            delta = event.delta / -120
        self.canvas.yview_scroll(int(delta), "units")

    def bind_keys(self):
        self.canvas.bind("<Left>", lambda event: self.navigate_pages(-1))
        self.canvas.bind("<Right>", lambda event: self.navigate_pages(1))
        self.canvas.bind("<Up>", lambda event: self.canvas.yview_scroll(-1, "units"))
        self.canvas.bind("<Down>", lambda event: self.canvas.yview_scroll(1, "units"))
        self.canvas.bind("<Prior>", lambda event: self.canvas.yview_scroll(-1, "pages"))
        self.canvas.bind("<Next>", lambda event: self.canvas.yview_scroll(1, "pages"))

    def navigate_pages(self, direction):
        # Get the current scroll position in terms of fraction of the total scrollable area
        scroll_pos_fraction = self.canvas.yview()[0]
        # Convert this to the actual scroll position in terms of canvas units
        scroll_pos_units = scroll_pos_fraction * self.canvas.bbox("all")[3]
        self.current_page = self.get_page(scroll_pos_units)

        # Calculate the new page index
        new_page = self.current_page + direction
        # Boundary check
        if 0 <= new_page < len(self.doc):
            self.goto_page(new_page)

    def goto_page(self, page):
        if 0 <= page < len(self.page_info):
            # Scroll to the y position of the target page
            pos = self.page_info[page] / self.canvas.bbox("all")[3]  # Convert to fraction
            self.canvas.yview_moveto(pos)
            self.current_page = page  # Update the current page index

    def handle_click(self, event):
        if not self.pdf_loaded:
            return
        # Convert canvas click Y-coordinate to document position
        canvas_y = self.canvas.canvasy(event.y)
        if len(self.clicks) < 2:  # We need only the first two clicks
            self.clicks.append(canvas_y)
            if len(self.clicks) == 2:
                self.create_snippet_from_clicks()
                self.clicks.clear()  # Reset clicks after processing

    def create_snippet_from_clicks(self):
        if len(self.clicks) != 2:
            return  # Ensure we have exactly two clicks
        
        start, end = sorted(self.clicks)  # Ensure start is less than end
        
        # Calculate the corresponding positions on the actual PDF page(s)
        # This example assumes a single-page PDF for simplicity. For multi-page
        # handling, you'd need to adjust the logic to find the correct page(s)
        # and calculate positions within those pages.
        page_num = self.get_page(start)
        current_height = self.page_info[page_num]
        
        #page_height = sum([self.doc[page_num].bound().height for page_num in range(len(self.doc))])
        #scale_factor = self.canvas.winfo_height() #/ page_height
        #pdf_start = start #/ scale_factor
        #pdf_end = end #/ scale_factor
        
        # Assume a uniform scale factor for simplicity; adjust based on your application's logic
        scale_factor = self.canvas.winfo_width() / self.doc[page_num-1].rect.width
        pdf_start = (start-current_height) / scale_factor
        pdf_end = (end-current_height) / scale_factor
        
        page = self.doc.load_page(page_num-1 )
        pix = page.get_pixmap()

        # Assuming the snippet does not span multiple pages
        print(0, pdf_start, pix.width, pdf_end)
        clip_rect = fitz.Rect(0, pdf_start, pix.width, pdf_end)
        snippet_pix = page.get_pixmap(clip=clip_rect)
        
        # Save the snippet as an image
        snippet_image = Image.open(io.BytesIO(snippet_pix.tobytes()))
        if self.front_img == None:
            self.front_img = snippet_image
        else:
            self.back_img = snippet_image
            anki.add_image_card_wrapper(self.front_img,self.back_img)
            self.front_img = None
            self.back_img = None


        #snippet_image.save("snippet.png")
    


    def get_page(self,scroll_pos_units):
        scroll_pos_units = round(scroll_pos_units)
        for i, pos in enumerate(self.page_info):
            # Assuming self.page_info stores tuples of (start_pos, end_pos) for each page
            if pos > scroll_pos_units:
                # The previous page is the current page since we've now gone past the current scroll position
                ret =  max(0, i - 1)
                break
        else:
            # If we didn't break from the loop, we are on or past the last page
            ret =  len(self.page_info) - 1

        #print("Current page:", ret)
        return ret


if __name__ == "__main__":
    app = PDFViewer()
    app.mainloop()

