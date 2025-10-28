from flask_mysql_connector import MySQL

mysql = MySQL()

# --- Users ---
def get_user_by_username(username):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT user_id, password_hash FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()
    cursor.close()
    return row

def create_user(username, password_hash):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s,%s)", (username, password_hash))
    mysql.connection.commit()
    cursor.close()

# --- Tanks ---
def get_tanks(user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT tank_id, tank_name, tank_volume, tank_type, created_at FROM tanks WHERE user_id=%s ORDER BY created_at DESC", (user_id,))
    tanks = cursor.fetchall()
    cursor.close()
    return tanks

def add_tank(user_id, name, volume, tank_type):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO tanks (user_id, tank_name, tank_volume, tank_type) VALUES (%s,%s,%s,%s)", (user_id, name, volume, tank_type))
    mysql.connection.commit()
    cursor.close()

def delete_tank(tank_id, user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM tanks WHERE tank_id=%s AND user_id=%s", (tank_id, user_id))
    mysql.connection.commit()
    cursor.close()

# --- Water Tests ---
def get_tests(tank_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""SELECT water_test_id, date_observed, ammonia, nitrite, nitrate, ph, salinity, temperature, phosphate, calcium, notes
                      FROM water_tests WHERE tank_id=%s ORDER BY date_observed DESC""", (tank_id,))
    tests = cursor.fetchall()
    cursor.close()
    return tests

def add_test(tank_id, data):
    cursor = mysql.connection.cursor()
    cursor.execute("""INSERT INTO water_tests
        (tank_id, date_observed, ammonia, nitrite, nitrate, ph, salinity, temperature, phosphate, calcium, notes)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
        (tank_id, data["date_observed"], data["ammonia"], data["nitrite"], data["nitrate"],
         data["ph"], data["salinity"], data["temperature"], data["phosphate"], data["calcium"], data["notes"]))
    mysql.connection.commit()
    cursor.close()

def delete_test(test_id, user_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""DELETE wt FROM water_tests wt
                      JOIN tanks t ON wt.tank_id=t.tank_id
                      WHERE wt.water_test_id=%s AND t.user_id=%s""", (test_id, user_id))
    mysql.connection.commit()
    cursor.close()