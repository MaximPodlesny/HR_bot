from aiogram.fsm.context import FSMContext
from handlers.utils.chat_history import ChatHistory
from collections import deque
from bot import history

async def record_history_by_user_id(user_id, data, state: FSMContext):
    print('\n\n!!\n\n in rec hist', history)
    history_user = history.get(user_id, deque([], maxlen=50))
    history_user.append(data)
    history[user_id] = history_user
    print('\n\n!!\n\n in rec hist 2', history)
    # if user_id not in history:
    #     history[user_id] = deque(maxlen=50)
    #     history[user_id] = [data]
    # elif user_id in history:
    #     print('\n\n!!\n\n in rec hist', history['history'][user_id])
    #     history['history'][user_id].append(data)
    #     await state.set_data(history)
    #     print('\n\n!!\n\n in rec hist 2', history['history'][user_id])
# async def record_history_by_user_id(user_id, data, state: FSMContext):
#     history = await state.get_data()
#     if "history" not in history:
#         history["history"] = {user_id: [data]}
#         # history["history"][user_id] = [data]  # Сохраняем user ID
#         await state.set_data(history)
#     elif user_id in history['history']:
#         print('\n\n!!\n\n in rec hist', history['history'][user_id])
#         history['history'][user_id].append(data)
#         await state.set_data(history)
#         print('\n\n!!\n\n in rec hist 2', history['history'][user_id])