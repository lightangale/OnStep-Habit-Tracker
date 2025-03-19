from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import date
from flask import Flask, request, jsonify, render_template, Response
import mysql.connector
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  #to solve the tkinter issue
import numpy as np
import io
from flask_cors import CORS 
import imblearn


app = Flask(__name__)
CORS(app) 
# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Mysql@3306",
        database="shruti"
    )

# Home route (default to index.html)
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/index.html')
def index():
    return render_template('index.html')

# Route for habit.html
@app.route('/habit.html')
def habit():
    return render_template('habit.html')

# Route for features.html
@app.route('/features.html')
def features():
    return render_template('features.html')

# Route for daily.html
@app.route('/daily.html')
def daily():
    return render_template('daily.html')

# Route for progress.html
@app.route('/progress.html')
def progress():
    return render_template('progress.html')

# Route for todo.html
@app.route('/todo.html')
def todo():
    return render_template('todo.html')

# Route for timer.html
@app.route('/timer.html')
def timer():
    return render_template('timer.html')

# Route for notes.html
@app.route('/notes.html')
def notes():
    return render_template('notes.html')

# Route for mood.html
@app.route('/mood.html')
def mood():
    return render_template('mood.html')

# Route for profile.html
@app.route('/profile.html')
def profile():
    return render_template('profile.html')

# Route for updating progress
@app.route("/update_progress", methods=["POST"])
def update_progress():
    data = request.get_json()

    # Extracting variables from received JSON 
    completed_habits = data.get("completed_habits", 0)
    total_habits = data.get("total_habits", 0)
    completed_tasks = data.get("completed_tasks", 0)
    total_tasks = data.get("total_tasks", 0)
    
    today = date.today().strftime("%Y-%m-%d")  # Get today's date as "YYYY-MM-DD"

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert or update habits table
    cursor.execute("""
        INSERT INTO habits (date, habits_completed_today, total_habits)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        habits_completed_today = VALUES(habits_completed_today),
        total_habits = VALUES(total_habits);
    """, (today, completed_habits, total_habits))

    # Insert or update tasks table
    cursor.execute("""
        INSERT INTO tasks (date, tasks_completed_today, total_tasks)
        VALUES (%s, %s, %s)
        ON DUPLICATE KEY UPDATE
        tasks_completed_today = VALUES(tasks_completed_today),
        total_tasks = VALUES(total_tasks);
    """, (today, completed_tasks, total_tasks))

    conn.commit()
    cursor.close()
    conn.close()
    print("Received data from frontend:")
    print(f"Completed Habits: {completed_habits}")
    print(f"Total Habits: {total_habits}")
    print(f"Completed Tasks: {completed_tasks}")
    print(f"Total Tasks: {total_tasks}")
    print(f"Date : {today}")

    return jsonify({
        "message": "Data successfully updated!",
        "completed_habits": completed_habits,
        "total_habits": total_habits,
        "completed_tasks": completed_tasks,
        "total_tasks": total_tasks
    })


########################################################################## GRAPH #######################################################


# Route for generating the graph
@app.route('/plot.png')
def plot_png():
    conn = get_db_connection()
    mycursor = conn.cursor()

    # Fetch Habit Data
    mycursor.execute("SELECT * FROM habits")
    habit_result = mycursor.fetchall()

    habits_completed_today = {}
    total_habits = {}

    for i in habit_result:
        date_str = str(i[0])  # Assuming the first column is the date
        habits_completed_today[date_str] = i[1]  # Completed habits
        total_habits[date_str] = i[2]  # Total habits

    # Fetch Task Data
    mycursor.execute("SELECT * FROM tasks")
    task_result = mycursor.fetchall()

    tasks_completed_today = {}
    total_tasks = {}

    for i in task_result:
        date_str = str(i[0])  # Assuming the first column is the date
        tasks_completed_today[date_str] = i[1]  # Completed tasks
        total_tasks[date_str] = i[2]  # Total tasks

    # Get the latest recorded date or default to today
    last_habit_date = max(habits_completed_today.keys(), default=str(datetime.today().date()))
    last_task_date = max(tasks_completed_today.keys(), default=str(datetime.today().date()))
    last_date = max(last_habit_date, last_task_date, str(datetime.today().date()))  # Ensure today is included

    # Generate last 6 days + today to ensure exactly 7 values
    last_date_obj = datetime.strptime(last_date, "%Y-%m-%d")
    week_dates = [(last_date_obj - timedelta(days=i)).strftime("%Y-%m-%d") for i in range(6, -1, -1)]

    # Fill missing days with 0 values
    x_labels = week_dates
    y_total_habits = [total_habits.get(day, 0) for day in week_dates]
    y_habits_completed = [habits_completed_today.get(day, 0) for day in week_dates]
    y_total_tasks = [total_tasks.get(day, 0) for day in week_dates]
    y_tasks_completed = [tasks_completed_today.get(day, 0) for day in week_dates]

    # Plotting
    x_indexes = np.arange(len(x_labels))
    width = 0.2  # Width of bars

    plt.figure(figsize=(12, 6))

    plt.bar(x_indexes - 1.5*width, y_total_habits, width=width, label="Total Habits", color='blue')
    plt.bar(x_indexes - 0.5*width, y_habits_completed, width=width, label="Habits Completed", color='lightblue')

    plt.bar(x_indexes + 0.5*width, y_total_tasks, width=width, label="Total Tasks", color='green')
    plt.bar(x_indexes + 1.5*width, y_tasks_completed, width=width, label="Tasks Completed", color='lightgreen')

    # Labels and Title
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.title("Habit & Task Tracking Progress (Last 7 Days)")
    plt.xticks(ticks=x_indexes, labels=x_labels, rotation=45)
    plt.legend()
    max_y = max(y_total_habits + y_habits_completed + y_total_tasks + y_tasks_completed)  
    plt.yticks(np.arange(0, max_y + 1, 1)) 

    # Show Graph
    plt.tight_layout()

    # Save graph to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return Response(buf.getvalue(), mimetype='image/png')

############################################################# MOOD ###########################################################################

@app.route('/mood_tracker', methods=["POST"])
def mood_tracker():
    data = request.get_json()

    
    mood = data.get("mood")
    activities = data.get("activities")
    satisfaction = data.get("satisfaction")
    interest = data.get("interest")
    feelings = data.get("feelings")
    selfCare = data.get("selfCare")
    today = date.today().strftime("%d-%m-%Y")  

    conn = get_db_connection()
    cursor = conn.cursor()

   
    cursor.execute(
        "INSERT INTO mood (date, Mood_Rating, Feelings, Satisfaction_Reason, Activities, Interesting_Event, Self_Care) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (today, mood, feelings, satisfaction, activities, interest, selfCare)
    )

    conn.commit()
    cursor.close()
    conn.close()
    print(today, mood, feelings, satisfaction, activities, interest, selfCare)
    return jsonify({"message": "Mood data recorded successfully"})  

############################################################### PROFILE ########################################################3

import google.generativeai as genai
import os


GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')


def summarize_with_gemini(input_text):
    try:
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")
        genai.configure(api_key=GOOGLE_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        
        prompt = (
            "mention the given date correctly, its DD-MM-YYYY format"
            "If no input found, say 'the day has no data, and no rating' in a creative and funny way. (refer to missing data as 'this day' or variants strictly)"
            "Turn this information into a summary for a user "
            "Use only plain texts, no bold or italics only plain texts with emojis and emoticons like ':D', ':(' etc  if suitable"
            "A lone number after the date is the rating out of 10, include that as well! "
            "If the rating is less than 4 make it sound encouraging, otherwise make it happy.\n\n"
            
            f"{input_text}"
        )

        response = model.generate_content(prompt)
        print(response.text)
        return response.text

    except Exception as e:
        print(f"Error during Gemini API call: {e}")
        return None

@app.route("/gemini", methods=["GET"])
def gemini_summary():


    date = request.args.get("date")  
    print(date)
    if not date:
        return jsonify({"error": "Date parameter is required"}), 400

    # Fetch all mood data for the given date from the database
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM mood WHERE date = %s", (date,))
    mood_data_list = cursor.fetchall()  # Fetch all records for the date

    cursor.close()
    conn.close()

    if not mood_data_list:
        input_text=""

    # Combine data for the same date
    combined_data = {
        "date": date,
        "Mood_Ratings": [],
        "Feelings": [],
        "Satisfaction_Reasons": [],
        "Activities": [],
        "Interesting_Events": [],
        "Self_Care": []
    }

    for mood_data in mood_data_list:
        combined_data["Mood_Ratings"].append(mood_data["Mood_Rating"])
        combined_data["Feelings"].append(mood_data["Feelings"])
        combined_data["Satisfaction_Reasons"].append(mood_data["Satisfaction_Reason"])
        combined_data["Activities"].append(mood_data["Activities"])
        combined_data["Interesting_Events"].append(mood_data["Interesting_Event"])
        combined_data["Self_Care"].append(mood_data["Self_Care"])

    # Convert lists to strings for Gemini input
    input_text = (
        f"Date: {combined_data['date']}\n"
        f"Mood Ratings: {', '.join(map(str, combined_data['Mood_Ratings']))}\n"
        f"Feelings: {', '.join(combined_data['Feelings'])}\n"
        f"Satisfaction Reasons: {', '.join(combined_data['Satisfaction_Reasons'])}\n"
        f"Activities: {', '.join(combined_data['Activities'])}\n"
        f"Interesting Events: {', '.join(combined_data['Interesting_Events'])}\n"
        f"Self Care: {', '.join(combined_data['Self_Care'])}"
    )

    # Generate summary using Gemini
    summary = summarize_with_gemini(input_text)

    if summary:
        return jsonify({"summary": summary})
    else:
        return jsonify({"error": "Failed to generate summary"}), 500
    

if __name__ == "__main__":
    app.run(debug=True)
