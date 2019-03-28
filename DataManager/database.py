# -*- coding utf-8 -*-
import datetime
from peewee import *

DbName = 'DataBase.db'
database = SqliteDatabase(DbName, **{})


class BaseModel(Model):
    class Meta:
        database = database

    @classmethod
    def get_by_name(cls, name: str):
        return cls.select().where(cls.name == name).first()

    @classmethod
    def create_or_get(cls, **kwargs):
        try:
            with cls._meta.database.atomic():
                return cls.create(**kwargs), True
        except IntegrityError:
            query = []
            for field_name, value in kwargs.items():
                field = getattr(cls, field_name)
                if field.unique or field.primary_key:
                    query.append(field == value)
            return cls.get(*query), False


class Message(BaseModel):
    id = PrimaryKeyField(primary_key=True, unique=True)  # IDENTITY
    time = DateTimeField()
    type = CharField()
    clientId = CharField(null=True)
    content = CharField()
    html = CharField()
    edited = BooleanField(default=False)
    sended = BooleanField(default=False)

    class Meta:
        db_table = 'Messages'

    @classmethod
    def get_or_create_message(cls, message):
        return cls.create_or_get(id=message.id,
                                 time=message.time,
                                 type=message.type,
                                 clientId=message.clientId,
                                 content=message.content,
                                 html=message.html, )


def init_tables():
    database.connect()
    database.create_tables([Message], safe=True)


init_tables()
