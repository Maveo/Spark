from helpers.settings_manager import Setting

SETTINGS = {
    'WHEELSPIN_FREE_RESET_HOURS': Setting(
        value=24.0,
        description='every x hours you get a free wheelspin',
        itype='float'
    ),
}
