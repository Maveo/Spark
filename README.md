
# - Spark -
 ### A Discord Bot
![alt text](https://cdn.discordapp.com/avatars/843214102108962856/9d05175cc55385fa4a5f5313a858a045.webp?size=128 "Sparks face")

## Application

Spark is currently being beta-tested on the [StudeGaming Discord Server](https://discord.gg/MzXV5GYRsN "Join the Discord") and continuous to be enhanced by his developer [skillor]( https://github.com/skillor "Visit his github profile"). It currently is not publicly avaliable, so can't be easily invited to your Discord server. Should you still want to use Spark on your Discord server, feel free to use it's source code to host it yourself.

## Installation

### Setup in Windows

> Clone the repository

    git clone https://github.com/skillor/Spark.git

> Install the requirements

    python -m pip install -r requirements.txt

> Copy the "settings.py.example" to "settings.py"

    copy settings.py.example settings.py

> Edit your settings like "APPLICATION_ID", "TOKEN" etc.

> Run tests

    python tests.py

> Start the bot

    python bot.py

### Setup in Unix

> Clone the repository

    git clone https://github.com/skillor/Spark.git

> Install the requirements

    pip3 install -r requirements.txt

> Copy the "settings.py.example" to "settings.py"

    cp settings.py.example settings.py

> Edit your settings like "APPLICATION_ID", "TOKEN" etc.

> Run tests

    python3 tests.py

> Start the bot

    python3 bot.py

## Available Commands

- **coinflip**
	- Toss a coin to your Witcher!
 - **random**
	- Generate a random number
 - **dice**
	- Rolls a six-sided dice
- **help**
	- A short list of avaliable commands
- **leaderboard**
	- Shows the Top 10 of the Server
- **lvlsys** *(requires administrator permissions)*
	- Everything about the level system
- **profile**
	- Shows your profile-card
	- "profile {username}" Show another user
- **boost**
	- Users can give other users a temporary xp-multiplier (can be adjusted in settings)
- **promo**
	- get a promo code to use for the promo system
- **ranking-all** *(requires administrator permissions)*
	- Posts all profile-cards of the server
- **send** *(requires administrator permissions)*
	- Talk through the bot in chat
- **settings** *(requires administrator permissions)*
	- Set Discord server specific parameters
- **setlvl** *(requires administrator permissions)*
	- Set a users level
- **clear** *(requires administrator permissions)*
	- Clear a certain number of messages in a text-channel

## Configurable Settings

### Global Settings

These Settings are applied globally and **cannot be changed without restarting** the application

- **APPLICATION_ID** is the Application-ID for your Discord Developer Application
- **TOKEN** is the Token of your Discord Bot
- **COMMAND_PREFIX** is the Command Prefix for the Discord Bot
- **PRINT_LOGGING** if logs should be printed to the console
- **USE_SLASH_COMMANDS** if [discord-py-slash-commands](https://github.com/eunwoo1104/discord-py-slash-command) should be used to interact with the [Discord Slash Commands API](https://discord.com/developers/docs/interactions/slash-commands)
- **UPDATE_VOICE_XP_INTERVAL** the interval in seconds in which the users should receive the xp for being in a voice channel (use -1 for no update interval)

### Default Guild Settings

These Settings are applied for each discord guild (server) and **can be changed** via the settings command

- **NEW_USER_LEVEL** the level a new user who joins the guild will be set to (you can use floats to set the relative XP, e.g. 3.5 will assign Level 3 and 60 XP)
- **NEW_USER_XP_MULTIPLIER** the xp multiplier a new user will have
- **MESSAGE_XP** the Base-XP a user receives for sending a message
- **VOICE_XP_PER_MINUTE** the Base-XP a user receives per minute for being in a voice channel (AFK-Channel does not give XP)
- **BOOST_EXPIRES_DAYS** the days after which the XP boost by the boost command expires
- **BOOST_ADD_XP_MULTIPLIER** the XP boost the boost command gives
- **SEND_WELCOME_IMAGE** if a welcome image should be sent from the bot via DM when a new user joins
- **PROMO_CHANNEL_ID** the channel id of the Channel to redeem Promo Codes **(don't change this in the settings.py)**
- **PROMO_CODE_LENGTH** the length of the promo code to generate
- **PROMO_CODE_EXPIRES_HOURS** the time in hours after which a promo code expires
- **PROMO_BOOST_EXPIRES_DAYS** the days after which the XP boost of the creator of the promo code expires
- **PROMO_BOOST_ADD_XP_MULTIPLIER** the XP boost the creator of the promo code gets
- **PROMO_USER_SET_LEVEL** the level a user who redeems a promo code will be set to (again, you can use a float)
- **COMMAND_NOT_FOUND_RESPONSES** the response choices the bot has if a unknown command was used
- **MISSING_PERMISSIONS_RESPONSES** the response choices the bot has if a user misses permission to use a command
- **PROFILE_IMAGE** the template to create a profile image
- **LEVEL_UP_IMAGE** the template to create a level up image
- **RANK_UP_IMAGE** the template to create a rank up image
- **RANKING_IMAGE** the template to create a ranking image
- **WELCOME_IMAGE** the template to create a welcome image

## Features

#### Spark has an evergrowing utility set with numerous advanced features:

 - #### Level System
	The level system tracks users voice-channel and chat activity on the server and rewards them with XP, which enables users to get levels. Server admins are then able to create ranks on certain level targets using the <kbd>/lvlsys set {level target} {role-id}</kbd> command and assign roles, that will  automatically be given to users hitting the stated level target (rank). All parameters like the rate at which users gain XP can be edited in the source code. Furthermore admins can change users levels and XP-multipliers, aswell as blacklisting users from gaining XP using <kbd>/lvlsys</kbd> chat commands.

 - #### Custom Bot Responses
	When a user attempts to use a command without the permission to do so, the bot will deny the interaction and jokingly inform the user with one of 13 different custom text messages. The same will happen when a user executes an unknown command.

 - #### Advanced Command Interaction
	Spark is able to communicate trough Discords slash command integration, which offers a more polished user experience and will help to keep your chat cleaner. Additionally Spark can handle user related commands with @mentions.

 - #### Custom Image Generation
	The Bot is equiped with a custom image generator, which will create custom levelup, rankup, leaderboard and profile-card images. All images can be designed using the build-in design code, that is build similar to knwon webdesign languages like CSS.
