import sqlalchemy as db
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship, backref, aliased
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


class InventoryRarity(Base):
    __tablename__ = 'inventory_rarity'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    background_color = db.Column(db.String, nullable=False)
    foreground_color = db.Column(db.String, nullable=False)
    order = db.Column(db.Integer, nullable=False)


class InventoryItemType(Base):
    __tablename__ = 'inventory_item_type'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String, nullable=False)
    rarity_id = db.Column(db.Integer, nullable=False)
    always_visible = db.Column(db.Boolean, nullable=False)
    tradable = db.Column(db.Boolean, nullable=False)
    equippable = db.Column(db.Boolean, nullable=False)
    useable = db.Column(db.Integer, nullable=False)
    actions = db.Column(db.String, nullable=False)
    __table_args__ = (db.ForeignKeyConstraint((rarity_id,),
                                              [InventoryRarity.id]),
                      {})
    rarity = relationship(InventoryRarity, backref=backref("item_types", cascade="all,delete"))


class UserInventoryItem(Base):
    __tablename__ = 'user_inventory_item'
    guild_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    item_type_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    equipped = db.Column(db.Boolean, nullable=False)
    __table_args__ = (db.ForeignKeyConstraint((item_type_id,),
                                              [InventoryItemType.id]),
                      {})
    item_type = relationship(InventoryItemType, backref=backref("user_items", cascade="all,delete"))


class WheelspinProbability(Base):
    __tablename__ = 'wheelspin_probabilities'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, nullable=False)
    item_type_id = db.Column(db.Integer, nullable=False)
    probability = db.Column(db.Float, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    sound = db.Column(db.Boolean, nullable=False)
    __table_args__ = (db.ForeignKeyConstraint((item_type_id,),
                                              [InventoryItemType.id]),
                      {})
    item_type = relationship(InventoryItemType, backref=backref("wheelspin_items", cascade="all,delete"))


class WheelspinAvailable(Base):
    __tablename__ = 'wheelspins_available'
    guild_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    last_free = db.Column(db.Integer, nullable=False)


class StoreItems(Base):
    __tablename__ = 'store_items'
    id = db.Column(db.Integer, primary_key=True)
    guild_id = db.Column(db.Integer, nullable=False)
    from_item_id = db.Column(db.Integer, nullable=False)
    from_item_amount = db.Column(db.Float, nullable=False)
    to_item_id = db.Column(db.Integer, nullable=False)
    to_item_amount = db.Column(db.Float, nullable=False)
    __table_args__ = (db.ForeignKeyConstraint((from_item_id, to_item_id,),
                                              [InventoryItemType.id, InventoryItemType.id]),
                      {})


class Database:
    def __init__(self, db_url, logger=None):
        engine = db.create_engine(db_url)
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

    def get_rarities(self, guild_id) -> List[InventoryRarity]:
        session = self.Session()
        stmt = db.select(
            InventoryRarity).where(InventoryRarity.guild_id == guild_id).order_by(InventoryRarity.order.asc())
        return session.scalars(stmt).all()

    def edit_rarity(self, guild_id, rarity_id, name, foreground_color, background_color):
        session = self.Session()
        if rarity_id is not None:
            session.query(InventoryRarity).filter(db.and_(InventoryRarity.id == rarity_id,
                                                          InventoryRarity.guild_id == guild_id)).update(
                {
                    InventoryRarity.name: name,
                    InventoryRarity.foreground_color: foreground_color,
                    InventoryRarity.background_color: background_color,
                })
        else:
            stmt = session.query(InventoryRarity, func.count().label("count")).filter(
                InventoryRarity.guild_id == guild_id)
            session.add(InventoryRarity(guild_id=guild_id,
                                        name=name,
                                        foreground_color=foreground_color,
                                        background_color=background_color,
                                        order=stmt.first()[1]))
        session.commit()

    def set_rarity_order(self, guild_id, rarity_order):
        session = self.Session()
        for r_order, r_id in rarity_order.items():
            session.query(InventoryRarity).filter(db.and_(InventoryRarity.guild_id == guild_id,
                                                          InventoryRarity.id == r_id)).update(
                {InventoryRarity.order: r_order})
        session.commit()

    def remove_rarity(self, guild_id, rarity_id):
        session = self.Session()
        stmt = db.delete(InventoryRarity).where(db.and_(InventoryRarity.guild_id == guild_id,
                                                        InventoryRarity.id == rarity_id))
        session.execute(stmt)
        item_type_ids = session.query(InventoryItemType.id).filter(InventoryItemType.rarity_id == rarity_id).all()
        item_type_ids = list(map(lambda x: x[0], item_type_ids))
        stmt = db.delete(InventoryItemType).where(db.and_(InventoryItemType.guild_id == guild_id,
                                                          InventoryItemType.rarity_id == rarity_id))
        session.execute(stmt)
        stmt = db.delete(UserInventoryItem).where(db.and_(UserInventoryItem.guild_id == guild_id,
                                                          UserInventoryItem.item_type_id.in_(item_type_ids)))
        session.execute(stmt)
        stmt = db.delete(WheelspinProbability).where(db.and_(WheelspinProbability.guild_id == guild_id,
                                                             WheelspinProbability.item_type_id.in_(item_type_ids)))
        session.execute(stmt)
        stmt = db.delete(StoreItems).where(db.and_(StoreItems.guild_id == guild_id,
                                                   db.or_(StoreItems.from_item_id.in_(item_type_ids),
                                                          StoreItems.to_item_id.in_(item_type_ids)
                                                          )))
        session.execute(stmt)
        session.commit()

    def edit_inventory_item_type(self,
                                 guild_id,
                                 item_type_id,
                                 name,
                                 rarity_id,
                                 always_visible,
                                 tradable,
                                 equippable,
                                 useable,
                                 actions,
                                 ):
        session = self.Session()
        if item_type_id is not None:
            session.query(InventoryItemType).filter(db.and_(InventoryItemType.id == item_type_id,
                                                            InventoryItemType.guild_id == guild_id)).update(
                {
                    InventoryItemType.name: name,
                    InventoryItemType.rarity_id: rarity_id,
                    InventoryItemType.always_visible: always_visible,
                    InventoryItemType.tradable: tradable,
                    InventoryItemType.equippable: equippable,
                    InventoryItemType.useable: useable,
                    InventoryItemType.actions: actions,
                })
        else:
            session.add(InventoryItemType(guild_id=guild_id,
                                          id=item_type_id,
                                          name=name,
                                          rarity_id=rarity_id,
                                          always_visible=always_visible,
                                          tradable=tradable,
                                          equippable=equippable,
                                          useable=useable,
                                          actions=actions,
                                          ))
        session.commit()

    def get_item_types(self, guild_id):
        session = self.Session()
        stmt = db.select(InventoryItemType).where(InventoryItemType.guild_id == guild_id) \
            .join(InventoryRarity).order_by(InventoryRarity.order.asc())
        return session.scalars(stmt).all()

    def get_item_type_by_id(self, guild_id, item_type_id) -> InventoryItemType:
        session = self.Session()
        stmt = db.select(InventoryItemType).where(db.and_(InventoryItemType.guild_id == guild_id,
                                                          InventoryItemType.id == item_type_id))
        return session.scalars(stmt).first()

    def remove_item_type(self, guild_id, item_type_id):
        session = self.Session()
        stmt = db.delete(InventoryItemType).where(db.and_(InventoryItemType.guild_id == guild_id,
                                                          InventoryItemType.id == item_type_id))
        session.execute(stmt)
        stmt = db.delete(UserInventoryItem).where(db.and_(UserInventoryItem.guild_id == guild_id,
                                                          UserInventoryItem.item_type_id == item_type_id))
        session.execute(stmt)
        stmt = db.delete(WheelspinProbability).where(db.and_(WheelspinProbability.guild_id == guild_id,
                                                             WheelspinProbability.item_type_id == item_type_id))
        session.execute(stmt)
        stmt = db.delete(StoreItems).where(db.and_(StoreItems.guild_id == guild_id,
                                                   db.or_(StoreItems.from_item_id == item_type_id,
                                                          StoreItems.to_item_id == item_type_id
                                                          )))
        session.execute(stmt)
        session.commit()

    def get_user_item_amount(self, guild_id, user_id, item_type_id) -> float:
        session = self.Session()
        stmt = db.select(UserInventoryItem).where(db.and_(UserInventoryItem.guild_id == guild_id,
                                                          UserInventoryItem.user_id == user_id,
                                                          UserInventoryItem.item_type_id == item_type_id))
        res = session.scalars(stmt).first()
        if res is None:
            return 0
        return res.amount

    def add_user_item(self, guild_id, user_id, item_type_id, amount, equipped=False):
        amount += self.get_user_item_amount(guild_id, user_id, item_type_id)
        session = self.Session()
        session.merge(UserInventoryItem(guild_id=guild_id,
                                        user_id=user_id,
                                        item_type_id=item_type_id,
                                        amount=amount,
                                        equipped=equipped,
                                        ))
        session.commit()

    def equip_user_item(self, guild_id, user_id, item_type_id, equip):
        session = self.Session()
        session.query(UserInventoryItem).filter(db.and_(UserInventoryItem.guild_id == guild_id,
                                                        UserInventoryItem.user_id == user_id,
                                                        UserInventoryItem.item_type_id == item_type_id)).update(
            {
                UserInventoryItem.equipped: equip
            })
        session.commit()

    def get_user_items(self, guild_id, user_id):
        session = self.Session()
        query = session.query(
            UserInventoryItem, InventoryItemType, InventoryRarity
        ).join(InventoryItemType, UserInventoryItem.item_type) \
            .join(InventoryRarity, InventoryItemType.rarity) \
            .filter(
            db.and_(UserInventoryItem.guild_id == guild_id,
                    UserInventoryItem.user_id == user_id,
                    db.or_(
                        InventoryItemType.always_visible,
                        UserInventoryItem.amount != 0
                    ))
        ).order_by(InventoryRarity.order.asc())
        return query.all()

    def get_user_useable_items(self, guild_id, user_id):
        session = self.Session()
        query = session.query(
            UserInventoryItem, InventoryItemType, InventoryRarity
        ).join(InventoryItemType, UserInventoryItem.item_type) \
            .join(InventoryRarity, InventoryItemType.rarity) \
            .filter(
            db.and_(UserInventoryItem.guild_id == guild_id,
                    UserInventoryItem.user_id == user_id,
                    UserInventoryItem.amount >= 1,
                    InventoryItemType.useable >= 1,
                    InventoryItemType.equippable == db.false()
                    )
        ).order_by(InventoryRarity.order.asc())
        return query.all()

    def use_inventory_item(self, guild_id, user_id, item_type_id, amount):
        session = self.Session()
        query = session.query(
            UserInventoryItem, InventoryItemType
        ).join(InventoryItemType, UserInventoryItem.item_type) \
            .filter(
            db.and_(UserInventoryItem.guild_id == guild_id,
                    UserInventoryItem.user_id == user_id,
                    InventoryItemType.id == item_type_id,
                    UserInventoryItem.amount >= amount,
                    db.or_(
                        InventoryItemType.useable == -1,
                        InventoryItemType.useable >= 1,
                    )
                    )
        )
        res = query.first()
        if res is None:
            return False, None
        if res.InventoryItemType.useable != 2:
            self.add_user_item(guild_id, user_id, item_type_id, -amount)

        if res.InventoryItemType.equippable:
            res.UserInventoryItem.equipped = not res.UserInventoryItem.equipped
            self.equip_user_item(guild_id, user_id, item_type_id, res.UserInventoryItem.equipped)

        return True, res

    def get_user_equippable_items(self, guild_id, user_id):
        session = self.Session()
        query = session.query(
            UserInventoryItem, InventoryItemType, InventoryRarity
        ).join(InventoryItemType, UserInventoryItem.item_type) \
            .join(InventoryRarity, InventoryItemType.rarity) \
            .filter(
            db.and_(UserInventoryItem.guild_id == guild_id,
                    UserInventoryItem.user_id == user_id,
                    UserInventoryItem.amount >= 1,
                    UserInventoryItem.equipped == db.false(),
                    InventoryItemType.useable >= 1,
                    InventoryItemType.equippable == db.true()
                    )
        ).order_by(InventoryRarity.order.asc())
        return query.all()

    def get_user_equipped_items(self, guild_id, user_id):
        session = self.Session()
        query = session.query(
            UserInventoryItem, InventoryItemType, InventoryRarity
        ).join(InventoryItemType, UserInventoryItem.item_type) \
            .join(InventoryRarity, InventoryItemType.rarity) \
            .filter(
            db.and_(UserInventoryItem.guild_id == guild_id,
                    UserInventoryItem.user_id == user_id,
                    UserInventoryItem.amount >= 1,
                    UserInventoryItem.equipped == db.true(),
                    InventoryItemType.useable >= 1,
                    InventoryItemType.equippable == db.true()
                    )
        ).order_by(InventoryRarity.order.asc())
        return query.all()

    def get_user_equipped_items_by_action(self, guild_id, user_id, action):
        session = self.Session()
        query = session.query(
            UserInventoryItem, InventoryItemType, InventoryRarity
        ).join(InventoryItemType, UserInventoryItem.item_type) \
            .join(InventoryRarity, InventoryItemType.rarity) \
            .filter(
            db.and_(UserInventoryItem.guild_id == guild_id,
                    UserInventoryItem.user_id == user_id,
                    UserInventoryItem.amount >= 1,
                    UserInventoryItem.equipped == db.true(),
                    InventoryItemType.actions.contains(f"\"action\": \"{action}\""),
                    InventoryItemType.useable >= 1,
                    InventoryItemType.equippable == db.true()
                    )
        ).order_by(InventoryRarity.order.asc())
        return query.all()

    def get_wheelspin(self, guild_id):
        session = self.Session()
        query = session.query(WheelspinProbability, InventoryItemType, InventoryRarity) \
            .join(InventoryItemType, WheelspinProbability.item_type) \
            .join(InventoryRarity, InventoryItemType.rarity) \
            .where(WheelspinProbability.guild_id == guild_id)
        return query.all()

    def set_wheelspin(self, guild_id, wheelspin):
        session = self.Session()
        stmt = db.delete(WheelspinProbability).where(WheelspinProbability.guild_id == guild_id)
        session.execute(stmt)
        objects = list(map(lambda x: WheelspinProbability(guild_id=guild_id,
                                                          item_type_id=x['item_type_id'],
                                                          probability=x['probability'],
                                                          amount=x['amount'],
                                                          sound=x['sound']), wheelspin))
        session.bulk_save_objects(objects)
        session.commit()

    def get_wheelspin_available(self, guild_id, user_id) -> WheelspinAvailable:
        session = self.Session()
        stmt = db.select(WheelspinAvailable).where(db.and_(WheelspinAvailable.guild_id == guild_id,
                                                           WheelspinAvailable.user_id == user_id))
        return session.scalars(stmt).first()

    def set_wheelspin_available(self, guild_id, user_id, amount, last_free):
        session = self.Session()
        session.merge(WheelspinAvailable(guild_id=guild_id, user_id=user_id, amount=amount, last_free=last_free))
        session.commit()

    def set_store(self, guild_id, store):
        session = self.Session()
        stmt = db.delete(StoreItems).where(StoreItems.guild_id == guild_id)
        session.execute(stmt)
        objects = list(map(lambda x: StoreItems(guild_id=guild_id,
                                                from_item_id=x['from_item_id'],
                                                from_item_amount=x['from_item_amount'],
                                                to_item_id=x['to_item_id'],
                                                to_item_amount=x['to_item_amount']
                                                ), store))
        session.bulk_save_objects(objects)
        session.commit()

    def get_store(self, guild_id):
        from_item_type = aliased(InventoryItemType)
        from_item_rarity = aliased(InventoryRarity)
        to_item_type = aliased(InventoryItemType)
        to_item_rarity = aliased(InventoryRarity)
        session = self.Session()
        query = session.query(StoreItems,
                              from_item_type,
                              from_item_rarity,
                              to_item_type,
                              to_item_rarity) \
            .where(StoreItems.guild_id == guild_id) \
            .join(from_item_type, from_item_type.id == StoreItems.from_item_id) \
            .join(from_item_rarity, from_item_rarity.id == from_item_type.rarity_id) \
            .join(to_item_type, to_item_type.id == StoreItems.to_item_id) \
            .join(to_item_rarity, to_item_rarity.id == to_item_type.rarity_id)
        return query.all()

    def get_offer(self, guild_id, offer_id) -> StoreItems:
        session = self.Session()
        stmt = db.select(StoreItems).where(db.and_(StoreItems.guild_id == guild_id, StoreItems.id == offer_id))
        return session.scalars(stmt).first()
