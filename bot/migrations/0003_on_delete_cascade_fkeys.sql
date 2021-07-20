/* alter the foreign keys of the tables to have on delete cascade */

ALTER TABLE guild_users
    DROP CONSTRAINT guild_users_guild_fkey,
    ADD CONSTRAINT guild_users_guild_fkey
        FOREIGN KEY(guild)
        REFERENCES guilds(guild_id)
        ON DELETE CASCADE;

ALTER TABLE guild_users
    DROP CONSTRAINT guild_users_user_id_fkey,
    ADD CONSTRAINT guild_users_user_id_fkey
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE;

ALTER TABLE user_content
    DROP CONSTRAINT user_content_user_id_fkey,
    ADD CONSTRAINT user_content_user_id_fkey
        FOREIGN KEY(user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE;
