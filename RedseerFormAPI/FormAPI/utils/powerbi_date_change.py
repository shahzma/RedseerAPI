import pandas as pd
import asyncio
from django.conf import settings
import pymysql
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from firebase_admin import firestore

db_settings = settings.DATABASES['default']

class PowerbiDateUpdate:
    def get_connection_url(self):
        package = "mysql+pymysql"
        database_connection_url = f"{package}://{db_settings['USER']}:{db_settings['PASSWORD']}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"
        return database_connection_url

    def get_db_connection(self):
        database_connection_url = self.get_connection_url()
        connect_args = {'charset': 'latin1'}
        # connect_args = {'ssl': {'ttls': True}}
        engine = create_engine(database_connection_url,
                               echo=False, connect_args=connect_args)
        db_conn = engine.connect()

        dbSession = sessionmaker(bind=engine)
        db_session = dbSession()

        return db_session, db_conn

    async def powerbi_date_update(self, end_date, industry_id):
        try:
            # end_date format in MM-DD-YYYY
            db_session, db_conn = self.get_db_connection()

            update_statement = "UPDATE powerbi_data SET end_date = :end_date WHERE industry_id = :industry_id"
            await db_conn.execute(text(update_statement), {"end_date": end_date, "industry_id": industry_id})

            await db_conn.commit()
            db_conn.close()
            db_session.close()
            
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Log: powerbi_date_update date change successful for industry_id =', industry_id)
            return "Data update completed"
        except Exception as e:
            print(f'{datetime.now().strftime("[%d/%b/%Y %H:%M:%S]")}  Error: powerbi_date_update prod error :-', e)
            raise e