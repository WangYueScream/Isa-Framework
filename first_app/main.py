from isafk import ISAApp, session, redirect, render_file, simple_template, render_json
from isafk.dbconnector import BaseDB

from controller.index import user_controller


#db_conn = BaseDB(user='Your user', password='Your password', database='Your database')
db_conn = BaseDB(user='root', password='root,./123', database='shadow_db')
app = ISAApp()


app.load_controller(user_controller)

def checkLogin(request):
    if 'user' in session.map(request):
        if session.map(request)['user']:
            return True

    return False


@app.route('/api2', methods=['GET', 'POST'])
def api2(request):
    if checkLogin(request):

        def get():
            ret = db_conn.execute('SELECT * FROM %s' % "t_server_list")
            if ret.suc:
                return render_json(ret.result)
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
    app.run(host='0.0.0.0', port=8000, use_debugger=True, threaded=True)
