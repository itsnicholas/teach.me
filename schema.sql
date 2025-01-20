CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE,
    password_hash TEXT,
    admin BOOLEAN
);

CREATE TABLE userscourses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users,
    course_id INTEGER REFERENCES courses
);

CREATE TABLE materials (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses,
    text TEXT,
    visible BOOLEAN 
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    name TEXT UNIQUE,
    visible BOOLEAN
);

CREATE TABLE usersquestions (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses,
    user_id INTEGER REFERENCES users,
    type INTEGER,
    question_id INTEGER
);

CREATE TABLE textquestions (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses,
    question TEXT UNIQUE,
    answer TEXT,
    visible BOOLEAN
);

CREATE TABLE multiplechoicequestions (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses,
    answer TEXT,
    question TEXT UNIQUE,
    visible BOOLEAN   
);

CREATE TABLE multiplechoiceoptions (
    id INTEGER PRIMARY KEY,
    multiplechoicequestion_id INTEGER REFERENCES multiplechoicequestions,
    option TEXT
);