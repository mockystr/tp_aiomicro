import psycopg2
from psycopg2 import sql
from psycopg2 import _ext
from fields import Field
from exceptions import (MultipleObjectsReturned,
                        DoesNotExist,
                        DeleteError,
                        DuplicateKeyConstraint,
                        OrderByFieldError,
                        IntegrityError,
                        ParentClashError,
                        LookupError)
from constants import (user_db_constant,
                       password_db_constant,
                       host_db_constant,
                       port_db_constant,
                       database_db_constant)

connection = psycopg2.connect(user=user_db_constant,
                              password=password_db_constant,
                              host=host_db_constant,
                              port=port_db_constant,
                              database=database_db_constant)
cursor = connection.cursor()


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

        # if isinstance(cond[1], str):
        #     tmp_value = Condition.quote_replace(cond[1])
        # elif isinstance(cond[1], (list, tuple)):
        #     tmp_value = [Condition.quote_replace(str(i)) for i in cond[1]]
        # else:
        #     tmp_value = cond[1]

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
                                               sql.Literal(str(self.value))).as_string(cursor)
            elif self.cond == 'in':
                print(self.value)
                print(tuple(self.value))
                # print([sql.Literal(i) for i in self.value])
                tmp_compose = sql.Composed(sql.SQL(', ').join([sql.Literal(i) for i in tuple(self.value)]))
                print(tmp_compose)
                return sql.SQL("{} IN ({})").format(sql.Identifier(self.field_name),
                                                    tmp_compose).as_string(cursor)
            elif self.cond == 'lt':
                return sql.SQL("{} < {}").format(sql.Identifier(self.field_name),
                                                 sql.Literal(str(self.value))).as_string(cursor)
            elif self.cond == 'gt':
                return sql.SQL("{} > {}").format(sql.Identifier(self.field_name),
                                                 sql.Literal(str(self.value))).as_string(cursor)
            elif self.cond == 'le':
                return sql.SQL("{} <= {}").format(sql.Identifier(self.field_name),
                                                  sql.Literal(str(self.value))).as_string(cursor)
            elif self.cond == 'ge':
                return sql.SQL("{} >= {}").format(sql.Identifier(self.field_name),
                                                  sql.Literal(str(self.value))).as_string(cursor)
            elif self.cond == 'contains':
                return sql.SQL("{} LIKE '%{}%' ESCAPE '\\'").format(sql.Identifier(self.field_name),
                                                                    sql.SQL(like_value)).as_string(cursor)
            elif self.cond == 'startswith':
                return sql.SQL("{} LIKE '{}%' ESCAPE '\\'").format(sql.Identifier(self.field_name),
                                                                   sql.SQL(like_value)).as_string(cursor)
            elif self.cond == 'endswith':
                return sql.SQL("{} LIKE '%{}' ESCAPE '\\'").format(sql.Identifier(self.field_name),
                                                                   sql.SQL(like_value)).as_string(cursor)
            else:
                raise LookupError("Unsupported lookup '{}' for {} column.".format(self.cond, self.field_name))


class QuerySet:
    def __init__(self, model_cls, where=None, limit=None, order_by=None, res=None):
        self.model_cls = model_cls
        self.fields = self.model_cls._fields
        self.where: dict = where
        self.res = res
        self.limit = limit
        self.__cache = {'count': -1, 'order_by': 0}

        if order_by is not None and isinstance(order_by, (list, tuple)):
            self._order_by: list = order_by
        elif hasattr(self.model_cls, '_order_by'):
            if isinstance(self.model_cls._order_by, (list, tuple)):
                self._order_by: list = self.model_cls._order_by
        elif order_by is not None:
            raise ValueError("ordering can be only tuple or list object")
        else:
            self._order_by = None

    def format_where(self):
        if self.where:
            where_list = []
            for i in self.where.items():
                where_list.append(Condition(i, self.model_cls).format_cond())
            return where_list
        return None

    def format_limit(self):
        if self.limit is not None:
            limit_list = []

            if isinstance(self.limit, slice):
                if self.limit.start:
                    limit_list.extend([sql.SQL('OFFSET'), sql.SQL(str(self.limit.start))])
                if self.limit.stop:
                    limit_list.extend([sql.SQL('LIMIT'), sql.SQL(str(self.limit.stop - (self.limit.start or 0)))])
                return limit_list
            elif isinstance(self.limit, int):
                limit_list.extend([sql.SQL('OFFSET'), sql.SQL(str(self.limit)), sql.SQL('LIMIT'), sql.SQL('1')])
                return limit_list
            else:
                raise TypeError('unsupported type of limit index')
        return None

    def format_order_list(self):
        if self._order_by:
            formatted_order = []

            for i in self._order_by:
                if i.startswith('-'):
                    formatted_order.append(
                        sql.SQL("{} DESC NULLS LAST").format(sql.Identifier(i.strip('-'))))
                else:
                    formatted_order.append(
                        sql.SQL("{} NULLS FIRST").format(sql.Identifier(i.strip('-'))))
            return formatted_order
        return None

    def slice_processing(self, key):
        if key.step:
            raise ValueError("you cant set step to slice")

        if self.limit is not None:
            if key.stop:
                if self.limit.stop:
                    max_start = max(self.limit.start or 0, key.start or 0)
                    min_stop = min(self.limit.stop, key.stop)
                    if max_start < min_stop:
                        self.limit = slice(max_start,
                                           min_stop,
                                           None)
                    else:
                        self.limit = slice((self.limit.start or 0) + (key.start or 0),
                                           min(self.limit.stop,
                                               (self.limit.start or 0) + key.stop),
                                           None)
                else:
                    self.limit = slice(max(self.limit.start or 0, key.start or 0), key.stop, None)
            else:
                self.limit = slice(max(self.limit.start or 0, key.start or 0), getattr(self.limit, 'stop'), None)
        else:
            self.limit = key

    def filter(self, *_, **kwargs):
        """Get rows that are suitable for condition"""
        if kwargs:
            [Condition.check_fields(i, self.model_cls) for i in kwargs.items()]

        if self.where and kwargs:
            self.where = {**self.where, **kwargs}
        else:
            self.where = kwargs
        return self

    def __getitem__(self, key):
        if isinstance(key, int):
            self.limit = key
            return self._build()
        elif isinstance(key, slice):
            self.slice_processing(key)
            return self
        else:
            raise TypeError('wrong index')

    def order_by(self, *args):
        if isinstance(args, (tuple, list)):
            stripped_order = [i.strip('-') for i in args]
            if not set(stripped_order).issubset(self.fields.keys()):
                raise OrderByFieldError('ordering refers to the nonexistent fields: {}'.
                                        format(', '.join(stripped_order)))
        else:
            raise ValueError("ordering can be only tuple or list object")

        if self._order_by is not None:
            if self.__cache['order_by'] == 0:
                self._order_by = args
                self.__cache['order_by'] = 1
            else:
                self._order_by = [*self._order_by, *args]
        else:
            self._order_by = args
        return self

    def reverse(self):
        if self.res is not None:
            if isinstance(self.res, list):
                self.res.reverse()
        return self

    def update(self, *_, **kwargs):
        if not kwargs:
            raise ValueError("you shoud write params")

        [Condition.check_fields(i, self.model_cls) for i in kwargs.items()]

        query = [sql.SQL('UPDATE {}').format(sql.Identifier(str(self.model_cls._table_name).lower())), sql.SQL('SET'),
                 sql.SQL(', ').join(
                     [sql.SQL("{}={}").format(sql.Identifier(i[0]), sql.Literal(i[1])) for i in kwargs.items()])]
        if self.where:
            sql_where = [sql.SQL(i) for i in self.format_where()]
            query.extend([sql.SQL('WHERE'),
                          sql.SQL('id IN (SELECT id FROM {} WHERE').format(
                              sql.Identifier(str(self.model_cls._table_name).lower())),
                          sql.SQL(' AND ').join(sql_where)])
        if self._order_by:
            query.extend([sql.SQL("ORDER BY"), sql.SQL(", ").join(self.format_order_list())])
        if self.limit:
            query.extend(self.format_limit())
        query.append(sql.SQL(')'))

        print(' '.join([i.as_string(connection) for i in query]))
        cursor.execute(' '.join([i.as_string(connection) for i in query]))
        connection.commit()
        return cursor.statusmessage.split()[1]

    def delete(self):
        query = [sql.SQL('DELETE FROM {0} WHERE ctid in (SELECT ctid FROM {0}').format(
            sql.Identifier(str(self.model_cls._table_name).lower()))]
        if self.where:
            query.extend([sql.SQL('WHERE'), sql.SQL(' AND ').join([sql.SQL(i) for i in self.format_where()])])
        if self._order_by is not None:
            query.extend([sql.SQL("ORDER BY"), sql.SQL(", ").join(self.format_order_list())])
        if self.limit:
            query.extend(self.format_limit())
        query.append(sql.SQL(')'))
        # print(' '.join([i.as_string(connection) for i in query]))
        cursor.execute(' '.join([i.as_string(connection) for i in query]))
        # connection.commit()
        return cursor.statusmessage.split()[1]

    def count(self):
        if 'count' in self.__cache.keys() and self.__cache['count'] != -1:
            return self.__cache['count']
        return self._count_perform()

    def _count_perform(self):
        if self.res is not None:
            res_len = len(self.res)
            self.__cache['count'] = res_len
            return res_len

        query = [sql.SQL('SELECT count(*) FROM (SELECT * FROM {}').format(
            sql.Identifier(str(self.model_cls._table_name).lower()))]

        if self.where:
            query.extend([sql.SQL('WHERE'), sql.SQL(' AND ').join([sql.SQL(i) for i in self.format_where()])])
        if self.limit:
            query.extend(self.format_limit())

        query.append(sql.SQL(') as tmp_table'))
        print(' '.join([i.as_string(connection) for i in query]))
        cursor.execute(' '.join([i.as_string(connection) for i in query]))
        res_len = cursor.fetchone()[0]
        self.__cache['count'] = res_len
        return res_len

    def _build(self):
        if self.where:
            [Condition.check_fields(i, self.model_cls) for i in self.where.items()]

        query = [sql.SQL("SELECT *")]
        query.extend([sql.SQL("FROM"), sql.Identifier(str(self.model_cls._table_name).lower())])

        if self.where:
            query.extend([sql.SQL("WHERE"), sql.SQL(" AND ").join([sql.SQL(i) for i in self.format_where()])])
        if self._order_by:
            query.extend([sql.SQL("ORDER BY"), sql.SQL(", ").join(self.format_order_list())])
        if self.limit:
            query.extend(self.format_limit())

        # print('BUILD QUERY', query)
        print(' '.join([i.as_string(connection) for i in query]))

        cursor.execute(' '.join([i.as_string(connection) for i in query]))
        res = cursor.fetchall()

        if isinstance(self.limit, int):
            return self.model_cls(**dict(zip([i.name for i in cursor.description], res[0])))

        self.res = [self.model_cls(**dict(zip([ii.name for ii in cursor.description], res[i]))) for i in
                    range(len(res))]

    def __str__(self):
        return '<QuerySet of {}>'.format(self.model_cls._table_name)

    def __iter__(self):
        if self.res is None:
            self._build()

        return iter(self.res)


class Manage:
    def __init__(self):
        self.model_cls = None

    def __get__(self, instance, owner):
        if self.model_cls is None:
            self.model_cls = owner
        return self

    def all(self):
        """Get all rows from table"""
        return QuerySet(self.model_cls)

    def filter(self, *_, **kwargs):
        """Get rows that are suitable for condition"""
        [Condition.check_fields(i, self.model_cls) for i in kwargs.items()]
        return QuerySet(self.model_cls, kwargs)

    def get(self, *_, **kwargs):
        """Get only one object"""
        if not kwargs:
            raise ValueError("you should write params")

        where_list = []
        for i in kwargs.items():
            where_list.append(Condition(i, self.model_cls).format_cond())

        select_get_query = sql.SQL("SELECT * FROM {} WHERE {};").format(
            sql.Identifier(str(self.model_cls._table_name).lower()),
            sql.SQL(' AND ').join([sql.SQL(i) for i in where_list]))

        print(select_get_query.as_string(connection))
        cursor.execute(select_get_query.as_string(connection))
        res = cursor.fetchall()

        if len(res) > 1:
            raise MultipleObjectsReturned('get() returned more than one {} -- it returned {}!'.
                                          format(self.model_cls._table_name, len(res)))
        elif len(res) == 0:
            raise DoesNotExist('{} matching query does not exist.'.
                               format(self.model_cls._table_name))
        else:
            res_d = dict(zip([i.name for i in cursor.description], res[0]))
        return self.model_cls(**res_d)

    def create(self, *_, **kwargs):
        """Create object"""
        if not kwargs:
            raise IntegrityError("no parameters to create")

        for field_name, field in self.model_cls._fields.items():
            if (getattr(self.model_cls, field_name) is None or getattr(self.model_cls,
                                                                       field_name) == "None") and field.required:
                raise IntegrityError('NOT NULL constraint failed: {} in {} column'
                                     .format(getattr(self.model_cls, field_name), field_name))
        edited_kw = {}
        for field_name, field in kwargs.items():
            value = getattr(self.model_cls, field_name).validate(kwargs.get(field_name))
            edited_kw[field_name] = value

        insert_query = sql.SQL("INSERT INTO {0} ({1}) VALUES ({2}) RETURNING *;").format(
            sql.Identifier(str(self.model_cls._table_name).lower()),
            sql.SQL(', ').join([sql.Identifier(i) for i in edited_kw.keys()]),
            sql.SQL(', ').join([sql.Literal(i) for i in edited_kw.values()]))

        print(insert_query.as_string(connection))
        cursor.execute(insert_query.as_string(connection))
        res = dict(zip([i.name for i in cursor.description], cursor.fetchone()))
        connection.commit()
        return self.model_cls(**res)


class Model(metaclass=ModelMeta):
    def __init__(self, *_, **kwargs):
        setattr(self, 'id', kwargs.get('id'))
        for field_name, field in self._fields.items():
            value = field.validate(kwargs.get(field_name))
            setattr(self, field_name, value)

    objects = Manage()

    def check_fields(self):
        """Return exception if required field is none"""
        for field_name, field in self._fields.items():
            if (getattr(self, field_name) is None or getattr(self, field_name) == "None") and field.required:
                raise IntegrityError(
                    'NOT NULL constraint failed: {} in {} column'.format(getattr(self, field_name),
                                                                         field_name))

    def delete(self):
        """Delete object"""
        if self.id is None:
            raise DeleteError('{} object can\'t be deleted because its id attribute is set to None.'.
                              format(self._table_name))
        try:
            delete_query = sql.SQL("DELETE FROM {} WHERE id={}").format(sql.Identifier(str(self._table_name).lower()),
                                                                        sql.Literal(self.id))
            print(delete_query.as_string(connection))
            cursor.execute(delete_query.as_string(connection))
            connection.commit()
        except Exception:
            raise DeleteError('{} object can\'t be deleted because its id is incorrect.'.
                              format(self._table_name))

    def save(self):
        """Update if exists in db or create if not"""
        for field_name, field in self._fields.items():
            value = field.validate(getattr(self, field_name))
            setattr(self, field_name, value)

        object_fields = ['id', *list(self._fields.keys())]
        self.check_fields()

        if self.__dict__.get('id') is not None:
            set_arr = []
            for i in object_fields:
                attr_value = getattr(self, i)

                if attr_value is None:
                    set_arr.append(sql.SQL("{}=null").format(sql.Identifier(i)))
                else:
                    set_arr.append(sql.SQL("{}={}").format(sql.Identifier(i), sql.Literal(attr_value)))

            update_query = sql.SQL("UPDATE {} SET {} WHERE id={}").format(sql.Identifier(str(self._table_name).lower()),
                                                                          sql.SQL(', ').join(set_arr),
                                                                          sql.Literal(self.id))
            print(update_query.as_string(connection))
            cursor.execute(update_query.as_string(connection))
            connection.commit()
        else:
            values = []
            for i in object_fields:
                if getattr(self, i) is not None:
                    values.append(sql.SQL("{}").format(sql.Literal(getattr(self, i))))
                else:
                    if i == 'id':
                        values.append(sql.SQL('DEFAULT'))
                    else:
                        values.append(sql.SQL("null"))

            insert_query = sql.SQL("INSERT INTO {0} ({1}) VALUES ({2}) RETURNING id;").format(
                sql.Identifier(str(self._table_name).lower()),
                sql.SQL(', ').join([sql.Identifier(i) for i in object_fields]),
                sql.SQL(', ').join(values))

            print(insert_query.as_string(connection))
            cursor.execute(insert_query.as_string(connection))
            self.id = cursor.fetchone()[0]
            connection.commit()

    class Meta:
        table_name = ''
