from instagrapi import types
from typing import List, AnyStr
from instagrapi import Client
from pathlib import Path
import logging

INSTAGRAM_USERNAME = 'flask_project_admin'
INSTAGRAM_PASSWORD = 'armanjt77'


def start(user, password):
    client = Client()
    session_file = Path(f"{user}.json")

    try:
        client.load_settings(Path("./user_settings/" + str(session_file)))
    except Exception as e:
        logging.error("Could not load session settings: %s", e)

    try:
        client.login(username=user, password=password)
        logging.info('Logged in successfully')
        client.dump_settings(Path("./user_settings/" + str(session_file)))
    except Exception as e:
        logging.error("Login failed: %s", e)
    return client


def find_user_id(client: Client,username):
    return client.user_id_from_username(username)

def send_direct_from_specific_comment(client: Client, list_of_users: List[AnyStr], ANSWER: AnyStr):
    logging.info('Sending direct comment')
    for user in list_of_users:
        client.direct_send(
            ANSWER,
            user_ids=[int(user)]
        )
        logging.info(f'Answer to user {user} sent...')

# cl = start('flask_project_admin','armanjt77')
# print(send_direct_from_specific_comment(cl, list_of_users=['38282936051'],ANSWER='salam'))
# print(find_user_id(cl,INSTAGRAM_USERNAME))
