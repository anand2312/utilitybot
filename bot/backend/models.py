"""
Module to handle general database interactions models.
"""

from dataclasses import dataclass
from typing import List, Optional

import asyncpg
from loguru import logger

from bot.utils.constants import ContentType


@dataclass
class ContentRecord:
    """
    Represents a content record on the database.
    """

    user_id: int  # the bare minimum fields needed for an operation (delete)
    name: str
    type: ContentType = (
        ContentType.Anime
    )  # this default is a lazy way to quiet pylance down
    recommended_by: Optional[int] = None
    id: Optional[int] = None  # this field exists only when retrieved from the db.
    url: Optional[str] = None

    @classmethod
    async def by_name(
        cls, conn: asyncpg.Connection, *, name: str, user: int
    ) -> Optional["ContentRecord"]:
        """
        Fetches an existing Content record for a specific user.
        NOTE: query is run with '%name%'
        """
        logger.debug(f"Retrieving content with name {name} for user {user}")
        r = await conn.fetchrow(
            "SELECT * FROM user_content WHERE LOWER(content_name) LIKE $1 AND user_id = $2",
            f"%{name.lower()}%",
            user,
        )

        if not r:
            logger.info(f"Content with name {name} did not exist")
            return None

        return cls._parse_db_output(r)

    @classmethod
    async def by_id(
        cls, conn: asyncpg.Connection, *, id: int
    ) -> Optional["ContentRecord"]:
        """
        Fetches a content record by its ID.
        """
        logger.debug(f"Retrieving content with ID {id}")
        r = await conn.fetchrow("SELECT * FROM user_content WHERE id = $1", id)

        if not r:
            logger.info(f"Content with ID {id} did not exist")
            return None

        return cls._parse_db_output(r)

    @classmethod
    def _parse_db_output(cls, r: asyncpg.Record) -> "ContentRecord":
        return cls(
            user_id=r["user_id"],
            name=r["content_name"],
            type=ContentType(r["content_type"]),
            recommended_by=r["recommended_by"],
            url=r["content_url"],
            id=r["id"],
        )

    async def save(self, conn: asyncpg.Connection) -> Optional["ContentRecord"]:
        """
        Saves a new Content record to the database.
        """
        existing = await self.__class__.by_name(conn, name=self.name, user=self.user_id)

        if not existing:
            logger.info(
                f"Creating new content record for user {self.user_id} with name {self.name}"
            )
            await conn.execute(
                (
                    "INSERT INTO user_content"
                    "(user_id, content_name, content_type, recommended_by, content_url)"
                    "VALUES ($1, $2, $3, $4, $5)"
                ),
                self.user_id,
                self.name,
                self.type.value,
                self.recommended_by,
                self.url,
            )
            return self
        else:
            logger.info(
                f"Content record with name {self.name} for user {self.user_id} already exists"
            )
            return self

    async def delete(self, conn: asyncpg.Connection) -> str:
        """
        Deletes a content record from the database.
        """
        logger.info(f"Deleting content with name {self.name} for user {self.id}")
        return await conn.execute(
            "DELETE FROM user_content WHERE user_id = $1 AND LOWER(content_name) = $2",
            self.user_id,
            self.name,
        )  # lowercase names must match


@dataclass
class User:
    """
    Represents a user.
    """

    id: int

    async def get_content_list(
        self, conn: asyncpg.Connection, *, content_type: ContentType
    ) -> List[ContentRecord]:
        """
        Gets the user's recommended 'list' for a specific content type.
        """
        logger.info(f"Fetching {content_type.value} list for user {self.id}")
        data = await conn.fetch(
            "SELECT * FROM user_content WHERE user_id = $1 AND content_type = $2",
            self.id,
            content_type.value,
        )
        return [ContentRecord._parse_db_output(record) for record in data]

    async def add_to_list(
        self, conn: asyncpg.Connection, *, record: ContentRecord
    ) -> Optional[ContentRecord]:
        """
        Adds a content record to the user's list.

        Returns:
            The saved content record object
        """
        logger.info(f"Adding {record.name} to {self.id}'s {record.type.value} list.")
        return await record.save(conn)

    async def remove_from_list(self, conn: asyncpg.Connection, *, name: str) -> None:
        """
        Removes a specific item by it's name from the user's 'list'.
        """
        logger.info(f"Deleting content with name {name} for user {self.id}")
        await ContentRecord(user_id=self.id, name=name).delete(conn)


@dataclass
class Guild:
    """
    Represents a guild.
    """

    id: int
    prefix: Optional[str] = "u!"

    async def get_prefix(self, conn: asyncpg.Connection) -> Optional[str]:
        return await conn.fetchval(
            "SELECT prefix FROM guilds WHERE guild_id = $1", self.id
        )

    async def set_prefix(self, conn: asyncpg.Connection, *, prefix: str) -> str:
        """
        Sets the guild's prefix.

        Args:
            conn: a database connection object
        Returns:
            The new prefix
        """
        logger.info(f"Setting prefix for guild {self.id} to {prefix}")
        await conn.execute(
            "UPDATE guilds SET prefix = $1 WHERE id = $2", prefix, self.id
        )
        self.prefix = prefix
        return prefix

    async def save(self, conn: asyncpg.Connection) -> Optional[str]:
        """Save a guild to the database."""
        logger.info(f"Saving guild {self.id} to the database")
        return await conn.execute("INSERT INTO guilds VALUES ($1)", self.id)

    async def bulk_save_members(
        self, conn: asyncpg.Connection, *, members: List[int]
    ) -> Optional[str]:
        """Save the guilds members to the database."""
        logger.info(f"Saving guild {self.id} members to global users table")
        await conn.executemany(
            "INSERT INTO users VALUES ($1) ON CONFLICT DO NOTHING",
            [(m,) for m in members],
        )
        logger.info(f"Saving guild {self.id} members to guild-users table")
        await conn.executemany(
            "INSERT INTO guild_users VALUES($1, $2)",
            [(self.id, member) for member in members],
        )
        logger.info(f"Completed inserting guild {self.id} members to database!")

    async def delete(self, conn: asyncpg.Connection) -> Optional[str]:
        return await conn.execute("DELETE FROM guilds WHERE guild_id = $1", self.id)
