from aiogram.fsm.context import FSMContext

from handlers.utils.chat_history import ChatHistory

async def get_history_by_user_id(user_id, state: FSMContext):
    history = await state.get_data()
    if "history" not in history:
        history["history"] = {}
        history["history"][user_id] = history["history"].get(user_id, [])  # Сохраняем user ID
        await state.set_data(history)
    elif user_id in history['history']:
        return history['history'][user_id]