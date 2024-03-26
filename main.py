from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from buttons import *
from handlers import expense, income
from db import *
from excel import create_excel_file

API_TOKEN = ("6726986505:AAGjM4uTLGArO-iuYhbITsfNLDqs0jttR9Q")
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

init_db('database.db')

async def statistics(msg: types.Message):
    await msg.reply('За какой период вы хотите получить статистику?', reply_markup=choose_statistics_period_kb)


# отслеживание кнопок для получения статистики для экспорта
@dp.callback_query_handler(lambda c: c.data and c.data.startswith('btn_'))
async def process_callback_buttons(callback_query: types.CallbackQuery):
    code = callback_query.data
    if code == 'btn_day':
        data = get_db().get_data_day_export(callback_query.from_user.id)
        filename = create_excel_file(data, callback_query.from_user.id)
        await bot.send_document(callback_query.message.chat.id, open(filename, 'rb'), reply_markup=main_kb)

    elif code == 'btn_week':
        data = get_db().get_data_week_export(callback_query.from_user.id)
        filename = create_excel_file(data, callback_query.from_user.id)
        await bot.send_document(callback_query.message.chat.id, open(filename, 'rb'), reply_markup=main_kb)

    elif code == 'btn_month':
        data = get_db().get_data_month_export(callback_query.from_user.id)
        filename = create_excel_file(data, callback_query.from_user.id)
        await bot.send_document(callback_query.message.chat.id, open(filename, 'rb'), reply_markup=main_kb)

    elif code == 'btn_all_time':
        data = get_db().get_data_all_time(callback_query.from_user.id)
        filename = create_excel_file(data, callback_query.from_user.id)
        await bot.send_document(callback_query.message.chat.id, open(filename, 'rb'), reply_markup=main_kb)


@dp.message_handler(commands=['start'])
async def start(msg: types.Message):
    # Получить никнейм пользователя
    nick = msg.from_user.username

    # Отправляем приветствие
    await msg.reply(
        f'Привет, {nick}👋 !\n\nЯ твой бот- помощник для учета финансов💰\n\n'
        f'Мой функционал:\n'
        f'➡Запись расходов и доходов\n'
        f'➡Удаление последней записи из базы данных\n'
        f'➡Просматр статистики расходов за день, неделю и месяц\n'
        f'➡Просматр статистики доходов за день, неделю и месяц\n'
        f'➡Отображение статуса финансов\n'
        f'➡Экспорт данных в формате excel с подробным отчетом и диаграммами за конкретный период\n\n'
        f'Используй навигационные кнопки',

        reply_markup=main_kb)



expense.register_expense_handlers(dp)
income.register_income_handlers(dp)

@dp.message_handler()
async def main(msg: types.Message):
    text = msg.text
    if text == 'Добавить расход':
        await expense.add_expense(msg)
    elif text == 'Добавить доход':
        await income.add_income(msg)
    elif text == 'Экспорт данных':
        await statistics(msg)
    elif text == 'Расходы за день':
        await spend_today_command(msg)
    elif text == 'Расходы за неделю':
        await spend_week_command(msg)
    elif text == 'Расходы за месяц':
        await spend_month_command(msg)
    elif text == 'Доходы за неделю':
        await income_week_command(msg)
    elif text == 'Доходы за месяц':
        await income_month_command(msg)
    elif text == 'Статус финансов':
        await financial_status(msg)
    elif text == 'Удалить последнюю запись':
        await delete_last_entry(msg)
    else:
        await msg.reply('Извините, я вас не понял. Пожалуйста, используйте команду еще раз',
                        reply_markup=main_kb)

async def delete_last_entry(msg: types.Message):   #выбираем последнюю запись по id
    row_id = msg.from_user.id
    last_entry = get_db().get_last_entry(row_id)
    if last_entry:
        get_db().delete_entry(last_entry['id'])
        await msg.answer('Последняя запись удалена!', reply_markup=main_kb)
    else:
        await msg.answer('Последняя запись удалена!', reply_markup=main_kb)
async def spend_today_command(msg: types.Message):
    row_id = msg.from_user.id
    expenses = get_db().get_data_day_filtered(row_id)

    if expenses:
        total_amount = 0
        for date, amount, reason, is_income in expenses:
            if is_income == 0:
                total_amount += amount

        expense_text = ""
        for date, amount, reason, is_income in expenses:
            if is_income == 0:
                expense_text += f" Дата: {date}\n Категория: {reason}\n Сумма: {amount} руб.\n"
                expense_text += f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"

        await msg.answer(("Расходы за сегодня:\n\n") + expense_text + f"\n\nОбщая сумма: {total_amount} руб.", reply_markup=main_kb)
    else:
        await msg.answer("Расходов за сегодня нет", reply_markup=main_kb)

async def spend_week_command(msg: types.Message):
    row_id = msg.from_user.id
    expenses = get_db().get_data_week_filtered(row_id)

    if expenses:
        total_amount = 0
        for date, amount, reason, is_income in expenses:
            if is_income == 0:
                total_amount += amount

        expense_text = ""
        for date, amount, reason, is_income in expenses:
            if is_income == 0:
                expense_text += f" Дата: {date}\n Категория: {reason}\n Сумма: {amount} руб.\n"
                expense_text += f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"

        await msg.answer(("Расходы за неделю:\n\n") + expense_text + f"\n\nОбщая сумма: {total_amount} руб.",
                         reply_markup=main_kb)
    else:
        await msg.answer("Расходов за неделю нет", reply_markup=main_kb)

async def spend_month_command(msg: types.Message):
    row_id = msg.from_user.id
    expenses = get_db().get_data_month_filtered(row_id)

    if expenses:
        total_amount = 0
        for date, amount, reason, is_income in expenses:
            if is_income == 0:
                total_amount += amount

        expense_text = ""
        for date, amount, reason, is_income in expenses:
            if is_income == 0:
                expense_text += f" Дата: {date}\n Категория: {reason}\n Сумма: {amount} руб.\n"
                expense_text += f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"

        await msg.answer(("Расходы за месяц:\n\n") + expense_text + f"\n\nОбщая сумма: {total_amount} руб.",
                         reply_markup=main_kb)
    else:
        await msg.answer("Расходов этот месяц нет", reply_markup=main_kb)

async def income_week_command(msg: types.Message):
    row_id = msg.from_user.id
    incomes = get_db().income_data_week(row_id)

    if incomes:
        total_amount = 0
        for date, amount, reason, is_income in incomes:
            if is_income == 1:
                total_amount += amount

        incomes_text = ""
        for date, amount, reason, is_income in incomes:
            if is_income == 1:
                incomes_text += f" Дата: {date}\n Категория: {reason}\n Сумма: {amount} руб.\n"
                incomes_text += f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"

        await msg.answer(("Доходы за неделю:\n\n") + incomes_text + f"\n\nОбщая сумма: {total_amount} руб.",
                         reply_markup=main_kb)
    else:
        await msg.answer("Доходов за эту неделю нет", reply_markup=main_kb)

async def income_month_command(msg: types.Message):
    row_id = msg.from_user.id
    incomes = get_db().income_data_month(row_id)

    if incomes:
        total_amount = 0
        for date, amount, reason, is_income in incomes:
            if is_income == 1:
                total_amount += amount

        incomes_text = ""
        for date, amount, reason, is_income in incomes:
            if is_income == 1:
                incomes_text += f" Дата: {date}\n Категория: {reason}\n Сумма: {amount} руб.\n"
                incomes_text += f"➖➖➖➖➖➖➖➖➖➖➖➖\n\n"

        await msg.answer(("Доходы за месяц:\n\n") + incomes_text + f"\n\nОбщая сумма: {total_amount} руб.",
                         reply_markup=main_kb)
    else:
        await msg.answer("Доходов за этот месяц нет", reply_markup=main_kb)

async def financial_status(msg: types.Message):
    # Получить общую сумму расходов
    total_expenses_cursor = get_db().get_total_expenses(msg.from_user.id)
    total_expenses = total_expenses_cursor.fetchone()[0] if total_expenses_cursor else 0

    # Получить общую сумму доходов
    total_income_cursor = get_db().get_total_income(msg.from_user.id)
    total_income = total_income_cursor.fetchone()[0] if total_income_cursor else 0

    # Вычислить процентное превышение доходов над расходами
    if total_expenses != 0:
        percentage_excess = ((total_income - total_expenses) / total_expenses) * 100
    else:
        percentage_excess = 0  # Если общие расходы равны нулю

    # Отправить сообщение с процентным превышением
    if percentage_excess > 0:
        await msg.reply(f'Процент превышения доходов над расходами: {percentage_excess:.2f}% Отлично управляетесь с финансами!', reply_markup=main_kb)
    elif percentage_excess < 0:
        await msg.reply(f'Процент превышения расходов над доходами: {abs(percentage_excess):.2f}% Ситуация требует внимания и коррекции', reply_markup=main_kb)
    else:
        await msg.reply('Доходы и расходы сбалансированы.', reply_markup=main_kb)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
