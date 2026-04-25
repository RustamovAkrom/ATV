import csv
import io
import json

from fastapi.encoders import jsonable_encoder

from core.exceptions.errors import BadRequest


class ExportService:
    MAX_EXPORT_ROWS = 10_000

    def __init__(self, asset_repo):
        self.asset_repo = asset_repo

    async def ensure_exportable(self, filters) -> None:
        total = await self.asset_repo.count_for_export(filters)
        if total > self.MAX_EXPORT_ROWS:
            raise BadRequest(
                f"Export exceeds maximum row limit of {self.MAX_EXPORT_ROWS}"
            )

    async def stream_assets(self, filters, format_: str):
        if format_ == "csv":
            async for chunk in self._stream_csv(filters):
                yield chunk
            return
        async for chunk in self._stream_json(filters):
            yield chunk

    async def _stream_csv(self, filters):
        header_buffer = io.StringIO()
        writer = csv.writer(header_buffer)
        writer.writerow(
            [
                "id",
                "name",
                "type",
                "status",
                "asset_tag",
                "serial_number",
                "owner_id",
                "region",
                "service",
                "warehouse",
            ]
        )
        yield header_buffer.getvalue()

        async for asset in self.asset_repo.iter_for_export(filters):
            row_buffer = io.StringIO()
            writer = csv.writer(row_buffer)
            writer.writerow(
                [
                    str(asset.id),
                    asset.name,
                    asset.type,
                    asset.status.value,
                    asset.asset_tag or "",
                    asset.serial_number or "",
                    str(asset.owner_id) if asset.owner_id else "",
                    asset.region.name if asset.region else "",
                    asset.service.name if asset.service else "",
                    asset.warehouse.name if asset.warehouse else "",
                ]
            )
            yield row_buffer.getvalue()

    async def _stream_json(self, filters):
        first = True
        yield "["
        async for asset in self.asset_repo.iter_for_export(filters):
            if not first:
                yield ","
            first = False
            yield json.dumps(
                jsonable_encoder(
                    {
                        "id": str(asset.id),
                        "name": asset.name,
                        "type": asset.type,
                        "status": asset.status.value,
                        "asset_tag": asset.asset_tag,
                        "serial_number": asset.serial_number,
                        "owner_id": str(asset.owner_id) if asset.owner_id else None,
                        "region": asset.region.name if asset.region else None,
                        "service": asset.service.name if asset.service else None,
                        "warehouse": asset.warehouse.name if asset.warehouse else None,
                    }
                )
            )
        yield "]"
