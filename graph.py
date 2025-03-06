import numpy as np
import matplotlib.pyplot as plt
import mysql.connector
from datetime import datetime, timedelta

#Connect to MySQL
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Mysql@3306",
    database="shruti"
)

mycursor = mydb.cursor()

# Fetch Habit Data
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
plt.show()
