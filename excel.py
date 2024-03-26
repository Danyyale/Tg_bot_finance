import xlsxwriter
import datetime


def create_excel_file(data, user_id):
    # Формирование имени файла
    workbook = xlsxwriter.Workbook(f'{user_id}.xlsx')
    filename = f'{user_id}.xlsx'
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    format = workbook.add_format({'num_format': 'dd.mm.yy'})  # формат для правильного вписывания даты
    merge_format = workbook.add_format({  # формат для объединения ячеек
        "bold": 1,
        "border": 1,
        "align": "center",
        "valign": "vcenter",
        "fg_color": "yellow",
    })

    worksheet.merge_range('A1:C1', 'Расходы', merge_format)
    worksheet.merge_range('E1:G1', 'Доходы', merge_format)

    worksheet.write_row(1, 0, ['Дата', 'Сумма', 'Категория', '', 'Дата', 'Сумма', 'Категория'])

    income_sum = dict()
    expense_sum = dict()

    row1, row2 = 2, 2
    for line in data:
        # если расход
        if line[-1] == 0:
            # если категория еще не учитывалась, то добавляем, иначе прибавляем к имеющемуся
            if line[2] not in expense_sum:
                expense_sum[line[2]] = line[1]
            else:
                expense_sum[line[2]] += line[1]
            col = 0
            for element in line[:-1]:
                # правильно вписать дату
                if col == 0:
                    worksheet.write(row1, col, datetime.datetime.strptime(element, '%Y-%m-%d'), format)
                else:
                    worksheet.write(row1, col, element)
                col += 1
            row1 += 1
        else:  # если доход
            if line[2] not in income_sum:
                income_sum[line[2]] = line[1]
            else:
                income_sum[line[2]] += line[1]

            col = 4
            for element in line[:-1]:
                if col == 4:
                    worksheet.write(row2, col, datetime.datetime.strptime(element, '%Y-%m-%d'), format)
                else:
                    worksheet.write(row2, col, element)
                col += 1
            row2 += 1

    worksheet.merge_range(max(row1, row2) + 1, 0, max(row1, row2) + 1, 6, 'ПОДСЧЕТ', merge_format)
    worksheet.merge_range(max(row1, row2) + 2, 0, max(row1, row2) + 2, 2, 'Расходы', merge_format)
    worksheet.merge_range(max(row1, row2) + 2, 4, max(row1, row2) + 2, 6, 'Доходы', merge_format)

    row1 = row2 = count_start = max(row1, row2) + 3
    for i in sorted(expense_sum.items(), reverse=True, key=lambda x: x[1]):
        worksheet.write_row(row1, 0, i)
        row1 += 1

    for i in sorted(income_sum.items(), reverse=True, key=lambda x: x[1]):
        worksheet.write_row(row2, 4, i)
        row2 += 1

    chart1 = workbook.add_chart({'type': 'pie'})
    chart1.add_series({
        'name': 'Расходы',
        'categories': f'=Sheet1!$A${count_start + 1}:$A$9999',
        'values': f'=Sheet1!$B${count_start + 1}:$B$9999',
        'data_labels': {'percentage': True}

    })
    worksheet.insert_chart('J2', chart1)

    chart1 = workbook.add_chart({'type': 'pie'})
    chart1.add_series({
        'name': 'Доходы',
        'categories': f'=Sheet1!$E${count_start + 1}:$E$9999',
        'values': f'=Sheet1!$F${count_start + 1}:$F$9999',
        'data_labels': {'percentage': True}

    })
    worksheet.insert_chart('R2', chart1)
    workbook.close()
    return workbook.filename
