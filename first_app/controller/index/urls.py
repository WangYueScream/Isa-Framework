from . import views

url_maps = [
    {
        'url': '/',
        'view': views.Index,
        'endpoint': 'index'
    },
    {
        'url': '/login',
        'view': views.Login,
        'endpoint': 'login'
    },
    {
        'url': '/logout',
        'view': views.Logout,
        'endpoint': 'logout'
    },
    {
        'url': '/api',
        'view': views.JsonTest,
        'endpoint': 'api'
    }
]
