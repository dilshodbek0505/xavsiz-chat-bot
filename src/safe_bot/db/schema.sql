CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    is_bot INTEGER NOT NULL DEFAULT 0,
    first_name TEXT NOT NULL,
    last_name TEXT,
    username TEXT,
    language_code TEXT,
    is_premium INTEGER,
    added_to_attachment_menu INTEGER,
    raw_json TEXT NOT NULL DEFAULT '{}',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS business_connections (
    id TEXT PRIMARY KEY,
    user_id INTEGER NOT NULL,
    user_chat_id INTEGER NOT NULL,
    is_enabled INTEGER NOT NULL,
    can_delete_all_messages INTEGER NOT NULL DEFAULT 0,
    can_delete_sent_messages INTEGER NOT NULL DEFAULT 0,
    updated_at TEXT NOT NULL
);
