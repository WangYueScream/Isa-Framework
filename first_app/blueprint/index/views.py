from isafk import redirect, session, simple_template
from core.base_view import BaseView
from core.base_view import SessionView


class Index(SessionView):
    def get(self, request, *args, **options):
        user = session.get_item(request, 'user')
        return simple_template('index/index.html', user=user, hello='你好，', world="世界")

    def post(self, request, *args, **options):
        return '<h1>Post to Index<h1/>'


class Login(BaseView):
    def get(self, request, *args, **options):
        return simple_template('index/login.html')

    def post(self, request, *args, **options):
        data = request.form.to_dict()
        if 'user' in data:
            user = data.get('user').encode('utf-8').decode("utf-8")
            session.push(request, 'user', user)
        return redirect('/')


class Logout(SessionView):
    def get(self, request, *args, **options):
        return simple_template('index/logout.html')

    def post(self, request, *args, **options):
        if 'user' in session.map(request):
            session.pop(request, 'user')
        return redirect('/login')


class JsonTest(SessionView):
    def get(self, request, *args, **options):
        return [{'Hello': "world"}]
