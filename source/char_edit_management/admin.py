from sqladmin import ModelView

from source.char_edit_management.models import Shop


class ShopAdmin(ModelView, model=Shop):
    column_list = ['id', 'title', 'is_active']
    column_searchable_list = ['title']
