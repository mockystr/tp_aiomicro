import asyncio
import time
from my_models import User, Man
from utils import current_loop
import datetime


async def main():
    # user = await Man.objects.get(id=28)
    # print(user.__dict__)
    # user.name = 'asd12'
    # print(user.__dict__)
    # await user.save()

    # man = await User.objects.create(name='as\'d', description='perfect gamer. registered in 2010',
    #                                 date_added=[2010, 12, 12], age=18,
    #                                 coins=322, is_superuser=False)
    # print(man.__dict__)
    # await man.save()
    # man.date_added = {'year': 2012, 'month': 10, 'day': 5}
    # await man.save()

    # man = Man(description='perfect gamer. registered in 2010',
    #           date_added=datetime.datetime.now(), age=18,
    #           coins=322, is_superuser=False,
    #           sex='male')
    # man.name = 'mockystr'
    # await man.save()
    # man.date_added = None
    # await man.save()
    # print(man.__dict__)

    # print([i.age async for i in await User.objects.all()])

    # users = await User.objects.all()
    # print(users.__dict__)

    # print([(i.id, i.name, i.age, i.coins) async for i in
    #        await (await (await User.objects.filter())[:10]).order_by('-age')])

    # [print('', (i.name, i.age, i.coins)) async for i in
    #  await (await User.objects.filter(name='abe')).order_by('-coins', 'age')]

    # p = await (await (await User.objects.filter(name__startswith='e'))[:20]).order_by('-name')
    # print([i async for i in p])
    # print(await p.count())

    # print([i async for i in
    #        await (await (await (await User.objects.all()).filter(name__startswith='e'))[:20])
    #       .order_by('-name', 'description')])

    # res = await (await (await User.objects.all()).order_by('-name')).filter(name__startswith='a')
    # print([i async for i in res])
    # print(await res[5])

    # user_obj = await User.objects.get(name='new_edit_after_get', id=2538)
    # print(user_obj.__dict__)
    # user_obj.name = 'new_edit_after_get'
    # await user_obj.save()

    # print([i async for i in await User.objects.filter(name__in='ef')])
    # print([i async for i in await User.objects.filter(id__le=2500)])

    # qs = await (await (await User.objects.filter(name__endswith='g')).filter(id__le=2505))[:20]
    # print(qs.__dict__)
    # print([i async for i in qs])
    # print(await qs.count())

    # user_obj = await User.objects.create(name='emir_name', age=150, date_added=datetime.datetime.now(),
    #                                      description='im',
    #                                      coins=123.3)
    # await user_obj.delete()

    # user = User(name='i', date_added={'year': 2010, 'day': 10, 'month': 10})
    # await user.save()
    # user.date_added = [2010, 12, 12]
    # await user.save()
    # print(user.__dict__)

    # update_int = await (
    #     await (await (await User.objects.filter(name__startswith='3', age__ge=0)).order_by('name'))[:5]).update(
    #     description='new52')
    # print(update_int)

    # delete_int = await (await(await(await User.objects.filter(name__startswith='a')).order_by('-name'))[:7]).delete()
    # print(delete_int)
    # print([i async for i in await (await(await User.objects.filter(name__startswith='a')).order_by('-name'))[:7]])

    """sql injections check"""
    # print([i.name async for i in await User.objects.filter(name__startswith='\'a')])
    # SELECT * FROM "ormtable" WHERE "name" LIKE '''a%' ESCAPE '\' ORDER BY "name" NULLS FIRST

    # print([i async for i in await User.objects.filter(name='\' or 1=1')])
    # SELECT * FROM "ormtable" WHERE "name"=''' or 1=1' ORDER BY "name" NULLS FIRST

    # print([i async for i in await User.objects.filter(name="'")])
    # SELECT * FROM "ormtable" WHERE "name"='''' ORDER BY "name" NULLS FIRST

    # print([i async for i in await (await User.objects.filter(name="'")).order_by('name', '-description \' or 1=1')])
    # exceptions.OrderByFieldError: ordering refers to the nonexistent fields: name, description ' or 1=1

    # print([i async for i in await User.objects.filter(age__lt='5\' or 1=1')])
    # LINE 1: SELECT * FROM "ormtable" WHERE "age" < '5'' or 1=1' ORDER BY...

    # print([i async for i in await User.objects.filter(name__in=['a', ')\' SELECT * from ormtable;'])])
    # SELECT * FROM "ormtable" WHERE "name" IN ('a', ')'' SELECT * from ormtable;') ORDER BY "name" NULLS FIRST

    # print([i async for i in await User.objects.filter(name__contains='a %\' or 1=1')])
    # SELECT * FROM "ormtable" WHERE "name" LIKE '%a %'' or 1=1%' ESCAPE '\' ORDER BY "name" NULLS FIRST

    # user = await User.objects.create(name='0\');\nDELETE from ormtable where id=2600; --')
    # print(user.id)

    # print(await (await User.objects.filter(name="1\'", age__ge=0)).update(name='injection'))
    # UPDATE "ormtable" SET "name"='injection' WHERE id IN (SELECT id FROM "ormtable"
    # WHERE "name"='1''' AND "age" >= '0' ORDER BY "name" NULLS FIRST )

    # user = User(name='name\'')
    # user.asd = 'asd'
    # await user.save()
    # user.name = 'asd\'); select * from ormtable;'
    # await user.save()
    # user.id = '1'
    # await user.delete()


if __name__ == '__main__':
    current_loop.run_until_complete(main())
