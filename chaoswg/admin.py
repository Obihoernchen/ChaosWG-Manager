from flask import redirect
from flask_admin import Admin, AdminIndexView, expose
from flask_admin.contrib.peewee import ModelView
from flask_admin.form import SecureForm
from flask_admin.menu import MenuLink
from flask_login import current_user

from chaoswg.models import User, Task, History


# Custom flask-admin classes for authentication
class AuthAdminModelView(ModelView):
    form_base_class = SecureForm

    @staticmethod
    def is_accessible(**kwargs):
        return current_user.is_authenticated


class AuthAdminUserModelView(AuthAdminModelView):
    column_exclude_list = ['password']


class AuthAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect('/login')
        return super(AuthAdminIndexView, self).index()


def init_admin(app):
    """
    initializes the flask-admin interface
    :param app:
    :return:
    """
    admin = Admin(app, index_view=AuthAdminIndexView(), name='ChaosWG Manager Admin',
                  template_mode='bootstrap3')
    admin.add_link(MenuLink(name='Back Home', url='/tasks'))
    admin.add_view(AuthAdminModelView(Task))
    admin.add_view(AuthAdminUserModelView(User))
    admin.add_view(AuthAdminModelView(History))
