from flask import Flask, request, jsonify, render_template
import mysql.connector
from datetime import date
from flask import Flask, request, jsonify, render_template, Response
import mysql.connector
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import numpy as np
import io

app = Flask(__name__)

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

    # Fetch Habit Data# Fetch Habit Data
    mycursor.execute("SELECT * FROM habits")
    habit_result = mycursor.fetchall()

    habits_completed_today = {}
    total_habits = {}

    for i in habit_result:
        date_str = str(i[0])  # Assuming the first column is the date
        habits_completed_today[date_str] = i[1]  # Completed habits
        total_habits[date_str] = i[2]  # Total habits

    #Fetch Task Data
    mycursor.execute("SELECT * FROM tasks")
    task_result = mycursor.fetchall()

    tasks_completed_today = {}
    total_tasks = {}

    for i in task_result:
        date_str = str(i[0])  # Assuming the first column is the date
        tasks_completed_today[date_str] = i[1]  # Completed tasks
        total_tasks[date_str] = i[2]  # Total tasks

    #Get the last available date from both tables, or default to today
    last_habit_date = max(habits_completed_today.keys(), default=str(datetime.today().date()))
    last_task_date = max(tasks_completed_today.keys(), default=str(datetime.today().date()))
    last_date = max(last_habit_date, last_task_date)  # Latest date overall

    #Find the start of the week (Sunday before last_date)
    last_date_obj = datetime.strptime(last_date, "%Y-%m-%d")
    start_of_week = last_date_obj - timedelta(days=last_date_obj.weekday() + 1)  # Adjusting to Sunday

    #Generate all 7 days from Sunday to Saturday
    week_dates = [(start_of_week + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(7)]

    #Fill missing days with 0 values
    x_labels = week_dates
    y_total_habits = [total_habits.get(day, 0) for day in week_dates]
    y_habits_completed = [habits_completed_today.get(day, 0) for day in week_dates]
    y_total_tasks = [total_tasks.get(day, 0) for day in week_dates]
    y_tasks_completed = [tasks_completed_today.get(day, 0) for day in week_dates]

    #Plotting
    x_indexes = np.arange(len(x_labels))
    width = 0.2  # Width of bars

    plt.figure(figsize=(12, 6))

    plt.bar(x_indexes - 1.5*width, y_total_habits, width=width, label="Total Habits", color='blue')
    plt.bar(x_indexes - 0.5*width, y_habits_completed, width=width, label="Habits Completed", color='lightblue')

    plt.bar(x_indexes + 0.5*width, y_total_tasks, width=width, label="Total Tasks", color='green')
    plt.bar(x_indexes + 1.5*width, y_tasks_completed, width=width, label="Tasks Completed", color='lightgreen')

    #Labels and Title
    plt.xlabel("Date")
    plt.ylabel("Count")
    plt.title("Habit & Task Tracking Progress (Sunday to Saturday)")
    plt.xticks(ticks=x_indexes, labels=x_labels, rotation=45)
    plt.legend()
    max_y = max(y_total_habits + y_habits_completed + y_total_tasks + y_tasks_completed)  
    plt.yticks(np.arange(0, max_y + 1, 1)) 

    #Show Graph
    plt.tight_layout()

    # Save graph to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    plt.close()

    return Response(buf.getvalue(), mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)