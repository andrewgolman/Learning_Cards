import psycopg2
from db.enums import *

base = psycopg2.connect("dbname='cardkeepersample' user='andrew' host='localhost' password='1234'")
cursor = base.cursor()

# Wrapped queries in alphabetic order


def add_user(user):
    query = """INSERT INTO users (user_id, name, general_goal, weekly_goal, notifications_learn, notifications_stats, joined)
                VALUES (%s, %s, %s, %s, %s, %s, current_date);"""
    cursor.execute(query, tuple(user))
    base.commit()


def active_packs(user_id, start=0, count=10):
    query = """SELECT packs.pack_id, packs.name FROM user_packs, packs WHERE packs.pack_id = user_packs.pack_id
                AND user_packs.status = %s AND user_id = %s ORDER BY pack_id
                OFFSET %s LIMIT %s;"""
    cursor.execute(query, (CardStatusType.ACTIVE.value, user_id, start, count))
    return cursor.fetchall()


def delete_pack(pack_id):
    owner_id = get_pack(pack_id)['owner_id']
    cursor.execute(
        'DELETE FROM cards WHERE pack_id = %s;',
        (pack_id,)
    )
    cursor.execute(
        'DELETE FROM user_packs WHERE pack_id = %s;',
        (pack_id,)
    )
    cursor.execute(
        'DELETE FROM packs WHERE pack_id = %s;',
        (pack_id,)
    )
    base.commit()


def get_pack(pack_id):
    query = 'SELECT name, owner_id, privacy FROM packs WHERE pack_id = %s;'
    cursor.execute(query, (pack_id,))
    name, owner_id, privacy = cursor.fetchone()
    return {
        'pack_id': pack_id,
        'name': name,
        'owner_id': owner_id,
        'privacy': privacy
    }


def if_registered(user_id):
    query = "SELECT * FROM users WHERE users.user_id = %s;"
    cursor.execute(query, (user_id,))
    return True if len(cursor.fetchall()) else False


def if_username_taken(username):
    query = "SELECT * FROM users WHERE users.name = %s;"
    cursor.execute(query, (username,))
    return True if len(cursor.fetchall()) else False


def cards_for_learning(user_id):
    query = """SELECT cards.front, cards.back, cards.comment FROM user_cards, cards
                WHERE user_cards.card_id = cards.card_id AND
                user_id = %s AND cards.type = %s"""
    cursor.execute(query, (user_id, CardType.SHORT))
    return cursor.fetchall()


def new_card(front, back):
    query = "INSERT INTO cards (front, back) VALUES (%s, %s);"
    cursor.execute(query, (front, back))
    base.commit()


def new_pack(name, owner, privacy=PrivacyType.PUBLIC, status=CardStatusType.ACTIVE, cards=[]):
    if isinstance(privacy, PrivacyType):
        privacy = privacy.value
    if isinstance(status, CardStatusType):
        status = status.value

    query = "INSERT INTO packs (name, owner_id, privacy) VALUES (%s, %s, %s);"
    cursor.execute(query, (name, owner, privacy))

    query = "SELECT pack_id FROM packs WHERE name = %s AND owner_id = %s;"
    cursor.execute(query, (name, owner))

    query = "INSERT INTO user_packs (user_id, pack_id, status) VALUES (%s, %s, %s);"
    pack_id = cursor.fetchone()[0]
    cursor.execute(query, (owner, pack_id, status))

    for front, back in cards:
        query = "INSERT INTO cards (pack_id, front, back, type) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (pack_id, front, back, CardType.SHORT.value))

    base.commit()
    return pack_id


def select_cards(user_id, pack_id):
    print(user_id, pack_id)
    query = """SELECT cards.card_id, cards.front, cards.back, cards.comment FROM cards, user_cards
                WHERE cards.card_id = user_cards.card_id
                AND user_cards.status = %s
                AND cards.pack_id = %s
                AND user_cards.user_id = %s"""
    cursor.execute(query, ('Active', pack_id, user_id))
    return cursor.fetchall()


def update_card_data(user_id, card_id, answer):
    query = """UPDATE user_cards SET times_reviewed = times_reviewed+1, correct_answers = correct_answers+%s
                WHERE user_id = %s AND card_id = %s"""
    cursor.execute(query,  (answer, user_id, card_id))
    base.commit()


def update_card_status(user_id, card_id, status):
    query = """UPDATE user_cards SET status = %s
                WHERE user_id = %s AND card_id = %s"""
    cursor.execute(query, (status, user_id, card_id))
    base.commit()


def update_pack_name(pack_id, new_name):
    query = 'UPDATE packs SET name = %s WHERE pack_id = %s;'
    cursor.execute(query, (new_name, pack_id))
    base.commit()


def update_pack_privacy(pack_id, new_privacy):
    if isinstance(new_privacy, PrivacyType):
        new_privacy = new_privacy.value

    query = 'UPDATE packs SET privacy = %s WHERE pack_id = %s;'
    cursor.execute(query, (new_privacy, pack_id))
    base.commit()


def update_pack_status(user_id, pack_id, status):
    query = """UPDATE user_cards SET status = %s
                WHERE user_id = %s AND card_id = %s"""
    cursor.execute(query, (status, user_id, pack_id))
    base.commit()
