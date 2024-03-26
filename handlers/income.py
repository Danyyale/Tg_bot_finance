from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram import types, Dispatcher
from datetime import datetime

from buttons import *
from db import *


class IncomeForm(StatesGroup):
    amount = State()
    reason = State()
    confirm = State()


async def add_income(msg: types.Message):
    await msg.reply('Введите сумму дохода')
    await IncomeForm.amount.set()


async def process_income_amount(msg: types.Message, state: FSMContext):
    text = msg.text
    if text.isdigit():
        await state.update_data(amount=text)
        await msg.answer('Введите тип дохода или выберете из уже созданных',
                         reply_markup=get_categories_kb(get_db().get_categories(msg.from_user.id, 1)))
        await IncomeForm.reason.set()
    else:
        await msg.answer('Вы ввели некорректое число')
        await state.reset_data()
        await state.finish()


async def process_income_category_selection_btn(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    category = code[13:]
    await state.update_data(reason=category)
    await callback_query.message.answer('Подтвердить внесение?', reply_markup=confirm_kb)
    await IncomeForm.confirm.set()


async def process_income_reason(msg: types.Message, state: FSMContext):
    text = msg.text
    await state.update_data(reason=text)
    await msg.reply('Подтвердить внесение?', reply_markup=confirm_kb)
    await IncomeForm.confirm.set()


async def process_income_confirm_btn(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data
    if code == 'btn_confirm':
        data = await state.get_data()

        user_id = callback_query.from_user.id
        is_income = True
        amount = data['amount']
        reason = data['reason'].capitalize()
        get_db().add_operation(user_id, is_income, amount, reason)

        # Отображение внесенной информации
        await display_added_info(callback_query.message, reason, amount)

        await callback_query.answer('Успешно внесено!')
        await callback_query.message.delete_reply_markup()
        await state.finish()

    elif code == 'btn_cancel':
        await state.reset_state()
        await callback_query.answer('Отменено!')
        await callback_query.message.delete_reply_markup()
        await state.finish()

async def display_added_info(message: types.Message, reason: str, amount: str):
    current_date = datetime.datetime.now()
    text = f"Доход добавлен!\n\nКатегория: {reason}\nСумма: {amount} руб.\nДата: {current_date.strftime('%d.%m.%Y %H:%M')}"
    await message.answer(text, reply_markup=main_kb)

def register_income_handlers(dp: Dispatcher):
    dp.register_message_handler(add_income, Text('Добавить доход'))
    dp.register_message_handler(process_income_amount, state=IncomeForm.amount)
    dp.register_message_handler(process_income_reason, state=IncomeForm.reason)
    dp.register_callback_query_handler(process_income_category_selection_btn,
                                       lambda c: c.data and c.data.startswith('btn_category_'), state=IncomeForm.reason)
    dp.register_callback_query_handler(process_income_confirm_btn, state=IncomeForm.confirm)
