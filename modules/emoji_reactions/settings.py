from helpers.settings_manager import Setting

SETTINGS = {
    'ALLOW_BOT_EMOJI_REACTIONS': Setting(
        value=False,
        description='If bots should be allowed emoji reactions',
        itype='bool'
    ),
}
