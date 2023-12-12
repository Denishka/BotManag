import psycopg2


def get_connection_to_database():
    return psycopg2.connect(dbname='postgres', user='postgres', password='postgres', host='127.0.0.1')


def init_database():
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT NOT NULL,
                username VARCHAR
            )
        """)
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS invitation_links (
                id SERIAL PRIMARY KEY,
                link TEXT
            )
        """)

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS regions(
            id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_regions(
            user_id BIGINT REFERENCES users (id),
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


def get_chat_ids(self):
    query = 'SELECT chat_id FROM chat_list'
    return self.execute_query(query)


def get_all_regions():
    query = "SELECT * FROM regions"
    return execute_query(query)


def delete_user_from_database(user_id):
    query = "DELETE FROM users WHERE user_id = %s"
    params = (user_id,)
    execute_and_commit_query(query, params)


async def add_user_to_regions(user_id, username, region_ids):
    conn = get_connection_to_database()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (user_id, username)
        VALUES (%s, %s)
        RETURNING id
    """, (user_id, username))
    user_db_id = cursor.fetchone()[0]

    # Добавляем связи пользователя с регионами
    for region_id in region_ids:
        cursor.execute("""
            INSERT INTO user_regions (user_id, region_id)
            VALUES (%s, %s)
        """, (user_db_id, region_id))

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
    return execute_query(query, params)[0]


def get_user_by_id_from_database(user):
    query = "SELECT * FROM users WHERE user_id = %s"
    params = (user.id,)
    return execute_query(query, params)[0]

# def get_user_regions(user_id):
#     conn = get_connection_to_database()
#     cursor = conn.cursor()
#
#     cursor.execute("""
#         SELECT regions.name
#         FROM users
#         JOIN user_regions ON users.id = user_regions.user_id
#         JOIN regions ON user_regions.region_id = regions.id
#         WHERE users.user_id = %s
#     """, (user_id,))
#
#     return [row[0] for row in cursor.fetchall()]