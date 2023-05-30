from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from django.conf import settings

db_settings = settings.DATABASES['default']

def get_connection_url(database_name):
    package = "mysql+pymysql"
    package = "mysql+pymysql"
    user_name = db_settings['USER']
    password = db_settings['PASSWORD']
    database_name = database_name
    host_name = db_settings['HOST']
    port = db_settings['PORT']

    database_connection_url = package + "://" + user_name + ":" + password + "@" + host_name + ":" + port + "/" + database_name
    #example -> 'mysql+pymysql://root:manoj123@127.0.0.1:3306/app_reviews'

    return database_connection_url

def get_db_connection(database_name):
    database_connection_url = get_connection_url(database_name)

    # connect_args = {'ssl': {'ttls': True}}
    # engine = create_engine(database_connection_url, encoding='latin1', echo=False, connect_args=connect_args)
    
    connect_args = {'charset': 'latin1'}
    engine = create_engine(database_connection_url,
                               echo=False, connect_args=connect_args)
    
    db_conn = engine.connect()

    dbSession = sessionmaker(bind=engine)
    db_session = dbSession()

    return db_session, db_conn

def InsertORUpdate(data, db_conn, db_session):
    cur = db_conn.connection.cursor()
    query = """
    INSERT INTO main_data (
        player_id, start_date, end_date, parameter_id, value, date_created, source, parametertree_id
    ) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) as value_list
    ON DUPLICATE KEY UPDATE value = value_list.value, date_created = value_list.date_created
    """
    cur.executemany(query, data)
    db_conn.connection.commit()
    db_session.commit()
    # db_conn.close()

def par_val_df(players, db_conn):
    players_str = str(players).replace("[", "(").replace("]", ")")
    all_data_df = pd.read_sql(text(f"SELECT player_id, start_date, parameter_id, value from main_data where player_id in {players_str};"), db_conn)
    all_data_df['start_date'] = pd.to_datetime(all_data_df['start_date']).dt.date
    transformed_df = all_data_df.pivot_table(index = ["start_date", "player_id"], columns= "parameter_id", values= "value")

    return transformed_df