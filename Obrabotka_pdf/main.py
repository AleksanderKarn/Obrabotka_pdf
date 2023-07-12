import os

from functions import upload_pdf, get_data_for_txt, get_car_name, get_datetime, get_car_id, funk, report_create, \
    collects_pdf_files, xlsx_file_create
from new_email_module import connector_for_mail
from settings import car_ids, url, header, username, password, email_server, directory


def main():
    connector_for_mail(username, password, email_server, directory)
    pdf_files = collects_pdf_files()  # Список необработанных pdf файлов
    for file in pdf_files:
        file_name_txt = upload_pdf(file)  # создали txt файл
        detales = get_data_for_txt(file_name_txt)  # детали и их цены из файла калькуляции
        print(detales)
        os.replace(file, f"pdf_files_executed/{file}")

        car_name = get_car_name(file_name_txt)
        print(f"Название авто: {car_name}")
        date = get_datetime()
        print(f"Дата: {date}")
        car_id = get_car_id(car_name, car_ids=car_ids)
        print(f"ID: {car_id}")
        print(f"Название файла txt: {file_name_txt}")
        print("Текущая деректория:", os.getcwd())
        os.replace(f"../txt_files/{file_name_txt}", f"../txt_files/txt_files_executed/{file_name_txt}")
        detales_rsa = funk(detales, car_id, date, url, header)  # детали и их цены с сайта РСА
        print(f"Детали с сайта РСА: {detales_rsa}")
        list_for_data = report_create(detales, detales_rsa)
        print(list_for_data)
        xlsx_file_create(f"{file_name_txt}", list_for_data)


if __name__ == "__main__":
    main()


