import sqlite3
import datetime
class Database:
    def __init__(self, dbfile):
        self.connection = sqlite3.connect(dbfile)
        self.cursor = self.connection.cursor()
    #Добавляем операцию
    def add_operation(self, user_id, is_income, amount, reason):
        with self.connection:
            return self.cursor.execute(
                'INSERT INTO operations (user_id, is_income, amount, reason, date) VALUES (?, ?, ?, ?, ?)',
                (user_id, is_income, amount, reason, datetime.date.today(),))
    #получаем статистику для экспорта за неделю
    def get_data_week_export(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?)"
            " AND date BETWEEN datetime('now', '-8 days') AND datetime('now', 'localtime')",
            (user_id,)).fetchall()

    #получаем статистику для экспресс отчета за неделю
    def get_data_week_filtered(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?) AND is_income=0"
            " AND date BETWEEN datetime('now', '-8 days') AND datetime('now', 'localtime')",
            (user_id,)).fetchall()

    #получаем статистику для экспорта за день
    def get_data_day_export(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?)"
            " AND date BETWEEN datetime('now', '-1 days') AND datetime('now', 'localtime')",
            (user_id,)).fetchall()

    #получаем статистику для экспресс отчета за день
    def get_data_day_filtered(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?) AND is_income=0"
            " AND date BETWEEN datetime('now', '-1 days') AND datetime('now', 'localtime')",
            (user_id,)).fetchall()

    #получаем статистику для экспорта за месяц
    def get_data_month_export(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?)"
            " AND date BETWEEN datetime('now', '-32 days') AND datetime('now', 'localtime')",
            (user_id,)).fetchall()

    #получаем статистику для экспресс отчета за месяц
    def get_data_month_filtered(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?) AND is_income=0"
            " AND date BETWEEN datetime('now', '-32 days') AND datetime('now', 'localtime')",
            (user_id,)).fetchall()

    #получаем статистику дохода для экспресс отчета за месяц
    def income_data_month(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?) AND is_income=1"
            " AND date BETWEEN datetime('now', '-32 days') AND datetime('now', 'localtime')",
            (user_id,)).fetchall()

    #получаем статистику дохода для экспресс отчета за неделю
    def income_data_week(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?) AND is_income=1"
            " AND date BETWEEN datetime('now', '-8 days') AND datetime('now', 'localtime')",
            (user_id,)).fetchall()

    #получаем статистику всех транзакций для экспорта за все время
    def get_data_all_time(self, user_id):
        return self.cursor.execute(
            "SELECT date, amount, reason, is_income FROM operations WHERE user_id=(?)", (user_id,)).fetchall()

    def get_total_expenses(self, user_id): #получаем сумму всех расходов
        return self.cursor.execute(
            "SELECT SUM(amount) FROM operations WHERE user_id=(?) AND is_income=0", (user_id,))

    def get_total_income(self, user_id): #получаем сумму всех доходов
        return self.cursor.execute(
            "SELECT SUM(amount) FROM operations WHERE user_id=(?) AND is_income=1", (user_id,))


    #получаем созданые ранее категории определенного человека
    def get_categories(self, user_id, is_income):
        return self.cursor.execute(
            'SELECT reason FROM operations'
            ' WHERE user_id=(?) AND is_income=(?)'
            ' GROUP BY reason'
            ' ORDER BY COUNT(*) DESC,'
            ' reason DESC ', (user_id, is_income,)
        ).fetchall()

    def get_user_ids(self):
        return self.cursor.execute('SELECT DISTINCT user_id FROM operations').fetchall()

    def get_last_entry(self, id):
        # Проверяем, есть ли записи для указанного пользователя
        user_records = self.cursor.execute('SELECT id FROM operations WHERE user_id = ?', (id,)).fetchall()

        if user_records:
            # Получаем ID последней записи для указанного пользователя
            last_record_id = user_records[-1][0]

            # Удаляем запись с соответствующим ID
            self.cursor.execute('DELETE FROM operations WHERE id=?', (last_record_id,))

            # Сохраняем изменения в базе данных
            self.connection.commit()

            # Возвращаем удаленную запись
            return self.cursor.execute('SELECT * FROM operations WHERE id=?', (last_record_id,)).fetchone()
        else:
            # Возвращаем None, если нет записей для пользователя
            return None


def init_db(dbfile):
    global db
    db = Database(dbfile)


def get_db():
    return db
