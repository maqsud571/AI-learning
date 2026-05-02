# # bot.py
# import asyncio
# import httpx
# from aiogram import Bot, Dispatcher, types
# ,env filedan olib kelish uchun
BOT_TOKEN = 

# API_URL = "http://localhost:8000/ask"

# bot = Bot(token=BOT_TOKEN)
# dp = Dispatcher()

# @dp.message()
# async def handle_message(message: types.Message):
#     user_question = message.text

#     async with httpx.AsyncClient() as client:
#         response = await client.post(API_URL, json={
#             "question": user_question
#         })

#     data = response.json()

#     if "error" in data:
#         await message.answer("❌ Xatolik: " + data["error"])
#     else:
#         await message.answer(f"📊 Natija:\n{data['result']}")

# async def main():
#     await dp.start_polling(bot)

# if __name__ == "__main__":
#     asyncio.run(main())

#                                                  Jarayonda