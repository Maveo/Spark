from helpers.settings_manager import Setting

SETTINGS = {
    'COIN_FLIP_AUDIO_CHANCE': Setting(
        value=0.01,
        description='Set the chance at which the bot will join a voice channel and play an audio track for the '
                    'coinflip command (a float as percentage, e.g. 0.4 equals 40%)',
        itype='float'
    ),
}
