import os
import tkinter as tk
from tkinter import ttk, font
from PIL import Image, ImageTk
import win32gui
import win32con
import win32api
import random

class GameDraft:
    def __init__(self, canvas, rolled_game, x_position, y_position, scale=[1.0,1.0]) -> None:
        self.rolled_game=rolled_game
        self.canvas = canvas
        self.primaries=[]
        self.curse=[]
        self.secondaries=[]
        self.scale=scale
        self.GenerateCardImageButtons(rolled_game, x_position,y_position)
    
    def GenerateCardImageButtons(self, rolled_game, x_position, y_position):
        #NOTE: Insert duplicate reroll  code here, and/or additional objective draft.
        self.primaries.clear()
        self.curse.clear()
        self.secondaries.clear()
        
        curse = bool(random.randrange(10)==0)
        #curse = False
        match rolled_game:
            case _:
                self.primaries.append(self.CardImageButtonFactory(x_position, y_position, 'p', rolled_game))
                self.secondaries.append(self.CardImageButtonFactory(x_position, y_position, 's', rolled_game))
        if (curse):
            self.curse.append(self.CardImageButtonFactory(x_position, y_position, 'c', rolled_game))
            # [Petra]: Debug
            #print("Curse rolled")
        self.PlaceCardImageButtons(rolled_game, x_position, y_position)
        return

    def CardImageButtonFactory(self, x_position, y_position, prefix, rolled_game):
        btn = CardImageButton(self.canvas, x_position, y_position, prefix, rolled_game, self.scale)
        btn.button_widget.config(command= btn.roll_objective_from_game)
        match prefix:
            case 'p':
                self.primaries.append(btn)
            case 's':
                self.secondaries.append(btn)
            case 'c':
                self.curse.append(btn)
            case _:
                print("Error: Unhandled prefix passed to CardImageButtonFactory()")
        return btn
    
    def PlaceCardImageButtons(self, rolled_game, x_position, y_position):
        if len(self.curse) > 0:
            curse_space = 1.0
        else:
            curse_space = 0
        for p in range(len(self.primaries)):
            self.primaries[p].button_widget.place(x=x_position, y=y_position+(200*p))
        for s in range(len(self.secondaries)):
            self.secondaries[s].button_widget.place(x=x_position + int(CardImageButton.button_width*self.scale[0]*(1+curse_space) + CardImageButton.button_x_spacing*self.scale[0]*(1+curse_space)), y=y_position+(200*s))
        for c in range(len(self.curse)):
            self.curse[c].button_widget.place(x=x_position + int(CardImageButton.button_width*self.scale[0] + CardImageButton.button_x_spacing*self.scale[0]), y=y_position+(200*c))

class CardImageButton:
    button_width = 189
    button_height = 270
    button_x_spacing = 10
    def __init__(self, canvas, x, y, prefix, rolled_game, scale=[1.0,1.0]):
        self.scale=scale
        self.image = []
        self.rolled_game = rolled_game
        self.button_widget = tk.Button(canvas, image=None,width=int(CardImageButton.button_width*self.scale[0]), height=int(CardImageButton.button_height*self.scale[1]))
        self.prefix = prefix
        self.roll_objective_from_game()
    
    def roll_objective_from_game(self):
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))+'\\Resources'
        image_folder = os.path.join(__location__, self.rolled_game)

        _image = Image.open(self.random_image_path_from_folder(image_folder, self.prefix))
        _image = _image.resize((int(CardImageButton.button_width*self.scale[0]), int(CardImageButton.button_height*self.scale[1])))
        _photo = ImageTk.PhotoImage(_image)

        self.image.clear()
        self.image.append(_photo)
        # [Petra]: Having CardImageButton.image be an array that we reference the tail of is likely unneeded. But this code worked for me. ¯\_(ツ)_/¯
        self.button_widget.config(image=self.image[-1])

    def random_image_path_from_folder(self,image_folder, prefix):
        images = [f for f in os.listdir(image_folder) if f.startswith(prefix) and f.endswith(('.png', '.jpg', '.jpeg'))]
        output = os.path.join(image_folder, random.choice(images))
        # [Petra]: Debugging; print loaded image filepath
        #print(str(output))
        return output

class ImageGalleryApp:
    def __init__(self, root, image_folder):
        self.root = root
        self.image_folder = image_folder
        self.images = []
        self.current_page = 0
        self.images_per_page = 24
        self.clicked_images = {}
        self.done_button_clicked = False

        self.drafted_games = []

        self.load_images()
        self.create_widgets()

    def load_images(self):
        # Load images from the specified folder
        image_files = [f for f in os.listdir(self.image_folder) if f.endswith(('.png', '.jpg', '.jpeg'))]
        for filename in image_files:
            image_path = os.path.join(self.image_folder, filename)
            image = Image.open(image_path)
            image = image.resize((CardImageButton.button_width, CardImageButton.button_height))  # Resize the image
            self.images.append((image, filename))  # Store both image and filename

    def create_widgets(self):

        self.background_image = Image.open("Resources/bg.png")  # Replace with your background image path
        self.background_photo = ImageTk.PhotoImage(self.background_image)

        # Create a Label to display the background image
        bg_label = tk.Label(self.root, image=self.background_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        
        self.canvas = tk.Canvas(root, width=1920, height=1080, highlightthickness=0, bg='#DAEE01')
        hwnd = self.canvas.winfo_id()
        colorkey = win32api.RGB(218,238,1) 
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd,win32con.GWL_EXSTYLE,new_exstyle)
        win32gui.SetLayeredWindowAttributes(hwnd,colorkey,255,win32con.LWA_COLORKEY)

        self.canvas.place(x=0, y=0)

        #[Petra]: Gotta update our font drip before we publish this. Arial and Helvetica do not have the juice.
        #[Petra]: They are neither fleek nor on-point.
        close_font = font.Font(family="Arial", size=16, weight="bold")  # Adjust font properties as needed
        self.close_button = tk.Label(self.root, text="X", font=close_font, bg="red", fg="white", cursor="hand2")
        self.close_button.place(x=1880, y=10)  # Adjust the coordinates as needed
        self.close_button.bind("<Button-1>", self.close_program)

        self.next_button = ttk.Button(self.root, text="Next", command=self.next_page, style="Large.TButton")
        self.next_button.place(x=1700, y=1000)

        self.prev_button = ttk.Button(self.root, text="Previous", command=self.prev_page, style="Large.TButton")
        self.prev_button.place(x=220, y=1000)

        self.done_button = ttk.Button(self.root, text="I'm Done Drafting my Deck!", command=self.choose_number_of_drafts, style="Large.TButton")
        self.done_button.place(x=950, y=1000, anchor=tk.CENTER)

        self.clicked_frame = tk.Frame(self.root)
        self.clicked_frame.place(x=950, y=940, anchor=tk.CENTER)
        
        self.show_page(0)

    # [Petra]: Probably rename this function? 
    def show_page(self, page_number):
        start_idx = page_number * self.images_per_page
        end_idx = min((page_number + 1) * self.images_per_page, len(self.images))

        for widget in self.canvas.winfo_children():
            widget.grid_forget()  # Remove all previous buttons

        for i in range(start_idx, end_idx):
            image, filename = self.images[i]
            photo = ImageTk.PhotoImage(image)
            btn = tk.Button(self.canvas, image=photo, width=CardImageButton.button_width, height=CardImageButton.button_height,
                            command=lambda f=filename: self.add_to_clicked_images(f))  # Pass filename to lambda
            btn.image = photo
            btn.grid(row=(i - start_idx) // 8, column=(i - start_idx) % 8, padx=22, pady=10)

    def next_page(self):
        self.current_page = (self.current_page + 1) % ((len(self.images) + self.images_per_page - 1) // self.images_per_page)
        self.show_page(self.current_page)

    def prev_page(self):
        self.current_page = (self.current_page - 1) % ((len(self.images) + self.images_per_page - 1) // self.images_per_page)
        self.show_page(self.current_page)

    def add_to_clicked_images(self, filename):
        if filename in self.clicked_images:
            self.clicked_images[filename] += 1
        else:
            self.clicked_images[filename] = 1

        clicked_image_path = os.path.join(self.image_folder, filename)
        clicked_image = Image.open(clicked_image_path)
        clicked_image = clicked_image.resize((CardImageButton.button_width // 4, CardImageButton.button_height // 4))
        clicked_photo = ImageTk.PhotoImage(clicked_image)

        clicked_label = tk.Label(self.clicked_frame, image=clicked_photo)
        clicked_label.image = clicked_photo
        clicked_label.pack(side=tk.LEFT)

    def choose_number_of_drafts(self):
        self.clear_screen()

        # Create a label asking how many games to play
        self.games_label = tk.Label(self.root, text="How many games would you like to play?", font=("Helvetica", 18))
        self.games_label.place(x=960, y=500, anchor=tk.CENTER)

        # Create buttons for 1, 3, and 5 games
        self.games_selection = tk.StringVar()  # Variable to store the selected number of games

        def set_games_selection(value):
            self.games_selection.set(value)

        self.games_1_button = tk.Button(self.root, text="1", font=("Helvetica", 24), command=lambda: set_games_selection("1"))
        self.games_1_button.place(x=800, y=600, anchor=tk.CENTER)

        self.games_3_button = tk.Button(self.root, text="3", font=("Helvetica", 24), command=lambda: set_games_selection("3"))
        self.games_3_button.place(x=960, y=600, anchor=tk.CENTER)

        self.games_5_button = tk.Button(self.root, text="5", font=("Helvetica", 24), command=lambda: set_games_selection("5"))
        self.games_5_button.place(x=1120, y=600, anchor=tk.CENTER)

        # Create an entry box for custom number of games
        self.custom_games_entry = tk.Entry(self.root, textvariable=self.games_selection, font=("Helvetica", 24), justify="center")
        self.custom_games_entry.place(x=960, y=700, anchor=tk.CENTER)

        # Create a "Start" button to proceed
        self.start_button = ttk.Button(self.root, text="Start", command=self.prep_canvas_for_run, style="Large.TButton")
        self.start_button.place(x=960, y=800, anchor=tk.CENTER)

    def prep_canvas_for_run(self):
        self.games_1_button.place_forget()
        self.games_3_button.place_forget()
        self.games_5_button.place_forget()
        self.custom_games_entry.place_forget()
        self.start_button.place_forget()
        self.games_label.place_forget()

        # Clear the previous screen
        self.canvas.destroy()
        self.clicked_frame.destroy()
        
        # Create a new canvas for displaying selected images
        # [Petra]: Consider defining a single canvas in init which would be reused between functions.
        self.canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0, bg='#DAEE01')
        hwnd = self.canvas.winfo_id()
        colorkey = win32api.RGB(218, 238, 1)
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_exstyle)
        win32gui.SetLayeredWindowAttributes(hwnd, colorkey, 255, win32con.LWA_COLORKEY)
        self.canvas.place(x=0, y=0)

        self.clicked_frame = tk.Frame(self.root)
        self.clicked_frame.place(x=950, y=940, anchor=tk.CENTER)

        self.start_games()

    def clear_screen(self):
        self.done_button_clicked = True
        self.canvas.destroy()
        self.clicked_frame.destroy()
        self.next_button.place_forget()
        self.prev_button.place_forget()
        self.done_button.place_forget()

        self.canvas = tk.Canvas(self.root, width=1920, height=1080, highlightthickness=0, bg='#DAEE01')
        hwnd = self.canvas.winfo_id()
        colorkey = win32api.RGB(218, 238, 1)
        wnd_exstyle = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        new_exstyle = wnd_exstyle | win32con.WS_EX_LAYERED
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, new_exstyle)
        win32gui.SetLayeredWindowAttributes(hwnd, colorkey, 255, win32con.LWA_COLORKEY)
        self.canvas.place(x=0, y=0)

        self.clicked_frame = tk.Frame(self.root)
        self.clicked_frame.place(x=950, y=940, anchor=tk.CENTER)
        
    def start_games(self):
        self.drafted_games.clear()
        self.clear_screen()
        if self.games_selection:
            weighted_images = []
            for rolled_game, weight in self.clicked_images.items():
                weighted_images.extend([rolled_game] * weight)
            
            x_position = 50
            y_position = 100

            selected_images = random.sample(weighted_images, int(self.games_selection.get()))
            self.reroll_button = tk.Button(self.root, text="REROLL", font="Helvetica", bg="black", fg="white", cursor="hand2", command=self.start_games)
            self.reroll_button.place(x=940, y=10)  # Adjust the coordinates as needed

            for rolled_game in selected_images:
                rolled_game_in = rolled_game.split('.')[0]
                self.drafted_games.append(GameDraft(self.canvas,rolled_game_in,x_position,y_position,[1.0,1.0]))

                x_position += 650
                if(x_position > 1900 and y_position < 470):
                    x_position = 317
                    y_position = 470
           

        if int(self.games_selection.get()) < 1:
            print("Please select the number of games before starting.")              
                           
    def close_program(self, event):
        self.root.destroy()

if __name__ == "__main__":
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))) + "\\Resources"
    image_folder_path = os.path.join(__location__, 'Card Backs App')  # Replace with the actual folder path containing your images

    root = tk.Tk()
    app = ImageGalleryApp(root, image_folder_path)

    root.attributes('-fullscreen', True)
    root.mainloop()
