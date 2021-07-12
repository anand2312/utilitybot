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
    Abstract base class representing the methods that each content type should allow.
    """

    user_id: int
    name: str
    type: ContentType
    recommended_by: int
    id: Optional[int] = None  # this field exists only when retrieved from the db.
    url: Optional[str] = None

    @classmethod
    async def by_name(
        cls, conn: asyncpg.Connection, *, name: str
    ) -> Optional["ContentRecord"]:
        """
        Fetches an existing Content record for a specific user.
        NOTE: query is run with '%name%'
        """
        logger.debug(f"Retrieving content with name {name}")
        r = await conn.fetchrow(
            "SELECT * FROM user_content WHERE name LIKE $1", f"%{name.lower()}%"
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
        r = await conn.fetchrow("SELECT * FROM user_content WHERE name = $1", id)

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
            url=r["url"],
            id=r["id"],
        )

    async def save(self, conn: asyncpg.Connection) -> Optional["ContentRecord"]:
        """
        Saves a new Content record to the database.
        """
        existing = await self.__class__.by_name(conn, name=self.name)

        if not existing:
            logger.info(
                f"Creating new content record for user {self.user_id} with name {self.name}"
            )
            await conn.execute(
                "INSERT INTO user_content VALUES($1, $2, $3, $4, $5)",
                self.user_id,
                self.name,
                self.type.value,
                self.recommended_by,
                self.url,
            )
            return self

    async def delete(self, conn: asyncpg.Connection) -> str:
        """
        Deletes a content record from the database.
        """
        return await conn.execute("DELETE FROM user_content WHERE id = $1", self.id)


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


@dataclass
class Guild:
    """
    Represents a guild.
    """

    id: int
    prefix: str

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
