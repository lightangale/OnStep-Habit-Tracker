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
-- The below table is used for the mood tracker
CREATE TABLE mood (
    id INT AUTO_INCREMENT PRIMARY KEY,
    date VARCHAR(10) ,
    Mood_Rating INT,
    Feelings TEXT,
    Satisfaction_Reason TEXT,
    Activities TEXT,
    Interesting_Event TEXT,
    Self_Care TEXT
);

