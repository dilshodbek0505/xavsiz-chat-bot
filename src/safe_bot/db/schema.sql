CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT NOT NULL,
    last_name TEXT,
    language_code TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
