from fastapi import HTTPException


class UnknownException(HTTPException):
    def __init__(self, status_code=400, detail='unknown'):
        super().__init__(status_code, detail)


class WrongInputException(HTTPException):
    def __init__(self, status_code=400, detail='wrong_input'):
        super().__init__(status_code, detail)


class UnauthorizedException(HTTPException):
    def __init__(self, status_code=401, detail='unauthorized'):
        super().__init__(status_code, detail)


class MethodNotAvailableException(HTTPException):
    def __init__(self, status_code=400, detail='method_not_available'):
        super().__init__(status_code, detail)


class ModuleNotActivatedException(HTTPException):
    def __init__(self, status_code=400, detail='module_not_activated'):
        super().__init__(status_code, detail)


class BoostingYourselfForbiddenException(WrongInputException):
    def __init__(self):
        super().__init__(detail='boosting_yourself_forbidden')


class BoostNotExpiredException(WrongInputException):
    def __init__(self):
        super().__init__(detail='boost_not_expired')


class LevelingBlacklistedUserException(WrongInputException):
    def __init__(self):
        super().__init__(detail='level_user_blacklisted')


class PromotingYourselfForbiddenException(WrongInputException):
    def __init__(self):
        super().__init__(detail='promoting_yourself_forbidden')


class PromoCodeNotFoundException(WrongInputException):
    def __init__(self):
        super().__init__(detail='promo_code_not_found')


class ItemNotFoundException(WrongInputException):
    def __init__(self):
        super().__init__(detail='item_not_found')


class ItemNotUsableException(WrongInputException):
    def __init__(self):
        super().__init__(detail='item_not_usable')


class WheelspinForbiddenException(WrongInputException):
    def __init__(self):
        super().__init__(detail='wheelspin_forbidden')


class WheelspinEmptyException(WrongInputException):
    def __init__(self):
        super().__init__(detail='wheelspin_empty')


class NoMoneyException(WrongInputException):
    def __init__(self):
        super().__init__(detail='no_money')
