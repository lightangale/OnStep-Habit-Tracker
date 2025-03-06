-- The below tables will be used for making the graph
CREATE TABLE habits (
    date VARCHAR(10) PRIMARY KEY,
    habits_completed_today INT DEFAULT 0,
    total_habits INT DEFAULT 0
);

CREATE TABLE tasks (
    date VARCHAR(10) PRIMARY KEY,
    tasks_completed_today INT DEFAULT 0,
    total_tasks INT DEFAULT 0
);

INSERT INTO habits (date, habits_completed_today, total_habits) 
VALUES ('2025-03-05', 6, 6);

INSERT INTO tasks (date, tasks_completed_today, total_tasks) 
VALUES ('2025-03-05', 5, 10);

SELECT * FROM habits;
SELECT * FROM tasks;

-- The below tables will be used for training the model

CREATE TABLE habit_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    habit_name VARCHAR(255),
    completed BOOLEAN DEFAULT 0,
    time_completed TIME,
    day_completed VARCHAR(10)
);

CREATE TABLE task_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_name VARCHAR(255),
    completed BOOLEAN DEFAULT 0,
    time_completed TIME,
    day_completed VARCHAR(10)
);

