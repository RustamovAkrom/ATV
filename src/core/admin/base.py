from sqladmin import ModelView


class BaseAdmin(ModelView):
    can_create = False
    can_edit = False
    can_delete = False
    can_view_details = True
    can_export = True

    page_size = 50

    column_default_sort = ("id", True)

    # def is_accessible(self, request):
    #     # TODO: integration with JWT / RBAC
    #     return True
