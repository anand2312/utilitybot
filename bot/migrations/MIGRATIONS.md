# Migrations

You can set the database up yourself; but set the `DB_URI` env var in your .env file.
Example db uri:
```
DB_URI=postgresql://user:password@localhost:5432/database
```

We aren't using an ORM as such, meaning migrations are kind of a pain.
To maintain consistence easily, I will be writing migration queries in files and committing them. Copying and pasting them all in order into psql should get you to the most up to date state of the database.
