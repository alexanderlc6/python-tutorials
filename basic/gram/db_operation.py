import sqlite3

# Query with criteria
criteria_birthday = input('Please input student birthday(yyyyMMdd):')

# Insert data input
i_name = input('Please input student name:')
i_sex = input('Please input student sex:')
i_birthday = input('Please input student birthday(yyyyMMdd):')

# Update data input
i_id = input('Please input update student ID:')
i_name = input('Please input new student name:')

# Delete data input
i_id = input('Please input delete student ID:')

# Query with criteria
try:
    con = sqlite3.connect('school_db.db')
    cursor = con.cursor()

    query_sql = 'select s_id, s_name, s_sex, s_birthday from student where s_birthday < ?'
    cursor.execute(query_sql, [criteria_birthday])
    result_set = cursor.fetchall()
    for row in result_set:
        print('Student ID:{0}, Name:{1}, Sex:{2}, Birthday:{3}'.format(row[0], row[1], row[2], row[3]))
except sqlite3.Error as e:
    print('DB query occur error:{}'.format(e))

# Insert data
try:
    con = sqlite3.connect('school_db.db')
    cursor = con.cursor()

    insert_sql = 'insert into student(s_name, s_sex, s_birthday) values(?,?,?)'
    cursor.execute(insert_sql, [i_name, i_sex, i_birthday])
    con.commit()
    print('Insert student success!')
except sqlite3.Error as e:
    print('DB insert occur error:{}'.format(e))
    con.rollback()

# Update data
try:
    con = sqlite3.connect('school_db.db')
    cursor = con.cursor()

    update_sql = 'update student set s_name = ? where s_id = ?'
    cursor.execute(update_sql, [i_name, i_id])
    con.commit()
    print('Update student success!')
except sqlite3.Error as e:
    print('DB update occur error:{}'.format(e))
    con.rollback()

# Delete data
try:
    con = sqlite3.connect('school_db.db')
    cursor = con.cursor()

    delete_sql = 'delete from student where s_id = ?'
    cursor.execute(delete_sql, [i_id])
    con.commit()
    print('Delete student {} success!'.format(i_id))
except sqlite3.Error as e:
    print('DB delete occur error:{}'.format(e))
    con.rollback()

finally:
    if cursor:
        cursor.close()
    if con:
        con.close()