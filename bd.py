from mysql.connector import connect, Error

def connection_(password, user):
    try:
        with connect(
                host="localhost",
                password=password,
                user=user,
                database="mydb",
        ) as connection:
            select_query = "SELECT * FROM apartments"
            with connection.cursor() as cursor:
                cursor.execute(select_query)
                result1 = cursor.fetchall()
            select_query = "SELECT first_name, password_hash, role FROM users"
            d = []
            with connection.cursor() as cursor:
                cursor.execute(select_query)
                result2 = cursor.fetchall()
                for i in result2:
                    d.append(i)
            return result1, d
    except Error as e:
        return None, str(e)

def add_user(password, user, first_name, password_hash):
    try:
        with connect(
                host="localhost",
                password=password,
                user=user,
                database="mydb",
        ) as connection:
            insert_users_query = """
            INSERT INTO users (first_name, password_hash, role)
            VALUES (%s, %s, %s)
            """
            users = [(first_name, password_hash, 'user')]
            with connection.cursor() as cursor:
                cursor.executemany(insert_users_query, users)
                connection.commit()
            return True
    except Error as e:
        return False, str(e)

def add_apartment(password, user, area, number_of_rooms, price, address):
    try:
        with connect(
                host="localhost",
                password=password,
                user=user,
                database="mydb",
        ) as connection:
            if all(x != '' for x in [area, number_of_rooms, price, address]):
                insert_apartments_query = """
                INSERT INTO apartments (area, number_of_rooms, price, address)
                VALUES (%s, %s, %s, %s)
                """
                apartments = (area, number_of_rooms, price, address)
                with connection.cursor() as cursor:
                    cursor.execute(insert_apartments_query, apartments)
                    connection.commit()
                return True, None
            else:
                return False, "Vse polya dolzhni byt zapolneny"
    except Error as e:
        return False, str(e)

def edit_apartment_bd(password, user, array):
    try:
        with connect(
                host="localhost",
                password=password,
                user=user,
                database="mydb",
        ) as connection:
            sql_update_query = """
            UPDATE apartments
            SET area = %s, number_of_rooms = %s, price = %s, address = %s
            WHERE id = %s
            """
            input_data = (array[1], array[2], array[3], array[4], array[0])
            with connection.cursor() as cursor:
                cursor.execute(sql_update_query, input_data)
                connection.commit()
            return True
    except Error as e:
        return False, str(e)

def delete_apartment_bd(password, user, id):
    try:
        with connect(
                host="localhost",
                password=password,
                user=user,
                database="mydb",
        ) as connection:
            delete_query = "DELETE FROM apartments WHERE id = %s"
            with connection.cursor() as cursor:
                cursor.execute(delete_query, (id,))
                connection.commit()
            return True
    except Error as e:
        return False, str(e)
