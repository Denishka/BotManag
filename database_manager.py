import psycopg2


def get_connection_to_database():
    return psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='127.0.0.1')


def init_database():
    conn = get_connection_to_database()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions(
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_list (
        id SERIAL PRIMARY KEY,
        chat_id VARCHAR NOT NULL UNIQUE
        )
    ''')

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invitation_links (
            link TEXT,
            description TEXT,
            region_id INTEGER REFERENCES regions (id)
        )
    """)

    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL UNIQUE,
                username VARCHAR
            )
        """)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_regions(
            user_id BIGINT REFERENCES users (user_id),
            region_id INTEGER REFERENCES regions (id),
            unique(user_id, region_id)
        )
    ''')
    conn.commit()


def execute_query(query, params=None):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()

    conn.close()
    return result


def execute_and_commit_query(query, params):
    with get_connection_to_database() as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, params)
            conn.commit()


def get_chat_ids():
    query = 'SELECT chat_id FROM chat_list'
    return execute_query(query)


def get_all_regions():
    query = "SELECT * FROM regions"
    return execute_query(query)


def delete_user_from_database(user_id):
    delete_user_relations(user_id)

    query = "DELETE FROM users WHERE user_id = %s"
    params = (user_id,)
    execute_and_commit_query(query, params)


def delete_user_relations(user_id):
    query = "DELETE FROM user_regions WHERE user_id = %s"
    params = (user_id,)
    execute_and_commit_query(query, params)


async def add_user_to_regions(user_id, username, region_ids):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id FROM users WHERE user_id = %s
    """, (user_id,))
    existing_user = cursor.fetchone()

    if existing_user is None:
        cursor.execute("""
            INSERT INTO users (user_id, username)
            VALUES (%s, %s)
            RETURNING id
        """, (user_id, username))

        for region_id in region_ids:
            cursor.execute("""
                INSERT INTO user_regions (user_id, region_id)
                VALUES (%s, %s)
            """, (user_id, region_id))
    else:
        return "Такой пользователь уже существует"

    conn.commit()


def insert_user_to_database(user):
    query = """
        INSERT INTO users (user_id, username, full_name) VALUES (%s, %s, %s)
    """
    params = (user.id, user.username, user.full_name)
    execute_and_commit_query(query, params)


def get_user_by_username_from_database(username):
    query = "SELECT * FROM users WHERE username = %s"
    params = (username,)
    result = execute_query(query, params)
    if result:
        return result[0]
    else:
        return None

def get_user_by_id_from_database(user):
    query = "SELECT * FROM users WHERE user_id = %s"
    params = (user.id,)
    return execute_query(query, params)[0]


def get_invite_links_for_region(region_id):
    conn = get_connection_to_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT link
        FROM invitation_links
        WHERE region_id = %s
    """, (region_id,))

    return [row[0] for row in cursor.fetchall()]


def add_links_to_database(links, description, region_id):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO invitation_links (link, description, region_id)
        VALUES (%s, %s, %s)
    """, (links, description, region_id))
    conn.commit()


def get_invite_links_for_user(user_id):
    conn = get_connection_to_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT region_id
        FROM user_regions
        WHERE user_id = %s
    """, (user_id,))
    user_regions = [row[0] for row in cursor.fetchall()]

    invite_links = []
    for region_id in user_regions:
        cursor.execute("""
            SELECT link, description
            FROM invitation_links
            WHERE region_id = %s
        """, (region_id,))
        invite_links.extend(cursor.fetchall())

    conn.close()
    return invite_links


def get_region_name_by_id(region_id):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM regions WHERE id = %s", (region_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None


def get_region_id_from_last_message(message_text):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    region_name = message_text
    cursor.execute("""
        SELECT id FROM regions
        WHERE name = %s
    """, (region_name,))
    region = cursor.fetchone()

    return region['id']


def add_start_regions():
    conn = get_connection_to_database()
    cursor = conn.cursor()
    regions = ['Ростов', 'Баку', 'Вне РФ', 'Удаленно']
    for region in regions:
        cursor.execute("""
            SELECT * FROM regions WHERE name = %s
        """, (region,))
        result = cursor.fetchone()
        if result is None:
            cursor.execute("""
                INSERT INTO regions (name)
                VALUES (%s)
            """, (region,))
    conn.commit()


