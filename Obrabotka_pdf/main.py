import os

from functions import get_datetime, get_car_id, get_details_for_rsa, report_create, \
    collects_pdf_files, xlsx_file_create, get_data_for_pdf_file, get_title_pdf, add_file_name_for_cashe
from new_email_module import connector_for_mail
from settings import car_ids, url, header, username, password, email_server, directory


def main():
    connector_for_mail(username, password, email_server, directory)
    pdf_files = collects_pdf_files()  # Список необработанных pdf файлов
    print(f"список pdf файлов для обработки: {pdf_files}")
    if pdf_files:
        for file in pdf_files:
            detales = get_data_for_pdf_file(file)
            car_name = get_title_pdf(file)[1]
            print(f"Название авто: {car_name}")
            date = get_datetime()
            car_id = get_car_id(car_name, car_ids=car_ids)
            print(f"ID: {car_id}")
            detales_rsa = get_details_for_rsa(detales, car_id, date, url, header)  # детали и их цены с сайта РСА
            print(f"Детали с сайта РСА: {detales_rsa}")
            list_for_data = report_create(detales, detales_rsa)
            print(f"Список данных для записи в EXEL: {list_for_data}")

            file_name = os.path.basename(file)
            print(file_name)
            add_file_name_for_cashe(file_name)
            xlsx_file_create(car_name, file_name, list_for_data)
    else:
        print("Новых писем нет!")


if __name__ == "__main__":
    main()
