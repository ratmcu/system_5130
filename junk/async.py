import asyncio
import time

async def say_after(delay, what, index, tail):
    await asyncio.sleep(delay[index])
    print(f'{what} from {delay[index]}')
    delay[index] = delay[index] + 1
    tail.append(index)

async def main():
    print(f"started at {time.strftime('%X')}")
    val = [1,2,3,4,5]
    print(f"{val}")
    tail = []
    fl = [say_after(val, 'hello', i, tail) for i in range(5)]
    # gath =  asyncio.gather(say_after(val, 'hello', 0), say_after(val, 'hello', 1))
    gath =  asyncio.gather(*fl)
    # gath =  asyncio.gather([say_after(val, 'hello', i) for i in range(5)])
    await gath
    print(f"{val}")
    print(f"{tail}")
    print(f"finished at {time.strftime('%X')}")

asyncio.run(main())



# def father():
#     def son(args):
#         print('uh \'oin on')
#     setattr(a,'name','aron')
#     return a
     
# a = father()
# print(getattr(a,'name'))
# a(0)