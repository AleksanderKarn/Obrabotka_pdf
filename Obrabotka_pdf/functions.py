import os
from datetime import datetime
import pandas as pd
import requests

from settings import car_list
import aspose.words as aw


def collects_pdf_files():
    '''Функция получает список необработанных PDF файлов и возвращает его'''
    os.chdir("pdf_files")  # сменили директорию.
    list_files = os.listdir()  # получили список файлов в ней
    list_files.remove('pdf_files_executed')
    return list_files


def get_datetime():
    '''Функция формирует необходимый формат даты и времени'''
    current_date = str(datetime.now().date()).split('-')
    dates = current_date[2] + '.' + current_date[1] + '.' + current_date[0]
    return dates


def upload_pdf(pdf_file):
    '''
    извлекает данные из PDF файла в TXT
    :param pdf_file:
    :return:
    '''
    pdf = aw.Document(pdf_file)
    file_name_txt = pdf_file.replace(".pdf", ".txt")
    pdf.save(f"../txt_files/{file_name_txt}")
    #print(f'имя файла txt: {file_name_txt}')
    return file_name_txt


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


def get_car_name(file_name) -> str:
    '''
    Ищет марку авто в TXT файле
    :param file_name:
    :return:
    '''
    file = open(f"../txt_files/{file_name}", encoding='UTF-8')
    car_ = ''
    for row in file:
        # print(f"Строка для поиска марки авто: {row}")
        for car in car_list:
            # print(f"Марка машины для поиска в строке: {car}")
            if row.find(car) != -1:
                if row.find('/') != -1:
                    # print(f"Блок ИФ")
                    car_ += row.split('/')[0][row.find(car):]
                else:
                    car_ += row.split(',')[0][row.find(car):]
                    # print("Блок ЕЛС")
                return car_


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
    car_str = car_name.split(' ')
    for i in car_str:
        if i in car_ids:
            car_id = car_ids[i]
            return car_id


def get_data_for_txt(file_name: str) -> dict:
    '''
    Собирает данные из файла TXT в словарь - детали/цена
    :param file_name:
    :return:
    '''
    file = open(f"../txt_files/{file_name}", encoding='UTF-8')
    details = {}  # Деталь/цена
    page = 1  # строка таблицы
    count = 100
    detail = ''  # список кодов деталей
    n = 0  # счетчик повторяющихся названий деталей

    for row in file:

        if count == 0:
            detail = row.replace('\n', '').replace(' ', '').replace('-', '')
            if detail in details:  # обработка на случай если елемент с таким же названием  уже есть в словаре
                detail += '_' + str(n)
                details[detail] = []
                n += 1
            else:
                details[detail] = []  # если элемент первый в строке(код детали)
        elif count == 1:
            details[detail] += [row.replace('\n', '')]

        elif count == 2:

            details[detail] += [row.replace('\n', '').replace(' ', '')]
        count += 1

        if len(row) <= 3 and row == f'{page}\n':  # блок для вычленения из файла строк подходящих под нумерацию строчек таблицы
            page += 1
            count = 0

    return details


def funk(detales, car_id, date, url, header):
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
            detail_price = result['repairPartDtoList'][0]['baseCost']
            detales_[detail_code] = detail_price
        except Exception as e:
            print(e)
    return detales_


def report_create(detales, detales_):
    '''Функция создает отчет по сравнению цен указанных в калькцляции с ценами с сайта РСА'''
    #print(f"Детали из калькуляции: {detales}")
    #print(f"Детали из PCA: {detales_}")

    bull = 1
    list_for_data = []

    for detail in detales.keys():  # цикл по деталям из калькуляции
        data_for_excel = {}

        if detail in detales_ and detales_[
            detail] != None:  # условие - если деталь из калькуляции есть в деталях из РСА
            if '_' in detail:
                detail = detail.split('_')[0]
                data_for_excel['Кат. номер'] = detail
                data_for_excel['Наименование'] = detales[detail][0]
            else:
                data_for_excel['Кат. номер'] = detail
                data_for_excel['Наименование'] = detales[detail][0]
            data_for_excel['Цена в Калькуляции рубли'] = detales[detail][1]
            data_for_excel['Цена на сайте РСА рубли'] = detales_[detail]
            if bull > 0:
                data_for_excel['Дороже на РСА'] = '+'
                data_for_excel['Дешевле на РСА'] = '—'
            else:
                data_for_excel['Дешевле на РСА'] = '+'
                data_for_excel['Дороже на РСА'] = '—'
            raznost_cen = int(detales[detail][1].split('.')[0].replace(' ', '')) - int(
                detales_[detail].split('.')[0].replace(' ', ''))
            data_for_excel['Разница в цене рубли'] = abs(raznost_cen)

            list_for_data.append(data_for_excel)
            bull *= -1
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
                    data_for_excel['Наименование'] = '-'
            try:
                data_for_excel['Цена в Калькуляции рубли'] = detales[detail][1]
            except:
                data_for_excel['Цена в Калькуляции рубли'] = '-'
            data_for_excel['Цена на сайте РСА рубли'] = '—'
            data_for_excel['Дороже на РСА'] = '—'
            data_for_excel['Дешевле на РСА'] = '—'
            data_for_excel['Разница в цене рубли'] = '—'
            list_for_data.append(data_for_excel)
            bull *= -1

    return list_for_data


def xlsx_file_create(file_name, list_for_data):
    car_name = get_car_name(f"../txt_files/txt_files_executed/{file_name}").replace(' ', '_')

    df = pd.DataFrame(list_for_data)
    df.to_excel(f"{file_name}_{car_name}.xlsx")


