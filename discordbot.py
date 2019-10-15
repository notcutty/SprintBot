#!/usr/bin/env python
# -*- coding: utf-8 -*-
import asyncio
import discord
import random
import re
import secrets
from datetime import datetime, timedelta
from sqlalchemy import create_engine, literal
from sqlalchemy.orm import sessionmaker
from declare_tables import Base, Sprint, SprintChannel, SprintServer

# Command regex
sprint_one_arg = r'sprint\s+(.{1,3})'
sprint_two_args = r'sprint\s+(.{1,3})\s+(.{1,3})'

# Help file for SprintBot
with open('help.txt', 'r') as help_file:
    help_text = "".join(help_file.readlines())

client = discord.Client()
engine = create_engine('sqlite:///sprintbot.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


def set_start_time(minute):
    start_time = datetime.utcnow()
    # Add one minute to this value until we're at the specified minute
    while(start_time.minute != minute):
        start_time = start_time + timedelta(seconds=60)
    while(start_time.second != 0):
        start_time = start_time - timedelta(seconds=1)
    while(start_time.microsecond != 0):
        start_time = start_time - timedelta(microseconds=1)
    return start_time


def set_end_time(start_time, length):
    return start_time + timedelta(seconds=(60 * length))


def at_halfway_point(dt1, dt2):
    return (dt1.hour == dt2.hour and
            dt1.minute == dt2.minute and
            dt1.second == dt2.second)


def set_halfway_point(start_time, end_time):
    rough_point = start_time + (end_time - start_time) / 2
    while(rough_point.second != 0 and rough_point.second != 30):
        rough_point = rough_point + timedelta(seconds=1)
    while(rough_point.microsecond != 0):
        rough_point = rough_point - timedelta(microseconds=1)
    return rough_point


def get_sprint_channel(message):
    query = session.query(SprintChannel).filter(
        SprintChannel.channel_id == message.channel.id).all()
    if not query:
        if message.channel.type is discord.ChannelType.private:
            type_string = 'p'
        elif message.channel.type is discord.ChannelType.group:
            type_string = 'g'
        elif message.channel.type is discord.ChannelType.text:
            type_string = 't'
        else:
            return
        channel = SprintChannel(channel_id=message.channel.id,
                                channel_type=type_string)
        session.add(channel)
        session.commit()
    else:
        channel = query[0]
    return channel


def messager_is_mod(message):
    if message.channel.type is discord.ChannelType.private:
        return True
    user = message.author
    permissions = user.permissions_in(message.channel)
    return (permissions.kick_members or permissions.ban_members or
            permissions.administrator or permissions.manage_channels or
            permissions.manage_guild or permissions.view_audit_log or
            permissions.manage_messages or permissions.mute_members or
            permissions.deafen_members or permissions.move_members or
            permissions.manage_roles)


async def active_sprint_already_exists(channel, message):
    query = session.query(Sprint).filter(
        Sprint.is_active == literal(True)).filter(
            Sprint.sprintchannel == channel).all()
    if query:
        sprint = query[0]
        if sprint.is_started:
            await message.channel.send(
                "There's already an ongoing sprint in this channel.")
        else:
            await message.channel.send(
                "There's already a scheduled sprint in this channel.")
        return True
    else:
        return False


async def create_new_sprint(start_time, length, channel, message):
    start_time = set_start_time(start_time)
    end_time = set_end_time(start_time, length)
    halfway = set_halfway_point(start_time, end_time)
    new_sprint = Sprint(is_active=True, start_time=start_time,
                        end_time=end_time, sprintchannel=channel,
                        user_id=message.author.id, is_started=False,
                        halfway_point=halfway)
    session.add(new_sprint)
    session.commit()
    remaining = round((start_time - datetime.utcnow()).seconds / 60)
    if remaining < 1:
        remaining = (start_time - datetime.utcnow()).seconds
        if remaining > 1 or remaining == 0:
            start_word = 'seconds'
        else:
            start_word = 'second'
    else:
        if remaining > 1 or remaining == 0:
            start_word = 'minutes'
        else:
            start_word = 'minute'
    if length > 1 or length == 0:
        length_word = 'minutes'
    else:
        length_word = 'minute'
    await message.channel.send("Scheduled a new sprint! It will start " +
                               f"in {remaining} {start_word} and last for " +
                               f"{length} {length_word}.")


async def cycle_avatar(last_avatar):
    """
    A silly little function that cycles SprintBot avatar between various
    running emojis. Changes once every 15 minutes.
    """
    # Select a random avatar from the avatars folder
    selected_avatar = last_avatar
    while selected_avatar == last_avatar:
        selected_avatar = random.randint(1, 12)
    file_name = f"avatars/{selected_avatar}.png"
    with open(file_name, 'rb') as random_avatar:
        # Set the avatar
        await client.user.edit(avatar=random_avatar.read())
    return selected_avatar


async def stopwatch():
    await client.wait_until_ready()
    last_avatar = 0
    while not client.is_closed():
        time_now = datetime.utcnow()
        query = session.query(Sprint).filter(
            Sprint.is_active == literal(True)).all()
        if time_now.minute % 15 == 0 and time_now.second == 0:
            # Change the avatar every 15 minutes
            last_avatar = await cycle_avatar(last_avatar)
        if (time_now.hour == 0 and time_now.minute == 0 and
                time_now.second == 0):
            # Submit usage statistics to the SprintBot development server
            usage_channel = client.get_channel(633451370103701535)
            servers = len(client.guilds)
            sprints = session.query(Sprint).count()
            await usage_channel.send(f"SprintBot is on {servers} servers " +
                                     f"and has helped with {sprints} word " +
                                     "sprints!")
        for sprint in query:
            if (time_now >= sprint.start_time and sprint.is_active and not
                    sprint.is_started):
                # Start the sprint
                minutes = (sprint.end_time - sprint.start_time).seconds / 60
                if minutes == 1:
                    minute_text = "minute"
                else:
                    minute_text = "minutes"
                channel = client.get_channel(
                    int(session.query(SprintChannel).get(
                        sprint.sprintchannel_id).channel_id))
                await channel.send("The sprint has begun! It will last for " +
                                   f"{int(minutes)} {minute_text}.")
                sprint.is_started = True
                session.commit()
            elif sprint.is_started and at_halfway_point(
                    sprint.halfway_point, time_now):
                # Inform the channel that the sprint is halfway done
                minutes = (sprint.end_time - sprint.start_time).seconds / 120
                if minutes == 1:
                    remainder = "One minute"
                else:
                    if minutes == int(minutes):
                        remainder = f"{minutes} minutes"
                    else:
                        if int(minutes) > 0:
                            remainder = (f"{int(minutes)} minutes and 30 " +
                                         "seconds")
                        else:
                            remainder = "30 seconds"
                channel = client.get_channel(
                    int(session.query(SprintChannel).get(
                        sprint.sprintchannel_id).channel_id))
                await channel.send(f"The sprint is halfway done! {remainder}" +
                                   " remaining.")
            elif time_now >= sprint.end_time and sprint.is_started:
                # End the sprint
                channel = client.get_channel(
                    int(session.query(SprintChannel).get(
                        sprint.sprintchannel_id).channel_id))
                await channel.send("The sprint is complete! Let everyone " +
                                   "know how you did!")
                sprint.is_active = False
                session.commit()
        await asyncio.sleep(1)


@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(
        name='Type "sb! help"'))
    print("SprintBot is ready.")


@client.event
async def on_guild_join(server):
    """
    Registers the new server to the SprintServer table in our DB,
    unless it's already there (perhaps due to SprintBot being kicked
    from a server)

    Note that the Discord API calls servers 'guilds' (or more accurately,
    the Discord UI calls guilds 'servers'). The bot documentation will
    refer to guilds/servers as 'servers', and the word 'server' will be
    used in code wherever possible.
    """
    if not session.query(SprintServer).filter(
            SprintServer.server_id == server.id).all():
        new_server = SprintServer(server_id=server.id)
        session.add(new_server)
        session.commit()


@client.event
async def on_message(message):
    """
    This handles the bot's reaction to messages. In order to play
    nice with other bots, the bot only reacts if directly messaged,
    or if @-mentioned on a group or server channel. It also reacts if the
    message string starts with 'sb!'.
    """
    if message.author.bot:
        # Bots should not react to each other's messages, or itself
        return

    if message.type is not discord.MessageType.default:
        # Bots shouldn't react to things like pin alerts, calls, new members
        return

    valid_message = False
    if message.channel.type is discord.ChannelType.private:
        valid_message = True
    if client.user in message.mentions:
        valid_message = True
    if message.content.startswith('sb!'):
        valid_message = True
    if not valid_message:
        return

    """
    Handle all commands from here.

    Sprint commands:
    sprint X :MM - Start a sprint at the next specified minute
    that will last X minutes.

    sprint :MM X - Same as above

    sprint X - Starts a sprint that will last X minutes at the
    next minute that is divisible by 5.

    sprint :MM - Starts a sprint at the specified minute that will
    last 15 minutes.
    """
    sprint_two_arg_match = re.search(sprint_two_args, message.content)
    if sprint_two_arg_match:
        captures = sprint_two_arg_match.group(1, 2)
        length = 0
        start_time = 0
        for capture in captures:
            if capture.startswith(":"):
                if len(capture) > 3:
                    # Needs to be in the format :MM
                    return
                start_time = int(capture[1:])
            else:
                length = int(capture.split(" ")[0])
        # Add the sprint channel if it doesn't already exist
        channel = get_sprint_channel(message)

        # Ensure there isn't already an active sprint in this channel
        if await active_sprint_already_exists(channel, message):
            return

        # Create a new sprint
        await create_new_sprint(start_time, length, channel, message)
        return

    sprint_one_arg_match = re.search(sprint_one_arg, message.content)
    if sprint_one_arg_match:
        capture = sprint_one_arg_match.group(1)
        if capture.startswith(':'):
            if len(capture) > 3:
                # Needs to be in the format :MM
                return
            start_time = int(capture[1:])
            if start_time < 0 or start_time > 59:
                return
            length = 15
        else:
            length = int(capture)
            if length < 1:
                return
            start_time = datetime.utcnow()
            while True:
                start_time = start_time + timedelta(seconds=60)
                if start_time.minute % 5 == 0:
                    break
            start_time = start_time.minute

        # Add the sprint channel if it doesn't already exist
        channel = get_sprint_channel(message)

        # Ensure there isn't already an active sprint in this channel
        if await active_sprint_already_exists(channel, message):
            return

        # Create a new sprint
        await create_new_sprint(start_time, length, channel, message)

        return

    """
    Command to cancel a scheduled sprint: sprint cancel
    Can ONLY be used by the user who started the sprint in that channel or by
    users with typical moderator privileges.
    Can ONLY target sprints that have been scheduled, but haven't started yet.
    """
    if 'cancel sprint' in message.content:
        # Add the sprint channel if it doesn't already exist
        channel = get_sprint_channel(message)

        query = session.query(Sprint).filter(Sprint.is_active == literal(
            True)).filter(Sprint.sprintchannel == channel).all()
        if not query:
            await message.channel.send(
                "There's no scheduled sprint to cancel.")
        else:
            sprint = query[0]
            if sprint.user_id == str(message.author.id) or messager_is_mod(
                    message):
                if sprint.is_started:
                    await message.channel.send(
                        "Can't cancel a sprint that's already started.")
                else:
                    sprint.is_active = False
                    session.commit()
                    await message.channel.send("Sprint canceled.")
            else:
                await message.channel.send(
                    "Can't cancel a sprint you didn't schedule.")

        return

    """
    Command to provide usage help to a user. The user is PMed all help
    information if they accept PMs.
    """
    if 'help' in message.content or 'info' in message.content:
        await message.author.send(help_text)


client.loop.create_task(stopwatch())
client.run(secrets.client_token)
