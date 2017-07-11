import pymysql


class DBResult:
    Suc = False
    Result = None
    Err = None
    Rows = None

    def index_of(self, index):
        if self.Suc and isinstance(index, int) and self.Rows > index >= -self.Rows:
            return self.Result[index]

        return None

    def get_first(self):
        return self.index_of(0)

    def get_last(self):
        return self.index_of(-1)


class BaseDB:
    def __init__(self, user, password, database, host='127.0.0.1', port=3306, charset='utf8', cursor_class=pymysql.cursors.DictCursor):
        self.dbConn = None
        self.cursor = None
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.cursor_class = cursor_class

    # Return DBResult
    def select(self, sql, params=None):
        with pymysql.connect(host=self.host, user=self.user, port=self.port, passwd=self.password, db=self.database,
                             charset=self.charset,
                             cursorclass=self.cursor_class) as cursor:
            r = DBResult()
            try:
                if params is None or len(params) == 0 or type(params) != dict:
                    r.Rows = cursor.execute(sql)
                else:
                    r.Rows = cursor.execute(sql, params)
                r.Result = cursor.fetchall() if r.Rows != 0 else []
                for i in range(0, len(r.Result)):
                    for k, v in r.Result[i].items():
                        r.Result[i][k] = str(v)
                r.Suc = True
            except Exception as e:
                r.Err = e
                
        return r

    # Return DBResult
    def callProc(self, func, params=None):
        with pymysql.connect(host=self.host, user=self.user, port=self.port, passwd=self.password, db=self.database,
                             charset=self.charset,
                             cursorclass=self.cursor_class)  as cursor:

            r = DBResult()
            try:
                if params:
                    cursor.callproc(func, params)
                else:
                    cursor.callproc(func)
                r.Result = cursor.fetchall()
                r.Suc = True
            except Exception as e:
                r.Err = e

        return r

    # Return DBResult
    def execute(self, sql, params=None):
        self.dbConn = pymysql.connect(host=self.host, user=self.user, port=self.port, passwd=self.password, db=self.database,
                             charset=self.charset,
                             cursorclass=self.cursor_class) 

        cursor = self.dbConn.cursor()

        r = DBResult()
        try:
            if not params:
                r.Rows = cursor.execute(sql)
            else:
                r.Rows = cursor.execute(sql, params)
            r.Result = cursor.fetchall() if r.Rows != 0 else []
            r.Suc = True
            self.dbConn.commit()
        except Exception as e:
            r.Err = e
            print(e, 'execute Error')
            self.dbConn.rollback()

        try:
            cursor.close()
            self.dbConn.close()
        except Exception as e:
            r.Err = e

        return r

    # Return DBResult
    def insert(self, sql, params=None):
        r = self.execute(sql, params)
        return r

    def getLastID(self):
        r = self.execute("SELECT LAST_INSERT_ID()")
        r.Result = r.Result[0]['LAST_INSERT_ID()']
        return r

    # Return DBResult
    def getValue(self, sql, params=None):
        r = self.select(sql, params)

        if r.Suc:
            if r.Result:
                r.Result = r.Result[0]
            else:
                r.Result = -1
        return r
