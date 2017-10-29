import sqlite3

#also creates a file
def openDb(path):
    db = sqlite3.connect(path)
    return db

def createCursor(db):
    c = db.cursor()
    return c

#types : text, integer, real, numeric, blob
#tableName is a string, fields is an array, types is an arr of the same length
def createTable(tableName, fields, types, cursor):
    parameter = '('
    for i in range(len(fields)):
        #print i
        parameter += fields[i] + " " + types[i] + ", "
    parameter = parameter[0:-2] + ");"
    create = "CREATE TABLE " + tableName + " " + parameter
    print "\n\n" + create + "\n\n"
    cursor.execute(create)


#NOTE: when putting in a string in the values array u have to do this: "'josh'"
#values is an array with values to insert for that row
def insertRow (tableName, fields, values, cursor):
    parameter = ' ('

    for field in fields:
        parameter += field + ", "
    parameter = parameter[0:-2] + ") VALUES ("
    #print parameter

    for value in values:
        val = str(value)
        if isinstance(value, basestring):
            val = "'" + val + "'"
        parameter += val + ", "
    parameter = parameter[0:-2] + ");"

    insert = "INSERT INTO " + tableName + parameter
    print "\n\n" + insert + "\n\n"

    cursor.execute(insert)



#condition is string type and follows WHERE statement for UPDATE
def update (tableName, field, newVal, condition, cursor):
    update = "UPDATE " + tableName + " SET " + field + " = " + str(newVal)
    if len(condition) != 0:
        update += " WHERE " + condition + ";"

    print "\n\n" + update + "\n\n"
    cursor.execute(update)


def display(tableName, fields, cursor):
    view = cursor.execute('SELECT * FROM ' + tableName + ';')

    table = ''
    for field in fields:
        table += field + "| "

    table = table[0:-2]
    table += "$|$\n"

    for item in view:
        for content in item:
            table +=  str(content) + "| "
        table = table[0:-2]
        table += "$|$\n"#unique delimiter that won't show up in text

    return table

def commit(db):
    db.commit()

def closeFile(db):
    db.close()


#TEST---------------------
'''
dbTest = openDb('../data/stories.db')
cursorTest = createCursor(dbTest)
#for the next line i tried making a column name "stupid?" but it gave me a syntax error???
createTable('students', ['grade', 'name' , 'stupid'], ['NUMERIC', 'TEXT', 'INTEGER'], cursorTest)
insertRow('students' , ['grade', 'name' , 'stupid'] , [89.5 , "'josh'", 0] , cursorTest)
insertRow('students' , ['grade', 'name' , 'stupid'] , [99 , "'allie'", 1] , cursorTest)
insertRow('students' , ['grade', 'name' , 'stupid'] , [93 , "'betty'", 1] , cursorTest)
update('students', 'stupid', 0, 'name = "betty"',cursorTest)

print display('students' , ['grade', 'name' , 'stupid'], cursorTest)
commit(dbTest)
closeFile(dbTest)
'''

#Creating the actual db

if __name__ == "__main__":
    #Creating the database
    dbStory = openDb("data/stories.db")
    cursor = createCursor(dbStory)


    createTable('mainStories',['title','storyID', 'timeLast', 'lastAdd','storyFile','lastEditor'] ,['TEXT', 'INTEGER PRIMARY KEY AUTOINCREMENT','TEXT', 'TEXT', 'TEXT', 'TEXT'], cursor)

    createTable('userStories', ['username', 'storyID' , 'myAddition'], ['TEXT' , 'TEXT' , 'TEXT'],cursor)


    createTable('accounts', ['username', 'password'], ['TEXT', 'TEXT'], cursor)

    commit(dbStory)
    closeFile(dbStory)
