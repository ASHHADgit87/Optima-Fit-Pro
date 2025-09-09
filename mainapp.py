import tkinter as tk
from tkinter import PhotoImage, Entry, Label, Button, StringVar, Radiobutton
from PIL import Image, ImageTk
import psycopg2
import uuid
from datetime import datetime, timedelta

def connect_db():
    try:
        connection = psycopg2.connect(
            database="postgres",
            user="postgres",
            password="ashhad12",
            host="localhost",
            port="5432"
        )
        return connection
    except Exception as e:
        print("Error connecting to database:", e)
        return None

def validate_input_length(P):
    if len(P) > 28:
        return False
    return True

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Optima Fit Pro".upper())
        self.geometry("1920x770")
        container = tk.Frame(self)
        container.pack(fill="both", expand=True)
        self.frames = {}
        for Page in (LoginPage, SignupPage, HomePage, ChestPage, BackPage, ShoulderPage, TricepsPage, BicepPage, LegPage,
        ChestExercisePage, ChestDietPage, BackExercisePage, BackDietPage,
        ShoulderExercisePage, ShoulderDietPage, TricepsExercisePage, TricepsDietPage, BicepExercisePage, BicepDietPage,
        LegExercisePage, LegDietPage):
            page = Page(container, self)
            self.frames[Page] = page
            page.place(relwidth=1, relheight=1)

        self.check_persistent_login()

    def show_frame(self, page_class, *args):
        frame = self.frames[page_class]
        frame.tkraise()

    def check_persistent_login(self):
        connection = connect_db()
        if connection:
            try:
                cursor = connection.cursor()
                cursor.execute("SELECT email FROM login_info WHERE token IS NOT NULL AND token_expiry > NOW()")
                user = cursor.fetchone()
                if user:
                    self.show_frame(HomePage)
                else:
                    self.show_frame(LoginPage)
            except Exception as e:
                print(f"Database error during persistent login check: {e}")
                self.show_frame(LoginPage)
            finally:
                connection.close()

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.email_var = StringVar()
        self.password_var = StringVar()

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=50, bg="#1e27d4", height=25).place(relx=0.4, rely=0.2)

        Label(self, text="Login".upper(), font=("times", 24, 'bold'), fg="white", bg="#1e27d4").place(
            relx=0.51, rely=0.25, anchor="center")

        Label(self, text="Email:".upper(), font=("times", 14), fg="white", bg="#1e27d4").place(
            relx=0.47, rely=0.3, anchor="e")
        self.email_entry = Entry(self, textvariable=self.email_var, width=30, font=("times", 14), fg="white",
                                 bg="grey", validate="key",
                                 validatecommand=(self.register(validate_input_length), "%P"))
        self.email_entry.place(relx=0.425, rely=0.33, anchor="w")
        self.email_error_label = Label(self, text="", font=("times", 12), fg="white", bg="#1e27d4")
        self.email_error_label.place(relx=0.425, rely=0.365, anchor="w")

        Label(self, text="Password:".upper(), font=("times", 14), fg="white", bg="#1e27d4").place(
            relx=0.5, rely=0.41, anchor="e")
        self.password_entry = Entry(self, textvariable=self.password_var, width=30, font=("times", 14), fg="white",
                                    bg="grey", show="*", validate="key",
                                    validatecommand=(self.register(validate_input_length), "%P"))
        self.password_entry.place(relx=0.425, rely=0.44, anchor="w")
        self.password_error_label = Label(self, text="", font=("times", 12), fg="white", bg="#1e27d4")
        self.password_error_label.place(relx=0.425, rely=0.475, anchor="w")

        login_button = Button(self, text="Login".upper(), width=25, font=("times", 14), command=self.login_user,
                              bg="#050863", fg="white", relief="solid", bd=2)
        login_button.place(relx=0.515, rely=0.51, anchor="center", y=10)

        self.login_error_label = Label(self, text="", font=("times", 12), fg="white", bg="#1e27d4")
        self.login_error_label.place(relx=0.515, rely=0.57, anchor="center")

        Label(self, text="Don't have an account?".upper(), font=("times", 12), fg="white", bg="#1e27d4").place(
            relx=0.41, rely=0.6)
        register_button = Button(self, text="Register".upper(), font=("times", 12), fg="white", bg="#1e27d4",
                                 command=lambda: self.controller.show_frame(SignupPage))
        register_button.place(relx=0.58, rely=0.615, anchor="center")

    def login_user(self):
        email = self.email_var.get()
        password = self.password_var.get()

        self.email_error_label.config(text="")
        self.password_error_label.config(text="")
        self.login_error_label.config(text="")

        error_found = False

        if not email:
            self.email_error_label.config(text="This field is required.")
            error_found = True

        if not password:
            self.password_error_label.config(text="This field is required.")
            error_found = True

        if not error_found:
            connection = connect_db()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute("SELECT * FROM login_info WHERE email = %s AND password = %s", (email, password))
                    user = cursor.fetchone()
                    if user:
                        token = str(uuid.uuid4())
                        expiry = datetime.now() + timedelta(days=2)


                        cursor.execute("UPDATE login_info SET token = %s, token_expiry = %s WHERE email = %s",
                                       (token, expiry, email))
                        connection.commit()
                        self.controller.show_frame(HomePage)
                    else:
                        self.login_error_label.config(text="Incorrect email or password.")
                except Exception as e:
                    self.login_error_label.config(text=f"Database error: {e}")
                finally:
                    cursor.close()
                    connection.close()

class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.username_var = StringVar()
        self.email_var = StringVar()
        self.password_var = StringVar()
        self.gender_var = StringVar()
        self.weight_var = StringVar()

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=50, bg="#1e27d4", height=45).place(relx=0.4, rely=0.05)

        Label(self, text="Signup".upper(), font=("times", 24, 'bold'), fg="white", bg="#1e27d4").place(relx=0.511,
                                                                                                       rely=0.11,
                                                                                                       anchor="center")

        Label(self, text="Username:".upper(), font=("times", 14), fg="white", bg="#1e27d4").place(relx=0.498, rely=0.16,
                                                                                                  anchor="e")
        self.username_entry = Entry(self, textvariable=self.username_var, width=30, font=("times", 14), fg="white",
                                    bg="grey", validate="key",
                                    validatecommand=(self.register(validate_input_length), "%P"))
        self.username_entry.place(relx=0.425, rely=0.19, anchor="w")
        self.username_error_label = Label(self, text="", font=("times", 12), fg="white", bg="#1e27d4")
        self.username_error_label.place(relx=0.425, rely=0.225, anchor="w")

        Label(self, text="Email:".upper(), font=("times", 14), fg="white", bg="#1e27d4").place(relx=0.47, rely=0.26,
                                                                                               anchor="e")
        self.email_entry = Entry(self, textvariable=self.email_var, width=30, font=("times", 14), fg="white", bg="grey",
                                 validate="key", validatecommand=(self.register(validate_input_length), "%P"))
        self.email_entry.place(relx=0.425, rely=0.29, anchor="w")
        self.email_error_label = Label(self, text="", font=("times", 12), fg="white", bg="#1e27d4")
        self.email_error_label.place(relx=0.425, rely=0.325, anchor="w")

        Label(self, text="Password:".upper(), font=("times", 14), fg="white", bg="#1e27d4").place(relx=0.5, rely=0.36,
                                                                                                  anchor="e")
        self.password_entry = Entry(self, textvariable=self.password_var, width=30, font=("times", 14), fg="white",
                                    bg="grey", show="*", validate="key",
                                    validatecommand=(self.register(validate_input_length), "%P"))
        self.password_entry.place(relx=0.425, rely=0.39, anchor="w")
        self.password_error_label = Label(self, text="", font=("times", 12), fg="white", bg="#1e27d4")
        self.password_error_label.place(relx=0.425, rely=0.425, anchor="w")

        Label(self, text="Gender:".upper(), font=("times", 14), fg="white", bg="#1e27d4").place(relx=0.48, rely=0.46,
                                                                                                anchor="e")
        self.male_radio = Radiobutton(self, text="Male", variable=self.gender_var, value="Male", font=("times", 14),
                                      fg="black", bg="#1e27d4")
        self.male_radio.place(relx=0.425, rely=0.49, anchor="w")
        self.female_radio = Radiobutton(self, text="Female", variable=self.gender_var, value="Female",
                                        font=("times", 14), fg="black", bg="#1e27d4")
        self.female_radio.place(relx=0.425, rely=0.52, anchor="w")

        Label(self, text="Weight:".upper(), font=("times", 14), fg="white", bg="#1e27d4").place(relx=0.48, rely=0.56,
                                                                                                anchor="e")
        self.weight_entry = Entry(self, textvariable=self.weight_var, width=30, font=("times", 14), fg="white",
                                  bg="grey", validate="key",
                                  validatecommand=(self.register(validate_input_length), "%P"))
        self.weight_entry.place(relx=0.425, rely=0.59, anchor="w")
        self.weight_error_label = Label(self, text="", font=("times", 12), fg="white", bg="#1e27d4")
        self.weight_error_label.place(relx=0.425, rely=0.625, anchor="w")

        self.signup_status_label = Label(self, text="", font=("times", 12), fg="white", bg="#1e27d4")
        self.signup_status_label.place(relx=0.425, rely=0.325, anchor="w")

        signup_button = Button(self, text="Signup".upper(), width=25, font=("times", 14), command=self.signup_user,
                               bg="#050863", fg="white", relief="solid", bd=2)
        signup_button.place(relx=0.515, rely=0.66, anchor="center", y=10)

        Label(self, text="already have an account?".upper(), font=("times", 12), fg="white", bg="#1e27d4").place(
            relx=0.41, rely=0.77)
        login_button = Button(self, text="login".upper(), font=("times", 12), fg="white", bg="#1e27d4",
                              command=lambda: self.controller.show_frame(LoginPage))
        login_button.place(relx=0.589, rely=0.787, anchor="center")

    def is_numeric(self, value):
        try:
            float(value)
            return True
        except ValueError:
            return False

    def signup_user(self):
        username = self.username_var.get()
        email = self.email_var.get()
        password = self.password_var.get()
        gender = self.gender_var.get()
        weight = self.weight_var.get()

        self.username_error_label.config(text="")
        self.email_error_label.config(text="")
        self.password_error_label.config(text="")
        self.weight_error_label.config(text="")
        self.signup_status_label.config(text="")

        error_found = False

        if not username:
            self.username_error_label.config(text="This field is required.")
            error_found = True

        if not email:
            self.email_error_label.config(text="This field is required.")
            error_found = True

        if not password:
            self.password_error_label.config(text="This field is required.")
            error_found = True

        if not weight:
            self.weight_error_label.config(text="This field is required.")
            error_found = True

        elif not self.is_numeric(weight):
            self.weight_error_label.config(text="Input numbers only")
            error_found = True

        if not error_found:
            connection = connect_db()
            if connection:
                try:
                    cursor = connection.cursor()
                    cursor.execute(
                        "INSERT INTO login_info (username, email, password, gender, weight) VALUES (%s, %s, %s, %s, %s)",
                        (username, email, password, gender, weight))
                    connection.commit()
                    self.signup_status_label.config(text="Signup successful!", fg="green")
                    self.controller.show_frame(HomePage)
                except Exception as e:
                    self.signup_status_label.config(text="Email already exists", fg="white")
                finally:
                    cursor.close()
                    connection.close()

class HomePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=90, bg="#1e27d4", height=48).place(relx=0.285, rely=0.03)

        Label(self, text="select your desired day".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(
            relx=0.341, rely=0.06)

        original_image = Image.open("chests.png")
        self.image = ImageTk.PhotoImage(original_image)
        button = tk.Button(self, text="", image=self.image, compound="top",
                           command=lambda: controller.show_frame(ChestPage))
        button.place(relx=0.33, rely=0.14)

        original_image1 = Image.open("backsss.png")
        self.image1 = ImageTk.PhotoImage(original_image1)
        button = tk.Button(self, text="", image=self.image1, compound="top",
                           command=lambda: controller.show_frame(BackPage))
        button.place(relx=0.55, rely=0.14)

        original_image2 = Image.open("shoulder.png")
        self.image2 = ImageTk.PhotoImage(original_image2)
        button = tk.Button(self, text="", image=self.image2, compound="top",
                           command=lambda: controller.show_frame(ShoulderPage))
        button.place(relx=0.33, rely=0.37)

        original_image3 = Image.open("tricep.png")
        self.image3 = ImageTk.PhotoImage(original_image3)
        button = tk.Button(self, text="", image=self.image3, compound="top",
                           command=lambda: controller.show_frame(TricepsPage))
        button.place(relx=0.55, rely=0.37)

        original_image4 = Image.open("bicep.png")
        self.image4 = ImageTk.PhotoImage(original_image4)
        button = tk.Button(self, text="", image=self.image4, compound="top",
                           command=lambda: controller.show_frame(BicepPage))
        button.place(relx=0.33, rely=0.6)

        original_image5 = Image.open("leg.png")
        self.image5 = ImageTk.PhotoImage(original_image5)
        button = tk.Button(self, text="", image=self.image5, compound="top",
                           command=lambda: controller.show_frame(LegPage))
        button.place(relx=0.55, rely=0.6)

        Button(self, text="log out".upper(), bg="#1e27d4", fg="white",
               command=lambda: controller.show_frame(LoginPage)).place(relx=0.471, rely=0.83)

class ChestPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=90, bg="#1e27d4", height=48).place(relx=0.285, rely=0.03)

        Label(self, text="chest day".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.425,
                                                                                                          rely=0.06)
        Button(self, text="Go back to Homepage".upper(), bg="#1e27d4", fg="white",
               command=lambda: controller.show_frame(HomePage)).place(relx=0.445, rely=0.85)

        original_image12 = Image.open("ex.png")
        self.image12 = ImageTk.PhotoImage(original_image12)
        button = tk.Button(self, text="", image=self.image12, compound="top",
                           command=lambda: controller.show_frame(ChestExercisePage))
        button.place(relx=0.39, rely=0.22)

        original_image13 = Image.open("diet.png")
        self.image13 = ImageTk.PhotoImage(original_image13)
        button = tk.Button(self, text="", image=self.image13, compound="top",
                           command=lambda: controller.show_frame(ChestDietPage))
        button.place(relx=0.39, rely=0.5)

class BackPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=90, bg="#1e27d4", height=48).place(relx=0.285, rely=0.03)


        Label(self, text="back day".upper(),bg = "#1e27d4" ,fg ="white",font=("times", 24, 'bold')).place(relx = 0.435,rely = 0.06)
        Button(self, text="Go back to HomePage".upper(),bg ="#1e27d4" ,fg = "white",command=lambda: controller.show_frame(HomePage)).place(relx = 0.445 , rely = 0.85)

        original_image14 = Image.open("ex.png")
        self.image14 = ImageTk.PhotoImage(original_image14)
        button = tk.Button(self, text="", image=self.image14, compound="top", command=lambda: controller.show_frame(BackExercisePage))
        button.place(relx=0.39, rely=0.22)

        original_image15 = Image.open("diet.png")
        self.image15 = ImageTk.PhotoImage(original_image15)
        button = tk.Button(self, text="", image=self.image15, compound="top", command=lambda: controller.show_frame(BackDietPage))
        button.place(relx=0.39, rely=0.5)

class ShoulderPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=90, bg="#1e27d4", height=48).place(relx=0.285, rely=0.03)


        Label(self, text="shoulder day".upper(),bg = "#1e27d4" ,fg ="white",font=("times", 24, 'bold')).place(relx = 0.405,rely = 0.06)
        Button(self, text="Go back to HomePage".upper(),bg ="#1e27d4" ,fg = "white",command=lambda: controller.show_frame(HomePage)).place(relx = 0.445 , rely = 0.85)

        original_image16 = Image.open("ex.png")
        self.image16 = ImageTk.PhotoImage(original_image16)
        button = tk.Button(self, text="", image=self.image16, compound="top", command=lambda: controller.show_frame(ShoulderExercisePage))
        button.place(relx=0.39, rely=0.22)

        original_image17 = Image.open("diet.png")
        self.image17 = ImageTk.PhotoImage(original_image17)
        button = tk.Button(self, text="", image=self.image17, compound="top", command=lambda: controller.show_frame(ShoulderDietPage))
        button.place(relx=0.39, rely=0.5)

class TricepsPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=90, bg="#1e27d4", height=48).place(relx=0.285, rely=0.03)

        Label(self, text="triceps day".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.42,
                                                                                                        rely=0.06)
        Button(self, text="Go back to HomePage".upper(),bg ="#1e27d4" ,fg = "white",command=lambda: controller.show_frame(HomePage)).place(relx = 0.445 , rely = 0.85  )

        original_image18 = Image.open("ex.png")
        self.image18 = ImageTk.PhotoImage(original_image18)
        button = tk.Button(self, text="", image=self.image18, compound="top", command=lambda: controller.show_frame(TricepsExercisePage))
        button.place(relx=0.39, rely=0.22)

        original_image19 = Image.open("diet.png")
        self.image19 = ImageTk.PhotoImage(original_image19)
        button = tk.Button(self, text="", image=self.image19, compound="top", command=lambda: controller.show_frame(TricepsDietPage))
        button.place(relx=0.39, rely=0.5)

class BicepPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=90, bg="#1e27d4", height=48).place(relx=0.285, rely=0.03)


        Label(self, text="biceps day".upper(),bg = "#1e27d4" ,fg ="white",font=("times", 24, 'bold')).place(relx = 0.425,rely = 0.06)

        Button(self, text="Go back to HomePage".upper(),bg ="#1e27d4" ,fg = "white",command=lambda: controller.show_frame(HomePage)).place(relx = 0.445 , rely = 0.85)

        original_image20 = Image.open("ex.png")
        self.image20 = ImageTk.PhotoImage(original_image20)
        button = tk.Button(self, text="", image=self.image20, compound="top", command=lambda: controller.show_frame(BicepExercisePage))
        button.place(relx=0.39, rely=0.22)

        original_image21 = Image.open("diet.png")
        self.image21 = ImageTk.PhotoImage(original_image21)
        button = tk.Button(self, text="", image=self.image21, compound="top", command=lambda: controller.show_frame(BicepDietPage))
        button.place(relx=0.39, rely=0.5)

class LegPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=90, bg="#1e27d4", height=48).place(relx=0.285, rely=0.03)

        Label(self, text="leg day".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.44,rely=0.06)
        Button(self, text="Go back to HomePage".upper(),bg ="#1e27d4" ,fg = "white",command=lambda: controller.show_frame(HomePage)).place(relx = 0.445 , rely = 0.85)

        original_image22 = Image.open("ex.png")
        self.image22 = ImageTk.PhotoImage(original_image22)
        button = tk.Button(self, text="", image=self.image22, compound="top", command=lambda: controller.show_frame(LegExercisePage))
        button.place(relx=0.39, rely=0.22)

        original_image23 = Image.open("diet.png")
        self.image23 = ImageTk.PhotoImage(original_image23)
        button = tk.Button(self, text="", image=self.image23, compound="top", command=lambda: controller.show_frame(LegDietPage))
        button.place(relx=0.39, rely=0.5)

class ChestExercisePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(self, text="chest exercises".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.402, rely=0.06)
        Button(self, text="Go back to chest day".upper(), bg="#1e27d4", fg="white", command=lambda: controller.show_frame(ChestPage)).place(relx=0.455, rely=0.859)

        exercises = self.fetch_random_exercises()
        self.display_exercises(exercises)

    def fetch_random_exercises(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT chest_exercise, exercise_image_path FROM chest_day ORDER BY RANDOM() LIMIT 5")
        exercises = cursor.fetchall()
        conn.close()
        return exercises

    def display_exercises(self, exercises):
        y_position = 0.19
        for exercise in exercises:
            exercise_text = exercise[0]
            image_path = exercise[1]


            exercise_image = Image.open(image_path)
            exercise_image = exercise_image.resize((100, 100))
            exercise_image = ImageTk.PhotoImage(exercise_image)

            Label(self, text=exercise_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.3, rely=y_position)
            image_label = Label(self, image=exercise_image, bg="#1e27d4")
            image_label.image = exercise_image
            image_label.place(x=950, y=y_position * 710)

            y_position += 0.13

class ChestDietPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(self, text="chest diet".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.432, rely=0.06)
        Button(self, text="Go back to Chest Day".upper(), bg="#1e27d4", fg="white", command=lambda: controller.show_frame(ChestPage)).place(relx=0.455, rely=0.859)

        diets = self.fetch_random_diets()
        self.display_diets(diets)

    def fetch_random_diets(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT chest_diet, diet_image_path FROM chest_day ORDER BY RANDOM() LIMIT 5")
        diets = cursor.fetchall()
        conn.close()
        return diets

    def display_diets(self, diets):
        y_position = 0.19
        for diet in diets:
            diet_text = diet[0]
            image_path = diet[1]


            diet_image = Image.open(image_path)
            diet_image = diet_image.resize((100, 100))
            diet_image = ImageTk.PhotoImage(diet_image)


            Label(self, text=diet_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.35, rely=y_position)
            image_label = Label(self, image=diet_image, bg="#1e27d4")
            image_label.image = diet_image
            image_label.place(x=850, y=y_position * 710)

            y_position += 0.13

class BackExercisePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(self, text="back exercises".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.402, rely=0.06)

        Button(self, text="Go back to back day".upper(), bg="#1e27d4", fg="white", command=lambda: controller.show_frame(BackPage)).place(relx=0.455, rely=0.859)

        exercises = self.fetch_random_exercises()
        self.display_exercises(exercises)

    def fetch_random_exercises(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT back_exercise, exercise_image_path FROM back_day ORDER BY RANDOM() LIMIT 5")
        exercises = cursor.fetchall()
        conn.close()
        return exercises

    def display_exercises(self, exercises):
        y_position = 0.19
        for exercise in exercises:
            exercise_text = exercise[0]
            image_path = exercise[1]


            exercise_image = Image.open(image_path)
            exercise_image = exercise_image.resize((100, 100))
            exercise_image = ImageTk.PhotoImage(exercise_image)


            Label(self, text=exercise_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.3, rely=y_position)
            image_label = Label(self, image=exercise_image, bg="#1e27d4")
            image_label.image = exercise_image
            image_label.place(x=950, y=y_position * 710)

            y_position += 0.13

class BackDietPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(self, text="back diet".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.435, rely=0.06)

        Button(self, text="Go back to back Day".upper(), bg = "#1e27d4", fg="white", command=lambda: controller.show_frame(BackPage)).place(relx=0.455, rely=0.859)

        diets = self.fetch_random_diets()
        self.display_diets(diets)

    def fetch_random_diets(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT back_diet, diet_image_path FROM back_day ORDER BY RANDOM() LIMIT 5")
        diets = cursor.fetchall()
        conn.close()
        return diets

    def display_diets(self, diets):
        y_position = 0.19
        for diet in diets:
            diet_text = diet[0]
            image_path = diet[1]


            diet_image = Image.open(image_path)
            diet_image = diet_image.resize((100, 100))
            diet_image = ImageTk.PhotoImage(diet_image)


            Label(self, text=diet_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.35, rely=y_position)
            image_label = Label(self, image=diet_image, bg="#1e27d4")
            image_label.image = diet_image
            image_label.place(x=850, y=y_position * 710)

            y_position += 0.13

class ShoulderExercisePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)

        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(self, text="shoulder exercises".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.39, rely=0.06)

        Button(self, text="Go back to Shoulder day".upper(), bg="#1e27d4", fg="white", command=lambda: controller.show_frame(ShoulderPage)).place(relx=0.455, rely=0.859)

        exercises = self.fetch_random_exercises()
        self.display_exercises(exercises)

    def fetch_random_exercises(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT shoulder_exercise, exercise_image_path FROM shoulder_day ORDER BY RANDOM() LIMIT 5")
        exercises = cursor.fetchall()
        conn.close()
        return exercises

    def display_exercises(self, exercises):
        y_position = 0.19
        for exercise in exercises:
            exercise_text = exercise[0]
            image_path = exercise[1]

            exercise_image = Image.open(image_path)
            exercise_image = exercise_image.resize((100, 100))
            exercise_image = ImageTk.PhotoImage(exercise_image)

            Label(self, text=exercise_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.3, rely=y_position)
            image_label = Label(self, image=exercise_image, bg="#1e27d4")
            image_label.image = exercise_image
            image_label.place(x=950, y=y_position * 710)

            y_position += 0.13

class ShoulderDietPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)


        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(self, text="shoulder diet".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(relx=0.407, rely=0.06)

        Button(self, text="Go back to Shoulder Day".upper(), bg="#1e27d4", fg="white", command=lambda: controller.show_frame(ShoulderPage)).place(relx=0.455, rely=0.859)

        diets = self.fetch_random_diets()
        self.display_diets(diets)

    def fetch_random_diets(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT shoulder_diet, diet_image_path FROM shoulder_day ORDER BY RANDOM() LIMIT 5")
        diets = cursor.fetchall()
        conn.close()
        return diets

    def display_diets(self, diets):
        y_position = 0.19
        for diet in diets:
            diet_text = diet[0]
            image_path = diet[1]

            diet_image = Image.open(image_path)
            diet_image = diet_image.resize((100, 100))
            diet_image = ImageTk.PhotoImage(diet_image)

            Label(self, text=diet_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.35, rely=y_position)
            image_label = Label(self, image=diet_image, bg="#1e27d4")
            image_label.image = diet_image
            image_label.place(x=850, y=y_position * 710)

            y_position += 0.13

class TricepsExercisePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)


        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(self, text="triceps exercises".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(
            relx=0.4, rely=0.06)

        Button(self, text="Go back to triceps day".upper(), bg="#1e27d4", fg="white",
               command=lambda: controller.show_frame(TricepsPage)).place(relx=0.455, rely=0.859)

        exercises = self.fetch_random_exercises()
        self.display_exercises(exercises)

    def fetch_random_exercises(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT triceps_exercise, exercise_image_path FROM triceps_day ORDER BY RANDOM() LIMIT 5")
        exercises = cursor.fetchall()
        conn.close()
        return exercises

    def display_exercises(self, exercises):
        y_position = 0.19
        for exercise in exercises:
            exercise_text = exercise[0]
            image_path = exercise[1]


            exercise_image = Image.open(image_path)
            exercise_image = exercise_image.resize((100, 100))
            exercise_image = ImageTk.PhotoImage(exercise_image)

            Label(self, text=exercise_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.3, rely=y_position)
            image_label = Label(self, image=exercise_image, bg="#1e27d4")
            image_label.image = exercise_image
            image_label.place(x=950, y=y_position * 710)

            y_position += 0.13

class TricepsDietPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        self.label = Label(self, image=self.bg_image)
        self.label.place(relwidth=1, relheight=1)


        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(self, text="triceps diet".upper(), bg="#1e27d4", fg="white", font=("times", 24, 'bold')).place(
            relx=0.425, rely=0.06)

        Button(self, text="Go back to triceps Day".upper(), bg="#1e27d4", fg="white",
               command=lambda: controller.show_frame(TricepsPage)).place(relx=0.455, rely=0.859)

        diets = self.fetch_random_diets()
        self.display_diets(diets)

    def fetch_random_diets(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT triceps_diet, diet_image_path FROM triceps_day ORDER BY RANDOM() LIMIT 5")
        diets = cursor.fetchall()
        conn.close()
        return diets

    def display_diets(self, diets):
        y_position = 0.19
        for diet in diets:
            diet_text = diet[0]
            image_path = diet[1]
            diet_image = Image.open(image_path)
            diet_image = diet_image.resize((100, 100))
            diet_image = ImageTk.PhotoImage(diet_image)

            Label(self, text=diet_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.35, rely=y_position)
            image_label = Label(self, image=diet_image, bg="#1e27d4")
            image_label.image = diet_image
            image_label.place(x=850, y=y_position * 710)

            y_position += 0.13

class BicepExercisePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        bg_label = Label(self, image=self.bg_image)
        bg_label.place(relwidth=1, relheight=1)


        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(
            self,
            text="bicep exercises".upper(),
            bg="#1e27d4",
            fg="white",
            font=("times", 24, 'bold')
        ).place(relx=0.402, rely=0.06)

        Button(
            self,
            text="Go back to bicep day".upper(),
            bg="#1e27d4",
            fg="white",
            command=lambda: controller.show_frame(BicepPage)
        ).place(relx=0.455, rely=0.859)

        exercises = self.fetch_random_exercises()
        self.display_exercises(exercises)

    def fetch_random_exercises(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT bicep_exercise, exercise_image_path FROM bicep_day ORDER BY RANDOM() LIMIT 5")
        exercises = cursor.fetchall()
        conn.close()
        return exercises

    def display_exercises(self, exercises):
        y_position = 0.19
        for exercise in exercises:
            exercise_text = exercise[0]
            exercise_image_path = exercise[1]

            exercise_image = Image.open(exercise_image_path)
            exercise_image = exercise_image.resize((100, 100))
            exercise_image = ImageTk.PhotoImage(exercise_image)

            Label(self, text=exercise_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.3, rely=y_position)
            image_label = Label(self, image=exercise_image, bg="#1e27d4")
            image_label.image = exercise_image
            image_label.place(x=950, y=y_position * 710)

            y_position += 0.13

class BicepDietPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        bg_label = Label(self, image=self.bg_image)
        bg_label.place(relwidth=1, relheight=1)


        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(
            self,
            text="bicep diet".upper(),
            bg="#1e27d4",
            fg="white",
            font=("times", 24, 'bold')
        ).place(relx=0.435, rely=0.06)

        Button(
            self,
            text="Go back to bicep Day".upper(),
            bg="#1e27d4",
            fg="white",
            command=lambda: controller.show_frame(BicepPage)
        ).place(relx=0.455, rely=0.859)

        diets = self.fetch_random_diets()
        self.display_diets(diets)

    def fetch_random_diets(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT bicep_diet, diet_image_path FROM bicep_day ORDER BY RANDOM() LIMIT 5")
        diets = cursor.fetchall()
        conn.close()
        return diets

    def display_diets(self, diets):
        y_position = 0.19
        for diet in diets:
            diet_text = diet[0]
            diet_image_path = diet[1]

            diet_image = Image.open(diet_image_path)
            diet_image = diet_image.resize((100, 100))
            diet_image = ImageTk.PhotoImage(diet_image)

            Label(self, text=diet_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.35, rely=y_position)
            image_label = Label(self, image=diet_image, bg="#1e27d4")
            image_label.image = diet_image
            image_label.place(x=850, y=y_position * 710)

            y_position += 0.13

class LegExercisePage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        bg_label = Label(self, image=self.bg_image)
        bg_label.place(relwidth=1, relheight=1)


        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(
            self,
            text="leg exercises".upper(),
            bg="#1e27d4",
            fg="white",
            font=("times", 24, 'bold')
        ).place(relx=0.405, rely=0.06)

        Button(
            self,
            text="Go back to leg day".upper(),
            bg="#1e27d4",
            fg="white",
            command=lambda: controller.show_frame(LegPage)
        ).place(relx=0.455, rely=0.859)

        exercises = self.fetch_random_exercises()
        self.display_exercises(exercises)

    def fetch_random_exercises(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT leg_exercise, exercise_image_path FROM leg_day ORDER BY RANDOM() LIMIT 5")
        exercises = cursor.fetchall()
        conn.close()
        return exercises

    def display_exercises(self, exercises):
        y_position = 0.19
        for exercise in exercises:
            exercise_text = exercise[0]
            exercise_image_path = exercise[1]

            exercise_image = Image.open(exercise_image_path)
            exercise_image = exercise_image.resize((100, 100))
            exercise_image = ImageTk.PhotoImage(exercise_image)

            Label(self, text=exercise_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.3, rely=y_position)
            image_label = Label(self, image=exercise_image, bg="#1e27d4")
            image_label.image = exercise_image
            image_label.place(x=950, y=y_position * 710)

            y_position += 0.13

class LegDietPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_image = PhotoImage(file="ash7.png")
        bg_label = Label(self, image=self.bg_image)
        bg_label.place(relwidth=1, relheight=1)


        Label(self, text="", width=120, bg="#1e27d4", height=49).place(relx=0.225, rely=0.03)

        Label(
            self,
            text="leg diet".upper(),
            bg="#1e27d4",
            fg="white",
            font=("times", 24, 'bold')
        ).place(relx=0.435, rely=0.06)

        Button(
            self,
            text="Go back to leg Day".upper(),
            bg="#1e27d4",
            fg="white",
            command=lambda: controller.show_frame(LegPage)
        ).place(relx=0.455, rely=0.859)

        diets = self.fetch_random_diets()
        self.display_diets(diets)

    def fetch_random_diets(self):
        conn = connect_db()
        if conn is None:
            return []

        cursor = conn.cursor()
        cursor.execute("SELECT leg_diet, diet_image_path FROM leg_day ORDER BY RANDOM() LIMIT 5")
        diets = cursor.fetchall()
        conn.close()
        return diets

    def display_diets(self, diets):
        y_position = 0.19
        for diet in diets:
            diet_text = diet[0]
            diet_image_path = diet[1]

            diet_image = Image.open(diet_image_path)
            diet_image = diet_image.resize((100, 100))
            diet_image = ImageTk.PhotoImage(diet_image)

            Label(self, text=diet_text, bg="#1e27d4", fg="white", font=("times", 16)).place(relx=0.35, rely=y_position)
            image_label = Label(self, image=diet_image, bg="#1e27d4")
            image_label.image = diet_image
            image_label.place(x=850, y=y_position * 710)
            y_position += 0.13

if __name__ == "__main__":
    app = App()
    app.mainloop()
