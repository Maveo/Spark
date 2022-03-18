from helpers.settings_manager import Setting

SETTINGS = {
    'BOOST_ADD_XP_MULTIPLIER': Setting(
        value=0.25,
        description='Configures the xp-multiplier of the >boost command',
        itype='float',
        categories=['Boost']
    ),
    'BOOST_EXPIRES_DAYS': Setting(
        value=7.0,
        description='Time period after which a boost expires (in days | you can use floats to define more accurate '
                    'time periods, e.g 6.5 will set a 6 days and 12 hours expiration length)',
        itype='float',
        categories=['Boost']
    ),
}
