import werkzeug


class UnauthorizedException(werkzeug.exceptions.HTTPException):
    code = 401


class UnknownException(werkzeug.exceptions.HTTPException):
    code = 400


class WrongInputException(werkzeug.exceptions.HTTPException):
    code = 400


class MethodNotAvailableException(werkzeug.exceptions.HTTPException):
    code = 400


class ModuleNotActivatedException(werkzeug.exceptions.HTTPException):
    code = 400

    def __init__(self, *args, **kwargs):
        self.description = 'module is not activated'
        super().__init__(*args, **kwargs)


class BoostingYourselfForbiddenException(WrongInputException):
    def __init__(self, *args, **kwargs):
        self.description = 'boosting yourself forbidden'
        super().__init__(*args, **kwargs)


class BoostNotExpiredException(WrongInputException):
    def __init__(self, *args, **kwargs):
        self.description = 'boost not expired'
        super().__init__(*args, **kwargs)


class LevelingBlacklistedUserException(WrongInputException):
    def __init__(self, *args, **kwargs):
        self.description = 'user is blacklisted'
        super().__init__(*args, **kwargs)


class PromotingYourselfForbiddenException(WrongInputException):
    def __init__(self, *args, **kwargs):
        self.description = 'promoting yourself forbidden'
        super().__init__(*args, **kwargs)


class PromoCodeNotFoundException(WrongInputException):
    def __init__(self, *args, **kwargs):
        self.description = 'promo code not found'
        super().__init__(*args, **kwargs)


class ItemNotUsableException(WrongInputException):
    pass


class WheelspinForbiddenException(WrongInputException):
    pass


class NoMoneyException(WrongInputException):
    pass
