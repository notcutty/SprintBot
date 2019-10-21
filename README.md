# SprintBot (v2019.10.15)
SprintBot is a Discord bot for managing word sprints for NaNoWriMo communities. If you're not familiar with NaNoWriMo (National Novel Writing Month), check out http://www.nanowrimo.org.

## Usage
SprintBot does not require any installation; it is running on a server, and all you need to do is add it to a Discord server you administrate. To add SprintBot to your Discord server, [click here](https://discordapp.com/api/oauth2/authorize?client_id=632592411838775318&permissions=3072&scope=bot). Note that you will need to give SprintBot permission to read and write messages in your server.

You can use SprintBot commands by starting your message with "sb!" (without quotes) or by tagging @SprintBot#8987 in your message. You can also DM SprintBot directly to use these commands by yourself.

The following commands are available:

### sprint X :MM
Schedules a sprint that will last for X minutes and starts when the clock reaches the :MM minute.

### sprint :MM X
Works the same as above, with the input order swapped.

### sprint X
Schedules a sprint of the specified length that will start when the clock reaches a minute divisible by 5 (:00, :05, :10, etc.)

### sprint :MM
Schedules a 15-minute sprint when the clock next reaches the :MM minute.

### cancel sprint
Cancels a sprint that has been scheduled, but hasn't started yet. Note that sprints that have already started can't be canceled, and that only the user who scheduled a sprint or a moderator of a channel can cancel sprints.

# Running Your Own Instance

You can run your own instance of SprintBot. A minimum of Python 3.6, SQLAlchemy 1.3, and the latest version of discord.py are required. You can install prerequisites with pip:

```
pip install sqlalchemy
pip install discord.py
```

After that, you will need to establish a SprintBot on the Discord Developer Portal and save the client token in sprintbot_client_token.py.

```
client_token = '(your client token here)'
```

For security purposes, it is advised that you do not share your client token publicly.

If you want your SprintBot to report usage information to a specific channel on a server that it's on, you will need to edit bot_info.py with the integer values of your bot's user ID and the channel it should report to. Note that this is not required for SprintBot to run.

# Contributions

Pull requests are alweays welcome. Feel free to add issues on the issue tracker as well. If you're not a programmer, you can still contribute by joining the official SprintBot development Discord server to make suggestions or report bugs in the #development channel.

Official SprintBot development Discord: https://discord.gg/HJeG5u7

If you're financially stable, consider contributing to SprintBot's server costs: https://www.buymeacoffee.com/VR41jDulG
