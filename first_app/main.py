from isafk import ISAApp, session, redirect, render_file, simple_template
from isafk.dbconnector import BaseDB

from blueprint.index import user_print


db_conn = BaseDB(user='Your user', password='Your password', database='Your database')
app = ISAApp()

app.register_blueprint(user_print)


def checkLogin(request):
    if 'user' in session(request):
        if session(request)['user']:
            return True

    return False


@app.route('/api2', methods=['GET', 'POST'])
def api2(request):
    if checkLogin(request):

        def get():
            ret = db_conn.select('SELECT * FROM %s' % "Your table name")
            if ret.Suc:
                return ret.Result
            else:
                return {}

        def post():
            return 'POST ME'

        method_meta = {
            'GET': get,
            'POST': post
        }

        return method_meta[request.method]()

    else:
        return redirect("/login")


@app.route('/upload', methods=['GET', 'POST'])
def hello_world(request):
    if request.method == 'GET':
        return simple_template("upload.html")
    else:
        file = request.files['up_file']
        file.save('/Users/c0hb1rd/FlaskApp/UploadWeb/' + file.filename)
        return '<h1>Upload Success</h1>'


@app.route('/getfile')
def hello_file():
    return render_file('wsgi.py')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True, threaded=True)
