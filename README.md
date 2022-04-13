# - Spark -
[![Build Status](https://github.com/Maveo/Spark/actions/workflows/test-python.yml/badge.svg)](https://github.com/Maveo/Spark/actions/workflows/test-python.yml)


 ### A Discord Bot
![alt text](https://cdn.discordapp.com/avatars/843214102108962856/9d05175cc55385fa4a5f5313a858a045.webp?size=128 "Sparks face")

## Application

Spark is currently being beta-tested on the [StudeGaming Discord Server](https://discord.gg/MzXV5GYRsN "Join the Discord") and continues to be enhanced by his developer [skillor](https://github.com/skillor "Visit his github profile"). If you are interested in Sparks development, you can view the project roadmap and history in the [Projects](https://github.com/skillor/Spark/projects "A deep dive into Sparks development") tab. If you have any suggestions or bug reports and want to help in the development process, you are welcome to let us know in the [Issues](https://github.com/skillor/Spark/issues/new/choose "Give us feedback") tab. Spark is currently not publicly available, so can't be easily invited to your Discord server. Should you still want to use Spark on your Discord server, feel free to use it's source code to host it yourself.

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

## Module System

Spark consists of numerous modules which can be activated per Guild.
Use `/module activate` to activate a module.
These modules contain their respective commands and settings.


## Configurable Settings

### Global Settings

These settings are applied globally and **cannot be changed without restarting** the application

- **DATABASE_URL**

  The url for the database of Spark (e.g. ```mongodb://example.com:27017/```)
- **APPLICATION_ID**

  This is the Application-ID for your Discord Developer Application
- **APPLICATION_SECRET**

  This is the Oauth2-Application-Secret for your Discord Developer Application
- **ACTIVATE_WEBSERVER**

  If the webserver should be activated
- **OAUTH2_REDIRECT_URI**

  This is the Oauth2-Redirect-Uri for your Discord Developer Application, you need to add "/oauth2" for the default setup (e.g. http://your.domain/oauth2)
  You also need to set this up in the Discord Developer Settings
- **WEBSERVER_SECRET**

  A secret to encrypt the webserver sessions
- **WEBSERVER_PORT**

  This is the Port for the Webserver
- **TOKEN** 

  This is the Token of your Discord Bot
- **INTERVAL_TIME**

   The interval in which the modules do their scheduled update (in seconds | use -1 for no update interval)
- **DOWNLOAD_EMOJIS**

  If emojis should be acquired from [emojipedia](https://emojipedia.org/).
- **SAVE_EMOJIS**

  If the downloaded emojis should be saved locally.
- **EMOJIS_PATH**

  The path to load and save emojis.


### Module Settings

Every module can have own settings which are applied for each Discord guild (server) and **can be changed** via the settings command


## Features

Spark has an evergrowing utility set with numerous advanced features:

 - #### Modular
    Spark is highly modular

 - #### Frontend
	Spark has an own frontend, yay

 - #### Level System
    The level system tracks users voice-channel and chat activity on the server and rewards them with XP, which enables users to get levels. Server admins are then able to create ranks on certain level targets using the <kbd>/lvlsys set {level target} {role-id}</kbd> command and assign roles, that will  automatically be given to users hitting the stated level target (rank). All parameters like the rate at which users gain XP can be edited in the source code. Furthermore admins can change users levels and XP-multipliers, aswell as blacklisting users from gaining XP using <kbd>/lvlsys</kbd> chat commands.

 - #### Promotion Codes
    Users have to ability to provide new users with a promo code, which rewards the new user with a configurable level headstart and to old user with a temporary configurable xp-multiplier

 - #### Custom Bot Responses
    When a user attempts to use a command without the permission to do so, the bot will deny the interaction and jokingly inform the user with one of 13 different custom text messages. The same will happen when a user executes an unknown command.

 - #### Advanced Command Interaction
    Spark is able to communicate through Discords slash command integration, which offers a more polished user experience and will help to keep your chat cleaner. Additionally Spark can handle user related commands with @mentions.

 - #### Custom Image Generation (ImageStack)
    The Bot is equipped with [ImageStack-SVG](https://github.com/skillor/imagestack-svg-python "ImageStacks Git Repository") (a custom image generator), which will create custom levelup, rankup, leaderboard and profile-card images. All images can be designed using ImageStack-SVG Code.
