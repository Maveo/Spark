from helpers.settings_manager import Setting

SETTINGS = {
    'PROMO_CODE_EXPIRES_HOURS': Setting(
        value=24.0,
        description='Time period after which a promo code expires (in hours | you can use floats to define more '
                    'accurate time periods, e.g 6.5 will set a 6 hours and 30 minutes expiration length)',
        itype='float',
        categories=['Promo']
    ),
    'PROMO_CODE_LENGTH': Setting(
        value=6,
        description='Length of generated promo codes',
        itype='int',
        categories=['Promo']
    ),
    'PROMO_CHANNEL_ID': Setting(
        value='',
        description='Sets one promo channel, in which users can enter promo codes (warning messages)',
        itype='string',
        categories=['Promo']
    ),
    'PROMO_CHANNEL_DELETE_MESSAGES_SECONDS': Setting(
        value=5,
        description='delete messages in the promo channel after x seconds (use -1 to not delete messages)',
        itype='int',
        categories=['Promo']
    ),
    'PROMO_BOOST_EXPIRES_DAYS': Setting(
        value=7.0,
        description='Time period after which the promo xp-boost expires (in days | you can use floats to define more '
                    'accurate time periods, e.g 6.5 will set a 6 days and 12 hours expiration length)',
        itype='float',
        categories=['Promo', 'Boost']
    ),
    'PROMO_BOOST_ADD_XP_MULTIPLIER': Setting(
        value=2.0,
        description='Configures the xp-multiplier awarded to the user who created and distributed their promo code',
        itype='float',
        categories=['Promo', 'Boost']
    ),
    'PROMO_USER_SET_LEVEL': Setting(
        value=2.0,
        description='Configures the level reward given to the new user who entered someone elses promo code (again, '
                    'you can use a float)',
        itype='float',
        categories=['Promo']
    ),
}
