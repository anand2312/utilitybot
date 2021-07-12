CREATE TABLE IF NOT EXISTS guilds (
    guild_id BIGINT PRIMARY KEY,
    prefix TEXT NOT NULL DEFAULT 'u!'
);

CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS guild_users (
    guild BIGINT REFERENCES guilds(guild_id),
    user_id BIGINT REFERENCES users(user_id)
);

/*
 * CREATE TYPE content_type AS ENUM ('anime', 'music');
 * The following enum does NOT exist on the database side to avoid having to alter
 * the type when we need to make new content types.
 * This validation should be done in the code itself.
*/

CREATE TABLE IF NOT EXISTS user_content (
    user_id BIGINT NOT NULL REFERENCES users(user_id),
    content_name TEXT NOT NULL,  -- run an UPDATE ... ON CONFLICT DO INSERT here to avoid duplication
    content_type TEXT NOT NULL,
    content_url TEXT,
    recommended_by BIGINT REFERENCES users(user_id)
);

CREATE INDEX id_content ON user_content(user_id);

CREATE INDEX content_name_index ON user_content (LOWER(content_name));  -- this allows efficient case insensitive searches
