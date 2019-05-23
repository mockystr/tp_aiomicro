from model import Model
from fields import (StringField, IntField, DateField,
                    FloatField, BooleanField)


class User(Model):
    name = StringField(required=True)
    description = StringField()
    date_added = DateField()
    age = IntField()
    coins = FloatField()
    is_superuser = BooleanField()

    def __str__(self):
        return 'User {}'.format(self.name, self.age)

    def __repr__(self):
        return '<User {}>'.format(self.name, self.age)

    def update(self):
        pass

    class Meta:
        table_name = 'ormtable'
        order_by = ('name',)


class Man(User):
    sex = StringField()

    class Meta:
        table_name = 'Man'
        order_by = ('-name', 'coins', 'sex')
