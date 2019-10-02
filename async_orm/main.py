from async_orm.models import User, Token, CrawlerStats
from async_orm.utils import current_loop

async def main():
    await User.objects.create(email='navruzov.e', password='asdasd123')
    await User.objects.filter().delete()

    print('SUCCESSFULLY CONFIGURED ORM')


if __name__ == '__main__':
    current_loop.run_until_complete(main())
