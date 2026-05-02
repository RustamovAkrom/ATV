from sqladmin import ModelView


class BaseAdmin(ModelView):
    can_create = True
    can_edit = True
    can_delete = True
    can_view_details = True

    page_size = 50

    column_default_sort = ("id", True)

    # def is_accessible(self, request):
    #     # TODO: integration with JWT / RBAC
    #     return True
