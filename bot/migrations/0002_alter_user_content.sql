/* alter the user_content table to have an ID field as well. */

ALTER TABLE user_content ADD COLUMN id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY;
