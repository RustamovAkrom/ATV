# core/cache/tags.py
# class CacheTags:
#     # Asset tags
#     ASSET_LIST = "asset:list"
#     ASSET_DETAIL = "asset:detail"
#     ASSET_HISTORY = "asset:history"
#     ASSET_EXPORT = "asset:export"

#     # Image tags
#     IMAGE_LIST = "asset:image:list"
#     IMAGE_FILE = "asset:image:file"

#     # Repair tags
#     REPAIR_DETAIL = "repair:detail"

#     # All tags for invalidation when asset changes
#     ASSET_ALL = (ASSET_LIST, ASSET_DETAIL, ASSET_HISTORY, ASSET_EXPORT)


# Использование:
# from core.cache.tags import CacheTags

# @invalidate_cache(tags=CacheTags.ASSET_ALL + (CacheTags.IMAGE_LIST,))
