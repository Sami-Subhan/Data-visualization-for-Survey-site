import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import json
import numpy as np

# Load questions and country data from JSON files
with open('questionsFormat.json', 'r') as f:
    themes_data = json.load(f)

with open('final_country.json', 'r') as f:
    country_data = json.load(f)

# Function to clear the screen and display questions for the selected theme
def show_questions(theme):
    # Clear all frames
    for widget in theme_frame.winfo_children():
        widget.destroy()
    for widget in answer_frame.winfo_children():
        widget.destroy()
    for widget in graph_frame.winfo_children():
        widget.destroy()

    # Add label for selecting a question
    question_label = tk.Label(theme_frame, text="Select a question", font=("Helvetica", 16))
    question_label.pack(pady=10)
    
    # Display questions at the top
    theme_questions = themes_data['questions'][theme]
    for question in theme_questions:
        question_id = list(question.keys())[0]  # Extract question ID
        question_button = tk.Button(theme_frame, text=question_id, command=lambda q=question: show_question_value(q))
        question_button.pack(side=tk.LEFT,pady=5)
    
    # Add a back button to return to the theme selection
    back_button = tk.Button(theme_frame, text="Back to Themes", command=reset_view)
    back_button.pack(pady=5)

# Function to display the question value for the selected question ID
def show_question_value(question):
    # Extract question value from the question dictionary
    question_value = list(question.values())[0]

    # Clear the answer frame before showing the question value
    for widget in question_frame.winfo_children():
        widget.destroy()

    # Display the question value
    question_value_label = tk.Label(question_frame, text=f"Question: {question_value}", font=("Helvetica", 16))
    question_value_label.pack(pady=10)

    # Call show_answers to display the answers based on the question ID
    question_id = list(question.keys())[0]  # Extract question ID
    show_answers(question_id)

# Function to plot the data for the selected answers or subanswers as a stacked bar graph
def plot_data(answer_data, is_sub=False,sub_only=False, all_subanswers=None):
    global canvas  # To clear previous plot
    countries = ["KSA", "UAE", "Qatar", "Egypt", "Morocco", "Jordan", "Lebanon", "Tunisia", "Algeria", "Other"]

    # Clear the previous graph if it exists
    for widget in graph_frame.winfo_children():
        widget.destroy()

    # If we are plotting subanswers, plot them as a single stacked bar graph
    if is_sub and all_subanswers:
        fig, ax = plt.subplots(figsize=(8, 6))

        # Prepare the data for stacking
        values = np.zeros(len(countries))

        # Colors for each subanswer
        colors = plt.cm.get_cmap('tab10', len(all_subanswers))
        
        # Plot each subanswer as a segment in the stacked bar
        for i, subanswer in enumerate(all_subanswers):
            sub_values = [int(subanswer[country].replace('%', '')) for country in countries]
            values += np.array(sub_values)  # Update the cumulative values
            ax.barh(countries, sub_values, color=colors(i), edgecolor='white', label=subanswer['subAnswer'], left=values - np.array(sub_values))

        ax.set_xlabel('Percentage (%)')
        if(sub_only==False):
          ax.set_title(f"Survey Data for All Subanswers of {answer_data['answer']}")
        ax.set_xlim(0, 100)

        # Add a legend to indicate subanswer colors
        legend=ax.legend(title="SubAnswers", bbox_to_anchor=(1.05, 1), loc='center')
        legend.set_draggable(True)

        
    else:
        # If no subanswers, plot the data as before
        values = [int(answer_data[country].replace('%', '')) for country in countries]
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.barh(countries, values, color='skyblue')
        ax.set_xlabel('Percentage (%)')
        ax.set_title(f"Survey Data for {answer_data['answer']}")
        ax.set_xlim(0, 100)

    # Embed the plot in Tkinter
    canvas = FigureCanvasTkAgg(fig, master=graph_frame)
    canvas.draw()
    canvas.get_tk_widget().pack()

# Function to display the answers for the selected question
def show_answers(question_id):
    question_data = country_data[question_id]
    
    # Clear previous answer buttons
    for widget in answer_frame.winfo_children():
        widget.destroy()

    # Add label for displaying answers
    answer_label = tk.Label(answer_frame, text="Answers", font=("Helvetica", 16))
    answer_label.pack(pady=10)
    
    # Get availability flags
    answers_available = question_data.get("answersAvailable", "No")
    gradient_available = question_data.get("gradientAvailable", "No")

    if answers_available == "Yes":
        if gradient_available == "No":
            # Only show answers, no subanswers
            for answer in question_data['data']:
                answer_button = tk.Button(answer_frame, text=answer['answer'], command=lambda a=answer: plot_data(a,False,False))
                answer_button.pack(pady=5)

        elif gradient_available == "Yes":
            for answer in question_data['data']:
                answer_text = answer['answer']
                
                # Create a button for the answer
                answer_button = tk.Button(answer_frame, text=answer_text, command=lambda ans=answer: show_subanswers(ans))
                answer_button.pack(pady=5, anchor='w')

    elif answers_available == "No" and gradient_available == "Yes":
        for widget in answer_frame.winfo_children():
            widget.destroy()
        all_subanswers = question_data['data']  # Access all subanswers based on answer text
        plot_data(question_data['data'][0], True,True, all_subanswers)  # Use first answer for plotting

    # Update scroll region for the answer canvas
    answer_canvas.configure(scrollregion=answer_canvas.bbox("all"))
        
# Function to display subanswers for the selected answer
def show_subanswers(answer):
    
     # Display subanswers as buttons
    all_subanswers = answer[answer['answer']]  # Access all subanswers based on answer text

    # Plot all subanswers in a single graph
    plot_data(answer, True, False,all_subanswers)

    # Update scroll region for the answer canvas
    answer_canvas.configure(scrollregion=answer_canvas.bbox("all"))

# Function to reset the view to show theme selection
def reset_view():
    # Clear all frames
    for widget in theme_frame.winfo_children():
        widget.destroy()
    for widget in question_frame.winfo_children():
        widget.destroy()    
    for widget in answer_frame.winfo_children():
        widget.destroy()
    for widget in graph_frame.winfo_children():
        widget.destroy()
    
    # Redisplay themes
    display_themes()

# Function to display themes
def display_themes():
    # Add label for selecting a theme
    theme_label = tk.Label(theme_frame, text="Select a theme", font=("Helvetica", 16))
    theme_label.pack(pady=10)
    
    for theme in themes_data['questions']:
        theme_button = tk.Button(theme_frame, text=theme, command=lambda t=theme: show_questions(t))
        theme_button.pack(pady=5)

# Function to handle window closing
def on_closing():
    window.quit()  # Exit the Tkinter main loop
    window.destroy()  # Destroy the window

# Main window setup
window = tk.Tk()
window.title("Survey Data")
window.geometry("800x600")

# Create frames
theme_frame = tk.Frame(window)
theme_frame.pack(side=tk.TOP, pady=10)
# Create frames
question_frame = tk.Frame(window)
question_frame.pack(side=tk.TOP, pady=10)

# Create a canvas and scrollbar for the answer frame
answer_canvas = tk.Canvas(window)
answer_scrollbar = ttk.Scrollbar(window, orient="vertical", command=answer_canvas.yview)
answer_frame = tk.Frame(answer_canvas)

answer_frame.bind("<Configure>", lambda e: answer_canvas.configure(scrollregion=answer_canvas.bbox("all")))
answer_canvas.create_window((0, 0), window=answer_frame, anchor="nw")

answer_canvas.configure(yscrollcommand=answer_scrollbar.set)

# Pack the canvas and scrollbar
answer_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
answer_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Create a graph frame
graph_frame = tk.Frame(window)
graph_frame.pack(side=tk.RIGHT, padx=20, pady=20, expand=True)

# Add "Q" button to quit the application
quit_button = tk.Button(window, text="Q: Quit", command=on_closing)
quit_button.pack(side=tk.BOTTOM, pady=10)

# Handle window closing event
window.protocol("WM_DELETE_WINDOW", on_closing)

# Display themes at the start
display_themes()

# Start the GUI loop
window.mainloop()
