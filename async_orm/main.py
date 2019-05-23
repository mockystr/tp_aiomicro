import asyncio
import time
from my_models import User
from utils import current_loop

async def main():
    # u = User()
    # u.name = "Emir"
    print(await User.objects.get(name=1))


if __name__ == '__main__':
    current_loop.run_until_complete(main())
