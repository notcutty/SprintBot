#!/usr/bin/env python
# -*- coding: utf-8 -*-

from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

"""
Sets up the SQL tables that Sprintbot uses.
"""

Base = declarative_base()


class SprintServer(Base):
    """
    A table listing all servers of which SprintBot is a
    member. This is primarily for statistical purposes,
    as SprintBot primarily interacts with channels.

    Columns:
    id: The primary key for the row entry. Increments as
    new servers are added.

    server_id: The Discord snowflake ID for the server that
    SprintBot is on.
    """
    __tablename__ = 'sprintserver'
    id = Column(Integer, primary_key=True)
    server_id = Column(String(255), nullable=False)


class SprintChannel(Base):
    """
    SprintBot can individually start sprints in all channels
    that it has access to on all servers that it is a member
    of. This table keeps track of all channels SprintBot is
    called in.

    Columns:
    id: The primary key for the row  entry. Increments as
    new servers are added.

    channel_id: The Discord snowflake ID for the channel that
    SprintBot is on. SprintBot only tracks Discord text
    channels, group channels, and private channels.

    channel_type: Is "T" for text channels (channels on a server),
    "G" for group channels, and "P" for private channels.
    """
    __tablename__ = 'sprintchannel'
    id = Column(Integer, primary_key=True)
    channel_id = Column(String(255), nullable=False)
    channel_type = Column(String(1), nullable=False)


class Sprint(Base):
    __tablename__ = 'sprint'
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, nullable=False)
    is_started = Column(Boolean, nullable=False)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    halfway_point = Column(DateTime)
    sprintchannel_id = Column(String(255), ForeignKey('sprintchannel.id'))
    sprintchannel = relationship(SprintChannel)
    user_id = Column(String(255), nullable=False)


engine = create_engine('sqlite:///sprintbot.db')
Base.metadata.create_all(engine)
