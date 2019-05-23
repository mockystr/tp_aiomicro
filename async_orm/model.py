import asyncio
import asyncpg
import psycopg2
from psycopg2 import sql
from utils import current_loop
from fields import Field
from exceptions import (MultipleObjectsReturned,
                        DoesNotExist,
                        DeleteError,
                        OrderByFieldError,
                        IntegrityError,
                        ParentClashError,
                        FieldLookupError)
from db_settings import (user_db_constant,
                         password_db_constant,
                         host_db_constant,
                         database_db_constant,
                         port_db_constant)


async def create_conn_cur():
    return await asyncpg.create_pool(user=user_db_constant,
                                     password=password_db_constant,
                                     host=host_db_constant,
                                     database=database_db_constant)


conn_pool = current_loop.run_until_complete(create_conn_cur())
psycopg_conn = psycopg2.connect(user=user_db_constant,
                                password=password_db_constant,
                                host=host_db_constant,
                                port=port_db_constant,
                                database=database_db_constant)


class ModelMeta(type):
    def __new__(mcs, name, bases, namespace):
        if name == 'Model':
            return super().__new__(mcs, name, bases, namespace)

        meta = namespace.get('Meta')
        if meta is None:
            raise ValueError('meta is none')

        if hasattr(meta, 'table_name'):
            namespace['_table_name'] = meta.table_name
        else:
            namespace['_table_name'] = name

        # todo create table from shell

        if len(bases) > 1:
            raise ParentClashError("You can't inherit more than one table!")

        if bases[0] != Model:
            fields = {k: v for k, v in [*namespace.items(), *bases[0]._fields.items()]
                      if isinstance(v, Field)}
        else:
            fields = {k: v for k, v in namespace.items()
                      if isinstance(v, Field)}

        if hasattr(meta, 'order_by'):
            if isinstance(meta.order_by, (tuple, list)):
                stripped_order = [i.strip('-') for i in meta.order_by]
            else:
                raise ValueError("ordering can be only tuple or list object")

            if not set(stripped_order).issubset(fields.keys()):
                raise OrderByFieldError(
                    'ordering refers to the nonexistent field \'{}\''.format(stripped_order))

        # print(name, fields)
        namespace['_fields'] = fields
        namespace['_order_by'] = getattr(meta, 'order_by', None)
        return super().__new__(mcs, name, bases, namespace)


class Condition:
    def __init__(self, cond, owner_class):
        self._conditions = ['exact', 'in', 'lt', 'gt', 'le', 'ge', 'contains', 'startswith', 'endswith']
        self.field_name, self.cond, self.value = self.from_string(cond, owner_class)

    @staticmethod
    def quote_replace(string):
        return str(string).replace('\'', '\'\'')

    @staticmethod
    def check_fields(cond, owner_class):
        # print(cond)
        condspl = cond[0].split('__')

        if condspl[0] not in ['id', *owner_class._fields.keys()]:
            raise LookupError("Cannot resolve keyword '{}' into field. Choices are: {}".
                              format(condspl[0], ', '.join(owner_class._fields.keys())))

        return condspl

    @staticmethod
    def from_string(cond, owner_class):
        condspl = Condition.check_fields(cond, owner_class)

        if len(condspl) == 2:
            return str(condspl[0]), str(condspl[1]), cond[1]
        elif len(condspl) == 1:
            return str(condspl[0]), 'exact', cond[1]
        else:
            raise LookupError("unresolved lookup {}".format(cond))

    def format_cond(self):
        if self.cond in self._conditions:
            like_value = str(self.value).replace('\'', '\'\'')
            if self.cond == 'exact':
                return sql.SQL("{}={}").format(sql.Identifier(self.field_name),
                                               sql.Literal(str(self.value))).as_string(psycopg_conn)
            elif self.cond == 'in':
                print(self.value)
                print(tuple(self.value))
                tmp_compose = sql.Composed(sql.SQL(', ').join([sql.Literal(i) for i in tuple(self.value)]))
                print(tmp_compose)
                return sql.SQL("{} IN ({})").format(sql.Identifier(self.field_name),
                                                    tmp_compose).as_string(psycopg_conn)
            elif self.cond == 'lt':
                return sql.SQL("{} < {}").format(sql.Identifier(self.field_name),
                                                 sql.Literal(str(self.value))).as_string(psycopg_conn)
            elif self.cond == 'gt':
                return sql.SQL("{} > {}").format(sql.Identifier(self.field_name),
                                                 sql.Literal(str(self.value))).as_string(psycopg_conn)
            elif self.cond == 'le':
                return sql.SQL("{} <= {}").format(sql.Identifier(self.field_name),
                                                  sql.Literal(str(self.value))).as_string(psycopg_conn)
            elif self.cond == 'ge':
                return sql.SQL("{} >= {}").format(sql.Identifier(self.field_name),
                                                  sql.Literal(str(self.value))).as_string(psycopg_conn)
            elif self.cond == 'contains':
                return sql.SQL("{} LIKE '%{}%' ESCAPE '\\'").format(sql.Identifier(self.field_name),
                                                                    sql.SQL(like_value)).as_string(psycopg_conn)
            elif self.cond == 'startswith':
                return sql.SQL("{} LIKE '{}%' ESCAPE '\\'").format(sql.Identifier(self.field_name),
                                                                   sql.SQL(like_value)).as_string(psycopg_conn)
            elif self.cond == 'endswith':
                return sql.SQL("{} LIKE '%{}' ESCAPE '\\'").format(sql.Identifier(self.field_name),
                                                                   sql.SQL(like_value)).as_string(psycopg_conn)
            else:
                raise LookupError("Unsupported lookup '{}' for {} column.".format(self.cond, self.field_name))


class Manage:
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        if self.model_cls is None:
            self.model_cls = owner
        return self

    # def all(self):
    #
    # def filter(self, *_, **kwargs):
    #

    async def get(self, *_, **kwargs):
        if not kwargs:
            raise ValueError("you should write params")

        where_list = []
        for i in kwargs.items():
            where_list.append(Condition(i, self.model_cls).format_cond())

        select_get_query = sql.SQL("SELECT * FROM {} WHERE {};").format(
            sql.Identifier(str(self.model_cls._table_name).lower()),
            sql.SQL(' AND ').join([sql.SQL(i) for i in where_list]))

        con = await conn_pool.acquire()
        res = await con.fetch(select_get_query.as_string(psycopg_conn))

        if len(res) > 1:
            raise MultipleObjectsReturned('get() returned more than one {} -- it returned {}!'.
                                          format(self.model_cls._table_name, len(res)))
        elif len(res) == 0:
            raise DoesNotExist('{} matching query does not exist.'.
                               format(self.model_cls._table_name))
        else:
            res_d = dict(zip(res[0].keys(), res[0]))

        await conn_pool.release(con)
        return self.model_cls(**res_d)


class Model(metaclass=ModelMeta):
    def __init__(self, *_, **kwargs):
        setattr(self, 'id', kwargs.get('id'))
        for field_name, field in self._fields.items():
            value = field.validate(kwargs.get(field_name))
            setattr(self, field_name, value)

    objects = Manage()

    class Meta:
        table_name = ''
