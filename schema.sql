CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    admin BOOLEAN NOT NULL
);

CREATE TABLE userscourses (
    id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users NOT NULL,
    course_id INTEGER REFERENCES courses NOT NULL
);

CREATE TABLE materials (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    text TEXT,
    visible BOOLEAN
);

CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    name TEXT,
    visible BOOLEAN
);

CREATE TABLE usersquestions (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    user_id INTEGER REFERENCES users NOT NULL,
    type INTEGER NOT NULL,
    question_id INTEGER NOT NULL
);

CREATE TABLE textquestions (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    question TEXT,
    answer TEXT,
    visible BOOLEAN
);

CREATE TABLE multiplechoicequestions (
    id INTEGER PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    answer TEXT,
    question TEXT,
    visible BOOLEAN
);

CREATE TABLE multiplechoiceoptions (
    id INTEGER PRIMARY KEY,
    multiplechoicequestion_id INTEGER REFERENCES multiplechoicequestions NOT NULL,
    option TEXT
);