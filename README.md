# - Spark -
[![Build Status](https://www.travis-ci.com/skillor/Spark.svg?branch=master)](https://www.travis-ci.com/skillor/Spark)


 ### A Discord Bot
![alt text](https://cdn.discordapp.com/avatars/843214102108962856/9d05175cc55385fa4a5f5313a858a045.webp?size=128 "Sparks face")

## Application

Spark is currently being beta-tested on the [StudeGaming Discord Server](https://discord.gg/MzXV5GYRsN "Join the Discord") and continues to be enhanced by his developer [skillor](https://github.com/skillor "Visit his github profile"). If you are interested in Sparks development, you can view the project roadmap and history in the [Projects](https://github.com/skillor/Spark/projects "A deep dive into Sparks development") tab. If you have any suggestions or bug reports and want to help the development process, you are welcome to let us know in the [Issues](https://github.com/skillor/Spark/issues/new/choose "Give us feedback") tab. Spark is currently not publicly avaliable, so can't be easily invited to your Discord server. Should you still want to use Spark on your Discord server, feel free to use it's source code to host it yourself.

## Installation

### Setup in Windows

> Clone repository

    git clone https://github.com/skillor/Spark.git

> Install requirements

    python -m pip install -r requirements.txt

> Copy "settings_example.py" to "settings.py"

    copy settings_example.py settings.py

> Edit your "APPLICATION_ID", "TOKEN" etc. in the settings.py

> Run tests

    python tests.py

> Start the bot

    python bot.py

### Setup in Unix

> Clone repository

    git clone https://github.com/skillor/Spark.git

> Install requirements

    pip3 install -r requirements.txt

> Copy "settings_example.py" to "settings.py"

    cp settings_example.py settings.py

> Edit your "APPLICATION_ID", "TOKEN" etc. in the settings

> Run tests

    python3 tests.py

> Start the bot

    python3 bot.py

## Available Commands

- `>coinflip` Toss a coin to your Witcher!
- `>random` Generate a random number
- `>dice` Rolls a six-sided dice
- `>help` A short list of avaliable commands
- `>leaderboard` Shows the Top 10 of the Server
- `>profile` Shows your profile-card | "profile {username}" Show another user
- `>boost` Users can give other users a temporary xp-multiplier (can be adjusted in settings)
- `>promo` get a promo code to use for the promo system
- `>lvlsys` Everything about the level system *(requires administrator permissions)* 
- `>ranking-all` Posts all profile-cards of the server *(requires administrator permissions)*
- `>send` Talk through the bot in chat *(requires administrator permissions)*
- `>settings` Set Discord server specific parameters *(requires administrator permissions)*
- `>setlvl` Set a users level *(requires administrator permissions)*
- `>clear` Clear a certain number of messages in a text-channel *(requires administrator permissions)*

## Configurable Settings

### Global Settings

These Settings are applied globally and **cannot be changed without restarting** the application

- **APPLICATION_ID**

  This is the Application-ID for your Discord Developer Application
- **APPLICATION_SECRET**

  This is the Oauth2-Application-Secret for your Discord Developer Application
- **OAUTH2_REDIRECT_URI**

  This is the Oauth2-Redirect-Uri for your Discord Developer Application, you need to add "/oauth2" for the default setup (e.g. http://your.domain/oauth2)
  You also need to set this up in the Discord Developer Settings
- **WEBSERVER_PORT**

  This is the Port for the Webserver
- **TOKEN** 

  This is the Token of your Discord Bot
- **COMMAND_PREFIX**

  This is the Command Prefix for the Discord Bot
- **PRINT_LOGGING**

   Enable/disable log printing to the console
- **USE_SLASH_COMMANDS**

   Configures if [discord-py-slash-commands](https://github.com/eunwoo1104/discord-py-slash-command "Visit their GitHub page") should be used to interact with the [Discord Slash Commands API](https://discord.com/developers/docs/interactions/slash-commands "Official Discord documentation")
- **UPDATE_VOICE_XP_INTERVAL**

   The interval in which users automatically recieve their xp for being in a voice channel (in seconds | use -1 for no update interval)
- **DOWNLOAD_EMOJIS**

  If emojis should be acquired from [emojipedia](https://emojipedia.org/).
- **SAVE_EMOJIS**

  If the downloaded emojis should be saved locally.
- **EMOJIS_PATH**

  The path to load and save emojis.


### Default Guild Settings

These settings are applied for each Discord guild (server) and **can be changed** via the settings command

- **NEW_USER_LEVEL**

  New users will be set this level (you can use floats to set the relative xp, e.g. 3.5 will assign Level 3 and 60 xp)
 
- **NEW_USER_XP_MULTIPLIER**
 
  The default xp multiplier for new users
- **MESSAGE_XP**

  The base-xp a user receives for sending a message
- **VOICE_XP_PER_MINUTE**
 
  The base-xp a user receives per minute for being in a voice channel (AFK-channel does not give xp)
- **BOOST_EXPIRES_DAYS**
  
  Time period after which a boost expires (in days | you can use floats to define more accurate time periods, e.g 6.5 will set a 6 days and 12 hours expiration length)
- **BOOST_ADD_XP_MULTIPLIER**
 
  Configures the xp-multiplier of the `>boost` command
- **SEND_WELCOME_IMAGE**
 
  Enables/disables the welcome image sent by the bot via DM when a new user joins
- **PROMO_CHANNEL_ID**
 
  Sets one promo channel, in which users can enter promo codes **(don't change this in the settings.py)**
- **PROMO_CODE_LENGTH**
  
   Length of generated promo code
- **PROMO_CODE_EXPIRES_HOURS**
 
  Time period after which a promo code expires (in days | you can use floats to define more accurate time periods, e.g 6.5 will set a 6 days and 12 hours expiration length)
- **PROMO_BOOST_EXPIRES_DAYS**

  Time period after which the promo xp-boost expires (in days | you can use floats to define more accurate time periods, e.g 6.5 will set a 6 days and 12 hours expiration length)
- **PROMO_BOOST_ADD_XP_MULTIPLIER**
 
  Configures the xp-multiplier awarded to the user who created and distributed their promo code
- **PROMO_USER_SET_LEVEL**

  Configures the level reward given to the new user who entered someone elses promo code (again, you can use a float)
- **COIN_FLIP_AUDIO_CHANCE**

  Set the chance at which the bot will join a voice channel and play an audio track for the coinflip command (a float as percentage, e.g. 0.4 equals 40%)
- **COMMAND_NOT_FOUND_RESPONSES**

  Set **entire list** of available response choices the bot replies with, if a unknown command was used
- **MISSING_PERMISSIONS_RESPONSES**

  Set **entire list** of available response choices the bot replies with, if a user entered a command without permission
- **PROFILE_IMAGE**

  Template to create the profile image upon
- **LEVEL_UP_IMAGE**

  Template to create a level up image upon
- **RANK_UP_IMAGE**

  Template to create a rank up image upon
- **RANKING_IMAGE**

  Template to create a ranking image upon
- **WELCOME_IMAGE**

  Template to create a welcome image upon

## Features

Spark has an evergrowing utility set with numerous advanced features:

 - #### Level System
	The level system tracks users voice-channel and chat activity on the server and rewards them with XP, which enables users to get levels. Server admins are then able to create ranks on certain level targets using the <kbd>/lvlsys set {level target} {role-id}</kbd> command and assign roles, that will  automatically be given to users hitting the stated level target (rank). All parameters like the rate at which users gain XP can be edited in the source code. Furthermore admins can change users levels and XP-multipliers, aswell as blacklisting users from gaining XP using <kbd>/lvlsys</kbd> chat commands.

 - #### Promotion Codes
    Users have to ability to provide new users with a promo code, which rewards the new user with a configurable level headstart and to old user with a temporary configurable xp-multiplier

 - #### Custom Bot Responses
	When a user attempts to use a command without the permission to do so, the bot will deny the interaction and jokingly inform the user with one of 13 different custom text messages. The same will happen when a user executes an unknown command.

 - #### Advanced Command Interaction
	Spark is able to communicate trough Discords slash command integration, which offers a more polished user experience and will help to keep your chat cleaner. Additionally Spark can handle user related commands with @mentions.

 - #### Custom Image Generation (ImageStack)
	The Bot is equiped with [ImageStack](https://github.com/skillor/imagestack-python "ImageStacks Git Repository") (a custom image generator), which will create custom levelup, rankup, leaderboard and profile-card images. All images can be designed using ImageStack Code.
