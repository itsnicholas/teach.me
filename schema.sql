CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    admin BOOLEAN NOT NULL
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    name TEXT,
    visible BOOLEAN
);

CREATE TABLE userscourses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users NOT NULL,
    course_id INTEGER REFERENCES courses NOT NULL
);

CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    material TEXT,
    visible BOOLEAN
);

CREATE TABLE usersquestions (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    user_id INTEGER REFERENCES users NOT NULL,
    type INTEGER NOT NULL,
    question_id INTEGER NOT NULL
);

CREATE TABLE textquestions (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    question TEXT,
    answer TEXT,
    visible BOOLEAN
);

CREATE TABLE multiplechoicequestions (
    id SERIAL PRIMARY KEY,
    course_id INTEGER REFERENCES courses NOT NULL,
    answer TEXT,
    question TEXT,
    visible BOOLEAN
);

CREATE TABLE multiplechoiceoptions (
    id SERIAL PRIMARY KEY,
    multiplechoicequestion_id INTEGER REFERENCES multiplechoicequestions NOT NULL,
    option TEXT
);