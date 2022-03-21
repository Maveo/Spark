import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.sql import func
from typing import *


class Representable:
    def __repr__(self) -> str:
        return self._repr(**{k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def _repr(self, **fields: Dict[str, Any]) -> str:
        """
        Helper for __repr__
        """
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except db.orm.exc.DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"


Base = declarative_base(cls=Representable)


class ActiveModule(Base):
    __tablename__ = 'active_modules'
    guild_id = db.Column(db.Integer, primary_key=True)
    module = db.Column(db.String, primary_key=True)


class Setting(Base):
    __tablename__ = 'settings'
    guild_id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, primary_key=True)
    value = db.Column(db.String, nullable=False)


class LevelSystem(Base):
    __tablename__ = 'level_system'
    guild_id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, nullable=False)


class LevelUser(Base):
    __tablename__ = 'level_user'
    guild_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    level = db.Column(db.Float, nullable=False)
    last_joined = db.Column(db.Integer)
    blacklisted = db.Column(db.Boolean, nullable=False)
    xp_origin = relationship('XPOrigin')
    xp_boost = relationship('XPBoost')


class XPOrigin(Base):
    __tablename__ = 'xp_origin'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Integer, nullable=False)
    origin = db.Column(db.String, nullable=True)
    guild_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    __table_args__ = (db.ForeignKeyConstraint((guild_id, user_id),
                                              [LevelUser.guild_id, LevelUser.user_id]),
                      {})


class XPBoost(Base):
    __tablename__ = 'xp_boost'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    origin = db.Column(db.String, nullable=False)
    expires = db.Column(db.Integer)
    guild_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)
    __table_args__ = (db.ForeignKeyConstraint((guild_id, user_id),
                                              [LevelUser.guild_id, LevelUser.user_id]),
                      {})


class MessageReaction(Base):
    __tablename__ = 'message_reactions'
    guild_id = db.Column(db.Integer, primary_key=True)
    trigger = db.Column(db.String, primary_key=True)
    reaction = db.Column(db.String, nullable=False)


class EmojiReaction(Base):
    __tablename__ = 'emoji_reactions'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, nullable=False)
    channel_id = db.Column(db.Integer, nullable=False)
    message_id = db.Column(db.Integer, nullable=False)
    emoji = db.Column(db.String, nullable=False)
    action_type = db.Column(db.String, nullable=False)
    action = db.Column(db.String, nullable=True)


class Database:
    def __init__(self, path, logger=None, protocol='sqlite', hostname=''):
        engine = db.create_engine('{}://{}/{}'.format(protocol, hostname, path))
        Base.metadata.create_all(engine)

        self.logger = logger

        session_factory = sessionmaker(bind=engine)

        self.Session = scoped_session(session_factory)

    def set_logger(self, logger):
        self.logger = logger

    def activate_module(self, guild_id, module):
        session = self.Session()
        session.merge(ActiveModule(guild_id=guild_id, module=module))
        session.commit()

    def deactivate_module(self, guild_id, module):
        session = self.Session()
        stmt = db.delete(ActiveModule).where(db.and_(ActiveModule.guild_id == guild_id, ActiveModule.module == module))
        session.execute(stmt)
        session.commit()

    def get_activated_modules(self, guild_id) -> List[str]:
        session = self.Session()
        stmt = db.select(ActiveModule).where(ActiveModule.guild_id == guild_id)
        return [x.module for x in session.scalars(stmt)]

    def get_setting(self, guild_id, key):
        session = self.Session()
        stmt = db.select(Setting).where(db.and_(Setting.guild_id == guild_id, Setting.key == key))
        res = session.scalars(stmt).first()
        if res is not None:
            res = res.value
        return res

    def set_setting(self, guild_id, key, value):
        session = self.Session()
        session.merge(Setting(guild_id=guild_id, key=key, value=value))
        session.commit()

    def remove_setting(self, guild_id, key):
        session = self.Session()
        stmt = db.delete(Setting).where(db.and_(Setting.guild_id == guild_id, Setting.key == key))
        session.execute(stmt)
        session.commit()

    def get_levelsystem(self, guild_id) -> List[LevelSystem]:
        session = self.Session()
        stmt = db.select(LevelSystem).where(LevelSystem.guild_id == guild_id)
        return list(session.scalars(stmt))

    def set_levelsystem(self, guild_id, level, role_id):
        session = self.Session()
        session.merge(LevelSystem(guild_id=guild_id, level=level, role_id=role_id))
        session.commit()

    def remove_levelsystem_by_level(self, guild_id, level):
        session = self.Session()
        stmt = db.delete(LevelSystem).where(db.and_(LevelSystem.guild_id == guild_id, LevelSystem.level == level))
        session.execute(stmt)
        session.commit()

    def get_level_user(self, guild_id, user_id) -> LevelUser:
        session = self.Session()
        stmt = db.select(LevelUser).where(db.and_(LevelUser.guild_id == guild_id, LevelUser.user_id == user_id))
        return session.scalars(stmt).first()

    def get_level_users(self, guild_id) -> List[LevelUser]:
        session = self.Session()
        stmt = db.select(LevelUser).where(LevelUser.guild_id == guild_id)
        return session.scalars(stmt).all()

    def get_blacklisted_level_users(self, guild_id, blacklisted) -> List[LevelUser]:
        session = self.Session()
        stmt = db.select(LevelUser).where(db.and_(LevelUser.guild_id == guild_id, LevelUser.blacklisted == blacklisted))
        return session.scalars(stmt).all()

    def get_level_user_xp_boosts(self, guild_id, user_id, current_time=-1) -> List[XPBoost]:
        session = self.Session()
        stmt = db.select(XPBoost).where(db.and_(XPBoost.guild_id == guild_id, XPBoost.user_id == user_id,
                                                db.or_(XPBoost.expires.is_(None), XPBoost.expires > current_time)))
        return session.scalars(stmt).all()

    def get_level_user_xp_boosts_by_origin(self, guild_id, user_id, origin, current_time=-1) -> List[XPBoost]:
        session = self.Session()
        stmt = db.select(XPBoost).where(db.and_(XPBoost.guild_id == guild_id,
                                                XPBoost.user_id == user_id,
                                                XPBoost.origin == origin,
                                                db.or_(XPBoost.expires.is_(None), XPBoost.expires > current_time)))
        return session.scalars(stmt).all()

    def get_level_users_xp_boosts_by_origin(self, guild_id, origin, current_time=-1) -> List[XPBoost]:
        session = self.Session()
        stmt = db.select(XPBoost).where(db.and_(XPBoost.guild_id == guild_id,
                                                XPBoost.origin == origin,
                                                db.or_(XPBoost.expires.is_(None), XPBoost.expires > current_time)))
        return session.scalars(stmt).all()

    def get_level_user_xp_boosts_by_origin_prefix(
            self, guild_id, user_id, origin_prefix, current_time=-1) -> List[XPBoost]:
        session = self.Session()
        stmt = db.select(XPBoost).where(db.and_(XPBoost.guild_id == guild_id,
                                                XPBoost.user_id == user_id,
                                                XPBoost.origin.startswith(origin_prefix),
                                                db.or_(XPBoost.expires.is_(None), XPBoost.expires > current_time)))
        return session.scalars(stmt).all()

    def update_level_user(self, guild_id, user_id, kwargs):
        session = self.Session()
        session.merge(LevelUser(guild_id=guild_id, user_id=user_id, **kwargs))
        session.commit()

    def add_xp_boost(self, guild_id, user_id, amount, origin, expires=None):
        session = self.Session()
        session.add(XPBoost(guild_id=guild_id, user_id=user_id, amount=amount, origin=origin, expires=expires))
        session.commit()

    def add_xp_origin(self, guild_id, user_id, amount, origin):
        session = self.Session()
        session.add(XPOrigin(guild_id=guild_id, user_id=user_id, amount=amount, origin=origin))
        session.commit()

    def get_xp_origin(self, guild_id, user_id):
        session = self.Session()
        stmt = session.query(XPOrigin, func.sum(XPOrigin.amount).label("total")).filter(
            db.and_(XPOrigin.guild_id == guild_id, XPOrigin.user_id == user_id)).group_by(XPOrigin.origin)
        return stmt.all()

    def set_message_reaction(self, guild_id, trigger, reaction):
        session = self.Session()
        session.merge(MessageReaction(guild_id=guild_id, trigger=trigger, reaction=reaction))
        session.commit()

    def remove_message_reaction(self, guild_id, trigger):
        session = self.Session()
        session.query(MessageReaction).filter(
            db.and_(MessageReaction.guild_id == guild_id, MessageReaction.trigger == trigger)).delete()
        session.commit()

    def get_message_reactions(self, guild_id) -> List[MessageReaction]:
        session = self.Session()
        stmt = db.select(MessageReaction).where(MessageReaction.guild_id == guild_id)
        return session.scalars(stmt).all()

    def get_message_reaction(self, guild_id, trigger) -> MessageReaction:
        session = self.Session()
        stmt = db.select(MessageReaction).where(
            db.and_(MessageReaction.guild_id == guild_id, MessageReaction.trigger == trigger))
        return session.scalars(stmt).first()

    def set_emoji_reaction(self, guild_id, channel_id, message_id, emoji, action_type, action):
        session = self.Session()
        session.merge(EmojiReaction(guild_id=guild_id,
                                    channel_id=channel_id,
                                    message_id=message_id,
                                    emoji=emoji,
                                    action_type=action_type,
                                    action=action))
        session.commit()

    def get_emoji_reactions(self, guild_id) -> List[EmojiReaction]:
        session = self.Session()
        stmt = db.select(EmojiReaction).where(EmojiReaction.guild_id == guild_id)
        return session.scalars(stmt).all()

    def get_emoji_reactions_by_payload(self, guild_id, channel_id, message_id, emoji) -> List[EmojiReaction]:
        session = self.Session()
        stmt = db.select(EmojiReaction).where(db.and_(
            EmojiReaction.guild_id == guild_id,
            EmojiReaction.channel_id == channel_id,
            EmojiReaction.message_id == message_id,
            EmojiReaction.emoji == emoji
        ))
        return session.scalars(stmt).all()

    def remove_emoji_reaction(self, guild_id, reaction_id):
        session = self.Session()
        stmt = db.delete(EmojiReaction).where(db.and_(EmojiReaction.guild_id == guild_id,
                                                      EmojiReaction.id == reaction_id))
        session.execute(stmt)
        session.commit()
        session = self.Session()
        stmt = db.delete(EmojiReaction).where(EmojiReaction.id == reaction_id)
        session.execute(stmt)
        session.commit()
