import requests
import tkinter as tk
from tkinter import messagebox
import json
import customtkinter as ctk
from PIL import Image, ImageTk
import random
import winsound
import html
import imageio
import threading
import time

app = ctk.CTk()
app.title("Gamer's Gambit")
app.geometry("380x600")
app.resizable(False, False)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

bg_image_path = "C:\\Users\\Trisha\\Documents\\GitHub\\Code-lab-II\\OPEN TRIVIA.png"
bg_image = Image.open(bg_image_path)
tk_bg_image = ImageTk.PhotoImage(bg_image)

categories_data = {}
chosen_difficulty = 'medium'  # setting default difficulty here
current_question_index = 0  # global index to keep track of current question
question_count_label = ctk.CTkLabel(app) 
question_count_label.pack()

player_points = 0  
video_label = None

correct_sound_path = "correct_answer.wav"
startup_sound = r'C:\Users\Trisha\Documents\GitHub\Code-lab-II\val_main.wav'

def play_startup_sound():
    winsound.PlaySound(startup_sound, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_LOOP)

    
def start_game():
    clear_content()
    show_difficulty_selection()
    
    global current_question_index, player_points
    current_question_index = 0
    player_points = 0
    # Set up background image
    global tk_bg_image  # Declare tk_bg_image as a global to ensure its reference is kept
    background_label = ctk.CTkLabel(app, image=tk_bg_image, text='')
    background_label.place(relwidth=1, relheight=1)
    background_label.image = tk_bg_image  # Keep a reference

    # Start button
    start_button = ctk.CTkButton(app, text="Start", command=show_game_description, width=200, height=30, hover_color= 'navy')
    start_button.place(relx=0.5, rely=0.95, anchor=ctk.CENTER)
    
def clean_html_entities(text):
    # Converts the random characters in json file to alphabets
    return html.unescape(text)

def download_categories():
    try:
        categories_url = 'https://opentdb.com/api.php?amount=20&category=15'
        response = requests.get(categories_url) 
        
        if response.status_code == 200:
            categories_data = response.json()

            # Write to a file
            with open('categories.json', 'w') as f:
                json.dump(categories_data, f, indent=4)
            print("Categories data saved!")  # Notify in the terminal

            return categories_data  # Returning data could be used elsewhere
        
        else:
            # If the response was not 200, show an API error message
            messagebox.showerror("API Error", "Could not fetch trivia questions: Status Code {}".format(response.status_code))
            return None
    except requests.exceptions.RequestException as e:
        # For network-related errors
        messagebox.showerror("Network Error", "There was a network error: {}".format(e))
        return None

download_categories()  
def show_game_description():
    clear_content()
    
    
    global video_label  
    if video_label is None:
        video_label = ctk.CTkLabel(app)  
        video_label.place(relwidth=1, relheight=1)
    
    frame = ctk.CTkFrame(app, fg_color=None)
    frame.pack(pady=70, padx=30, fill='both', expand=True)
    
    video_path = r"C:\Users\Trisha\Documents\GitHub\Code-lab-II\bg.mp4"
    video_reader = imageio.get_reader(video_path, 'ffmpeg')

    def update_video_label(reader):
        try:
            frame = next(reader)  # Get the next frame from the iterator
            frame_image = ImageTk.PhotoImage(image=Image.fromarray(frame))
            video_label.configure(image=frame_image)
            video_label.image = frame_image  # Keep a reference
            app.after(33, lambda: update_video_label(reader))  # Continue updating
        except StopIteration:
            
            video_reader.close()
        except Exception as e:
            print(f"Failed to update video label: {e}")

    # Get an iterator over the video frames
    frame_iterator = iter(video_reader.iter_data())
    update_video_label(frame_iterator)

    description_label = ctk.CTkLabel(
        frame,
        text="Welcome to Gamer's Gambit",
        font=("Roboto", 30, 'bold'),
        text_color='white', fg_color= None,
        wraplength=250
    )
    description_label.pack(pady=5)
    small_description_label = ctk.CTkLabel(
        frame,
        text=("This is a trivia game that challenges your knowledge about "
              "online video games. Think fast and be quick - each question "
              "is timed to a limit of 5 seconds, and failing to respond before "
              "the clock runs out will cost you one point!"),
        justify=ctk.CENTER,  
        wraplength=200,  
        fg_color=None,  
        text_color="#CCCCCC",  
        font=('Comic Sans MS', 16)
    )
    small_description_label.pack(pady=(20), padx=(30))
    
    continue_button = ctk.CTkButton(
        frame,
        text="Continue",
        command=show_difficulty_selection,
        hover_color='navy',
        width=200,
        height=50
    )
    continue_button.pack(pady=20)


after_call_id = None
def update_video_label(frame_image_data):
    global after_call_id
    if video_label.winfo_exists():  # Check to ensure widget exists before updating
        try:
            frame = next(reader)  # Get the next frame
            frame_image = ImageTk.PhotoImage(image=Image.fromarray(frame))
            video_label.configure(image=frame_image)
            video_label.image = frame_image
            after_call_id = app.after(33, lambda: update_video_label(reader))
        except StopIteration:
            reader.close()
        except Exception as e:
            print(f"Failed to update video label: {e}")
    else:
        # If it doesn't exist, cancel the upcoming 'after' call
        if after_call_id is not None:
            app.after_cancel(after_call_id)
            after_call_id = None
            
def load_questions():
    global categories_data
    try:
        with open('categories.json', 'r') as f:
            categories_data = json.load(f)
    except FileNotFoundError:
        categories_data = download_categories()  # Attempt to download if not found

counter_id = None
def clear_content():
    global after_call_id, video_label
    if after_call_id is not None:
        app.after_cancel(after_call_id)
        after_call_id = None
    video_label = None
        
    global counter_id, timer_label
    if counter_id is not None:
        app.after_cancel(counter_id)
        counter_id = None
    for widget in app.winfo_children():
        if widget!= question_count_label:
            widget.destroy()
    timer_label = None
     


def show_difficulty_selection():
    global question_count_label
    question_count_label.pack_forget()
    clear_content()
    
    difficulty_frame = ctk.CTkFrame(app)
    difficulty_frame.place(x=100, y=150)
    text_frame= ctk.CTkLabel(difficulty_frame, text='Choose your difficulty')
    text_frame.pack(pady=10, padx=10, fill='both', expand= True)
    
    difficulties = ['easy', 'medium', 'hard', 'any']
    difficulty_buttons = {}
    
    def make_difficulty_button(diff):
        return ctk.CTkButton(
            difficulty_frame,
            text=diff.capitalize(),
            width=200,
            height=40,
            hover_color='purple',
            command=lambda: on_difficulty_button_click(diff)
        )
    
    for diff in difficulties:
        b = make_difficulty_button(diff)
        b.pack(pady=5)
        difficulty_buttons[diff] = b


def on_difficulty_button_click(difficulty):
    global chosen_difficulty
    chosen_difficulty = difficulty

    filtered_questions = get_filtered_questions(chosen_difficulty)
    start_quiz(filtered_questions)


def get_filtered_questions(difficulty_level):
    if not categories_data:
        load_questions()  # Ensure we've loaded questions

    if difficulty_level == "any":
        return categories_data['results']
    
    return [q for q in categories_data['results'] if q.get("difficulty") == difficulty_level]

question_count_label = None


def update_question_count():
    global current_question_index, question_count_label
    
    if question_count_label is not None:
        text= f"Question {current_question_index + 1} of {len(app.questions)}"
        question_count_label.configure(text=text)
        question_count_label.pack()
        
def setup_question_count_label():
    global question_count_label
    question_count_label = ctk.CTkLabel(app)
    question_count_label.pack()


setup_question_count_label()    

def start_quiz(questions):
    global current_question_index
    clear_content()
    question_count_label.pack()

    app.questions = questions
    current_question_index = 0
    update_question_count()

    show_question(app.questions[current_question_index])
    app.questions = questions
    current_question_index = 0
    show_question(app.questions[current_question_index])

def show_question(question):
    global current_question_index, timer_label, counter_id
    clear_content()
    update_question_count()
    
    question_text = clean_html_entities(question['question'])
    question_label = ctk.CTkLabel(app, text=question_text, wraplength=300) # Use question_text
    question_label.pack(pady=20)
    
    if current_question_index >= len(app.questions):
        messagebox.showinfo("End of Quiz", "No more questions available.")
        return
        
    timer_label = ctk.CTkLabel(app, text="Timer: 5", font=("Arial", 22, "bold"))
    timer_label.pack(pady=(10, 20))

    counter_id = None 
    count_down(5)

    answers = question['incorrect_answers'][:] + [question['correct_answer']]
    random.shuffle(answers)
    
    for answer in answers:
        answer_button = ctk.CTkButton(
            app,
            text=answer,
            command=lambda ans=answer: answer_callback(ans, question)
        )
        answer_button.pack(pady=10)

def answer_selected(answer, question):
    check_answer(answer, question)
    next_question()
    
def count_down(time_left):
    global timer_label, counter_id, current_question_index
    if counter_id is not None:
        app.after_cancel(counter_id)

    if time_left >= 0:
        timer_label.configure(text=f"Timer: {time_left}")
        time_left -= 1
        counter_id = app.after(1000, count_down, time_left)
    else:
        times_up()
        
     
def answer_callback(selected_answer, question):
    global counter_id, player_points, current_question_index
    app.after_cancel(counter_id)  # Cancel the timer

    correct = selected_answer == question['correct_answer']
    
    if selected_answer == question['correct_answer']:
        player_points += 1  # Only increment points if the answer is correct.
        messagebox.showinfo("Correct!", "You have selected the correct answer.") 
        winsound.PlaySound(correct_sound_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
        
    else:
        messagebox.showinfo("Incorrect", f"The correct answer was: {question['correct_answer']}")
    next_question()

    
    if current_question_index < len(app.questions):
        show_question(app.questions[current_question_index])
    else:
        final_screen()
        current_question_index = 0  # Reset the index
        
    

def next_question():
    global current_question_index
    current_question_index +=1
    if current_question_index < len(app.questions):
        show_question(app.questions[current_question_index])
    else:
        final_screen()
    
def final_screen():
    clear_content()
    global player_points
    final_score = ctk.CTkLabel(app, text="Your Final Score: " + str(player_points), font=('Cursive', 15))
    final_score.pack(pady=20)

    play_again_btn = ctk.CTkButton(app, text='Play Again', command=start_game)
    play_again_btn.pack(padx=20)

    
def times_up():
    global current_question_index

    if current_question_index < len(app.questions):  # Check if there are still questions left
        answer = app.questions[current_question_index]['correct_answer']
        messagebox.showinfo("Time's Up!", f"No answer selected. The correct answer was: {answer}")
        current_question_index += 1 
        
        if current_question_index < len(app.questions):
            show_question(app.questions[current_question_index])  # Show next question
        else:
            end_quiz()  # End the quiz if there are no more questions
    else:
        end_quiz()  # If no more questions, end the quiz
        
def end_quiz():
    global current_question_index
    current_question_index = 0
    start_game()

     
    
background_label = ctk.CTkLabel(app, image=tk_bg_image)
background_label.place(relwidth=1, relheight=1)
background_label.image = tk_bg_image  # Keeping a reference

play_startup_sound()
start_game()  # This should lead to the difficulties page

app.mainloop()
