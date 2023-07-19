import os
from datetime import datetime
import pandas as pd
import requests
import tabula

from settings import car_list
import aspose.words as aw
from pdfminer.high_level import extract_text


def add_file_name_for_cashe(file_name):
    with open('../cashe/cashe.txt', 'a+') as f:
        f.write(f"{file_name},")
        #print(f"Добавили {file_name} в кэш")
        os.remove(file_name)
        #print(f"Удалил: {file_name}")


def get_title_pdf(file_name):
    '''
    Функция получает номер акта и марку авто из PDF файла
    и возвращает кортеж с номером акта и маркой авто
    '''
    text = extract_text(file_name).replace('\n', '')
    number_index = text.find("№") + 3
    if number_index != -1:
        num = ''
        while True:
            str_num = text[number_index]
            if str_num.isnumeric() or str_num == "G" or str_num == "S" or str_num == "-" or str_num == "_":
                num += str_num
                number_index += 1
            else:
                num = num.replace('-', '_')
                break
        for car in car_list:
            index_car = text.find(car)
            if index_car != -1:
                car = ''
                while True:
                    car_ = text[index_car]
                    if car_ != ',':
                        car += car_
                        index_car += 1
                    else:
                        car = car.replace(' ', '_').replace('"', '').replace('-', '')
                        return (num, car)


def collects_pdf_files() -> list:
    '''Функция получает список необработанных PDF файлов и возвращает его'''
    os.chdir("pdf_files")  # сменили директорию.
    list_files = os.listdir()  # получили список файлов в ней

    return list_files


def get_datetime():
    '''Функция формирует необходимый формат даты и времени'''
    current_date = str(datetime.now().date()).split('-')
    dates = current_date[2] + '.' + current_date[1] + '.' + current_date[0]
    return dates


#def upload_pdf(pdf_file):
#    '''
#    извлекает данные из PDF файла в TXT
#    :param pdf_file:
#    :return:
#    '''
#    pdf = aw.Document(pdf_file)
#    file_name_txt = pdf_file.replace(".pdf", ".txt")
#    pdf.save(f"../txt_files/{file_name_txt}")
#    return file_name_txt


def fetch(url, params, body):
    '''
    функция отправляет запрос в зависимости от типа запроса и возвращает ответ
    :param url:
    :param params:
    :param body:
    :return:
    '''
    headers = params["headers"]
    method = params["method"]
    if method == "POST":
        return requests.post(url, headers=headers, data=body)
    if method == "GET":
        return requests.get(url, headers=headers)


#def get_car_name(file_name) -> str:
#    '''
#    Ищет марку авто в TXT файле
#    :param file_name:
#    :return:
#    '''
#    file = open(f"../txt_files/{file_name}", encoding='UTF-8')
#    car_ = ''
#    for row in file:
#        for car in car_list:
#            if row.find(car) != -1:
#                if row.find('/') != -1:
#                    car_ += row.split('/')[0][row.find(car):]
#                else:
#                    car_ += row.split(',')[0][row.find(car):]
#                return car_


def create_body(car_id, date, detail):
    '''функция формирует тело запроса по названию детали и авто'''
    body = f"*oemId*:{car_id},*subjectRF*:77,*versionDate*:*{date}*,*partNumber1*:*{detail}*"
    body = ('{' + body + '}').replace('*', '\"')
    return body


def get_car_id(car_name, car_ids):
    '''
    находит ID авто по имени авто из TXT файла
    :param car_name:
    :param car_ids:
    :return:
    '''
    car_str = car_name.split('_')[0]
    if car_str in car_ids:
        return car_ids[car_str]



#def get_data_for_txt(file_name: str) -> dict:
#    '''
#    Собирает данные из файла TXT в словарь - детали/цена
#    :param file_name:
#    :return:
#    '''
#    file = open(f"../txt_files/{file_name}", encoding='UTF-8')
#    details = {}  # Деталь/цена
#    page = 1  # строка таблицы
#    count = 100
#    detail = ''  # список кодов деталей
#    n = 0  # счетчик повторяющихся названий деталей
#
#    for row in file:
#
#        if count == 0:
#            detail = row.replace('\n', '').replace(' ', '').replace('-', '')
#            if detail in details:  # обработка на случай если елемент с таким же названием  уже есть в словаре
#                detail += '_' + str(n)
#                details[detail] = []
#                n += 1
#            else:
#                details[detail] = []  # если элемент первый в строке(код детали)
#        elif count == 1:
#            details[detail] += [row.replace('\n', '')]
#
#        elif count == 6:
#
#            details[detail] += [row.replace('\n', '').replace(' ', '')]
#            print(row.replace('\n', '').replace(' ', ''))
#        count += 1
#
#        if len(row) <= 4 and row == f'{page}\n':  # блок для вычленения из файла строк подходящих под нумерацию строчек таблицы
#            page += 1
#            count = 0
#
#    return details


def get_details_for_rsa(detales, car_id, date, url, header):
    '''
    Функция собирает данные с сайта РСА по ценам на интересующие нас детали
    :param detales:
    :param car_id:
    :param date:
    :param url:
    :param header:
    :return:
    '''
    detales_ = {}
    for detail in detales:
        body = create_body(car_id, date, detail)
        result = fetch(url, header, body).json()
        try:
            detail_code = result['repairPartDtoList'][0]['partnumber']
            detail_price = float(result['repairPartDtoList'][0]['baseCost'])
            detales_[detail_code] = detail_price
        except Exception as e:
            print(e)
    return detales_


def report_create(detales, detales_):
    '''Функция создает отчет по сравнению цен указанных в калькцляции с ценами с сайта РСА'''
    list_for_data = []

    for detail in detales.keys():  # цикл по деталям из калькуляции
        data_for_excel = {}

        if detail in detales_ and detales_[detail] != None:  # условие: если деталь из калькуляции есть в деталях из РСА
            if '_' in detail:
                detail = detail.split('_')[0]
                data_for_excel['Кат. номер'] = detail
                data_for_excel['Наименование'] = detales[detail][0]
            else:
                data_for_excel['Кат. номер'] = detail
                data_for_excel['Наименование'] = detales[detail][0]

            data_for_excel['Цена в Калькуляции рубли'] = detales[detail][1]
            data_for_excel['Цена на сайте РСА рубли'] = detales_[detail]

            raznost_cen = detales[detail][1] - float(detales_[detail])

            if raznost_cen < 0:
                data_for_excel['Дороже на РСА'] = 1
                data_for_excel['Дешевле на РСА'] = 0
            else:
                data_for_excel['Дешевле на РСА'] = 1
                data_for_excel['Дороже на РСА'] = 0

            data_for_excel['Разница в цене рубли'] = round(abs(raznost_cen), 2)

            list_for_data.append(data_for_excel)
        else:
            if '_' in detail:
                detail_ = detail.split('_')[0]
                data_for_excel['Кат. номер'] = detail_
                data_for_excel['Наименование'] = detales[detail][0]
            else:
                data_for_excel['Кат. номер'] = detail
                try:
                    data_for_excel['Наименование'] = detales[detail][0]
                except:
                    data_for_excel['Наименование'] = 0
            try:
                data_for_excel['Цена в Калькуляции рубли'] = detales[detail][1]
            except:
                data_for_excel['Цена в Калькуляции рубли'] = 0
            data_for_excel['Цена на сайте РСА рубли'] = 0
            data_for_excel['Дороже на РСА'] = 0
            data_for_excel['Дешевле на РСА'] = 0
            data_for_excel['Разница в цене рубли'] = 0
            list_for_data.append(data_for_excel)

    return list_for_data


def xlsx_file_create(car_name, file_name, list_for_data):
    file_name = file_name.split('.')[0]
    df = pd.DataFrame(list_for_data)
    car_name = car_name.replace('/', '_')
    df.to_excel(f"../xlsx_files/{file_name}_{car_name}.xlsx")


def get_data_for_pdf_file(file_name: str) -> dict:
    '''
    Функция анализирует PDF файл и формирует словарь с данными о детали
    ID детали : [название детали, цена детали]
    :param file_name: имя файла
    :return: словарь {ID детали : [название детали, цена детали]}
    '''
    pdf_tables = tabula.read_pdf(file_name, pages='all', multiple_tables=True, lattice=True)
    details = {}
    table_count = 0
    column_count = 0
    row_count = 0
    detail_id = ''
    n = 0
    while True:
        try:
            if column_count == 1:
                detail_id = pdf_tables[table_count].iloc[row_count, column_count].replace('\n', '').replace(' ', '').replace('-', '')
                if detail_id in details:  # обработка на случай если елемент с таким же названием  уже есть в словаре
                    detail_id += '_' + str(n)
                    details[detail_id] = []
                    n += 1
                else:
                    details[detail_id] = []
            elif column_count == 2:
                detail_name = pdf_tables[table_count].iloc[row_count, column_count]
                details[detail_id] += [detail_name]
            elif column_count == 7:
                price = pdf_tables[table_count].iloc[row_count, column_count]
                details[detail_id] += [float(price.replace(' ', ''))]
            elif column_count == 8:
                column_count *= 0
                row_count += 1
                detail_id *= 0
            column_count += 1
        except:
            if table_count == 0:
                table_count += 1
                column_count *= 0
                row_count *= 0
            else:
                print(details)
                return details