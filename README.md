# SprintBot
SprintBot is a Discord bot for managing word sprints for NaNoWriMo communities. If you're not familiar with NaNoWriMo (National Novel Writing Month), check out http://www.nanowrimo.org.

## Usage
To add SprintBot to your Discord server, [click here](https://discordapp.com/channels/632747287067754497/632747287067754501/632930249696477187). Note that you will need to give SprintBot permission to read and write messages in your server.

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

# Contributions

Pull requests are alweays welcome. If you're not a programmer, you can still contribute by joining the official SprintBot development Discord server to make suggestions or report bugs in the #development channel.

Official SprintBot development Discord: https://discord.gg/HJeG5u7
