import Config
import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload,MediaFileUpload
import sqlite3
import pprint


class DataBase:
    def __init__(self):
        self._uploadIdFromDB()

    def _uploadIdFromDB(self): # обновляет список айди
        try:
            try:
                if Config.NAME_DB not in os.listdir(path='.'):
                    self.upload_file()
                conn = sqlite3.connect(Config.NAME_DB)
                cursor = conn.cursor()
                all_data_in_db = f"""SELECT * from {Config.TABLE_DB_NAME}"""
                cursor.execute(all_data_in_db)
                records = cursor.fetchall()
                self.ALL_IDs_FROM_DB = [i[0] for i in records]
            except FileNotFoundError:
                self.upload_file()
        except sqlite3.Error as error:
            print("Ошибка при работе с SQLite", error)
    
    def upload_file(self):  # загрузка бд в директорию бота
        if Config.NAME_DB not in os.listdir(path='.'):
            pp = pprint.PrettyPrinter(indent=4)
            SCOPES = ['https://www.googleapis.com/auth/drive']
            SERVICE_ACCOUNT_FILE = 'telbotpy-9d6a5e48ed1e.json'
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('drive', 'v3', credentials=credentials)
            results = service.files().list(pageSize=10,
                                        fields="nextPageToken, files(id, name, mimeType)").execute()
            pp.pprint(results)
            file_id = results.get('files')[0].get('id')
            request = service.files().get_media(fileId=file_id)
            fh = io.FileIO(Config.NAME_DB, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print("Download %d%%." % int(status.progress() * 100))
        else:
            print('уже добавлена')

    def delete(self, user_id): # удаление человека из БД
        try:
            conn = sqlite3.connect(Config.NAME_DB)  # или :memory: чтобы сохранить в RAM
            if str(user_id) in self.ALL_IDs_FROM_DB:
                mydata = conn.execute(f"DELETE FROM {Config.TABLE_DB_NAME} WHERE UserID=?", (user_id,))
                conn.commit()
                self.ALL_IDs_FROM_DB.pop(self.ALL_IDs_FROM_DB.index(str(user_id)))
                print(f'Удален пользователь c id {user_id}')
                self.backup()
                return 'Удаление прошло успешно.'
            else:
                return 'Вы уже удалены из Базы Данных.'
        except Exception as e:
            print(e)
            return 'При удалении записи произошла ошибка. Попробуйте снова.'
        finally:
            conn.close()

    def backup(self): # бекап текущей версии бд на гугл диск и отправка ее администратору
        try:
            pp = pprint.PrettyPrinter(indent=4)
            SCOPES = ['https://www.googleapis.com/auth/drive']
            SERVICE_ACCOUNT_FILE = 'telbotpy-9d6a5e48ed1e.json'
            credentials = service_account.Credentials.from_service_account_file(
                SERVICE_ACCOUNT_FILE, scopes=SCOPES)
            service = build('drive', 'v3', credentials=credentials)
            results = service.files().list(pageSize=10,
                                        fields="nextPageToken, files(id, name, mimeType)").execute()
            pp.pprint(results)

            service.files().delete(fileId=results.get('files')[0].get('id'), ).execute()
            file_metadata = {
                'name': Config.NAME_DB,
                'mimeType': 'application/vnd.sqlite3',
                'parents': [Config.PATH_TO_DB_ON_GD]
            }
            media = MediaFileUpload(Config.NAME_DB, mimetype='application/vnd.sqlite3', resumable=True)
            r = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            pp.pprint(r)
        except FileNotFoundError:
            self.upload_file()

    def add_user(self, message): # добавление пользователя в бд
        try:
            conn = sqlite3.connect(Config.NAME_DB)
            cursor = conn.cursor()
            sqlite_insert_with_param = f"""INSERT INTO {Config.TABLE_DB_NAME}
                                                (UserID, Username, FirstName, LastName)
                                                VALUES (?, ?, ?, ?);"""

            data_tuple = (message.from_user.id, message.from_user.username, message.from_user.first_name,
                                    message.from_user.last_name)
            cursor.execute(sqlite_insert_with_param, data_tuple)
            conn.commit()
            self.backup()
            self.ALL_IDs_FROM_DB.append(str(message.from_user.id))
            print(f'Добавлен пользователь {message.from_user.first_name}')
        except FileNotFoundError:
            self.upload_file()
            if message.from_user.id not in self.ALL_IDs_FROM_DB:
                self.add_user(message)

    
a = DataBase()