
# import asyncio
# import uvloop

# # async def get_some_values_from_io():
# #     # Some IO code which returns a list of values
# #     return [0]*10

# # vals = []

# # async def fetcher():
# #     while True:
# #         print("CP fetcher.1")
# #         io_vals = await get_some_values_from_io()
# #         print("CP fetcher.2")
# #         for val in io_vals:
# #             vals.append(io_vals)
# #         print("CP fetcher.3")

# # async def monitor():
# #     while True:
# #         print (len(vals))
# #         await asyncio.sleep(1)
# #         print("CP monitor.exit")

# # async def main():
# #     t1 = asyncio.create_task(fetcher())
# #     t2 = asyncio.create_task(monitor())
# #     print("CP start async")
# #     await asyncio.gather(t1, t2)
# #     print("CP exiting async")


# # if __name__ == '__main__':
# #     print("CP start.log")

# #     print("CP start.log")
# #     asyncio.run(main())
# #     print("CP exiting")
# #     print("CP end.log")



# async def counter(name: str):
#     for i in range(0, 100):
#         print(f"{name}: {i!s}")
#         await asyncio.sleep(0)

# async def main():
#     tasks = []
#     for n in range(0, 4):
#         tasks.append(asyncio.create_task(counter(f"task{n}")))

#     while True:
#         tasks = [t for t in tasks if not t.done()]
#         if len(tasks) == 0:
#             return

#         await tasks[0]

# uvloop.install()
# asyncio.run(main())