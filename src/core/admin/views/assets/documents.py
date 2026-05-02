from core.admin.base import BaseAdmin
from db.models.documents.document import Document
from db.models.documents.document_file import DocumentFile


class DocumentAdmin(BaseAdmin, model=Document):
    name = "Document"
    name_plural = "Documents"
    icon = "fa-solid fa-file"

    column_list = [
        "id",
        "title",
        "document_type",
        "asset",
        "created_by",
        "status",
        "created_at",
    ]

    column_searchable_list = ["title"]

    column_formatters = {
        "asset": lambda m, _: m.asset.name if m.asset else None,
        "created_by": lambda m, _: m.created_by.full_name if m.created_by else None,
    }


class DocumentFileAdmin(BaseAdmin, model=DocumentFile):
    name = "Document File"
    name_plural = "Document Files"
    icon = "fa-solid fa-file-alt"

    column_list = [
        "id",
        "document",
        "file_name",
        "file_path",
        "file_size",
        "content_type",
    ]

    column_formatters = {
        "document": lambda m, _: m.document.title if m.document else None,
    }
