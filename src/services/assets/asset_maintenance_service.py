from uuid import UUID

from core.events.asset_events import AssetEventService
from core.exceptions.errors import NotFound
from core.security.access_control import AccessControl
from repositories.assets.asset_maintenance_repo import AssetMaintenanceRepository
from repositories.assets.asset_repo import AssetRepository
from schemas.assets.asset_maintenance import (
    AssetMaintenanceCreateSchema,
    AssetMaintenanceOutSchema,
    AssetMaintenanceUpdateSchema,
)
from schemas.auth.auth import CurrentUserSchema


class AssetMaintenanceService:
    """Сервис для управления техническим обслуживанием активов"""

    def __init__(
        self,
        repo: AssetMaintenanceRepository,
        asset_repo: AssetRepository,
        asset_events: AssetEventService,
    ):
        self.repo = repo
        self.asset_repo = asset_repo
        self.asset_events = asset_events

    async def _check_asset_access(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> None:
        """Проверить доступ к активу"""
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise NotFound(f"Asset {asset_id} not found")
        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

    async def create(
        self,
        asset_id: UUID,
        data: AssetMaintenanceCreateSchema,
        actor: CurrentUserSchema,
    ) -> AssetMaintenanceOutSchema:
        """Create a new maintenance record for an asset"""
        await self._check_asset_access(asset_id, actor)

        maintenance = await self.repo.create(
            {
                "asset_id": asset_id,
                "maintenance_type": data.maintenance_type.strip(),
                "performed_at": data.performed_at,
                "issues_found": (
                    data.issues_found.strip() if data.issues_found else None
                ),
                "performed_by_id": data.performed_by_id,
                "notes": data.notes.strip() if data.notes else None,
            }
        )

        await self.asset_events.maintenance_performed(
            asset_id=asset_id,
            actor_id=actor.id,
            maintenance_type=data.maintenance_type,
            performed_by_id=data.performed_by_id,
        )

        return self._to_out(maintenance)

    async def list_by_asset(
        self,
        asset_id: UUID,
        actor: CurrentUserSchema,
    ) -> list[AssetMaintenanceOutSchema]:
        """Получить все записи обслуживания актива"""
        await self._check_asset_access(asset_id, actor)
        records = await self.repo.get_by_asset(asset_id)
        return [self._to_out(r) for r in records]

    async def update(
        self,
        maintenance_id: UUID,
        data: AssetMaintenanceUpdateSchema,
        actor: CurrentUserSchema,
    ) -> AssetMaintenanceOutSchema:
        """Обновить запись обслуживания"""
        record = await self.repo.get(maintenance_id)
        if not record:
            raise NotFound(f"Maintenance record {maintenance_id} not found")

        await self._check_asset_access(record.asset_id, actor)

        update_data = data.model_dump(exclude_unset=True)
        if update_data:
            if "maintenance_type" in update_data:
                update_data["maintenance_type"] = update_data[
                    "maintenance_type"
                ].strip()
            if issues := update_data.get("issues_found"):
                update_data["issues_found"] = issues.strip()
            if notes := update_data.get("notes"):
                update_data["notes"] = notes.strip()

            updated = await self.repo.update(maintenance_id, update_data)
            if not updated:
                raise NotFound(f"Maintenance record {maintenance_id} not found")
            record = updated

        return self._to_out(record)

    async def delete(
        self,
        maintenance_id: UUID,
        actor: CurrentUserSchema,
    ) -> None:
        """Удалить запись обслуживания"""
        record = await self.repo.get(maintenance_id)
        if not record:
            raise NotFound(f"Maintenance record {maintenance_id} not found")

        await self._check_asset_access(record.asset_id, actor)
        await self.repo.delete(maintenance_id)

    def _to_out(self, record) -> AssetMaintenanceOutSchema:
        performed_by_name = None
        if record.performed_by:
            performed_by_name = (
                record.performed_by.full_name or record.performed_by.login
            )

        return AssetMaintenanceOutSchema(
            id=record.id,
            asset_id=record.asset_id,
            maintenance_type=record.maintenance_type,
            performed_at=record.performed_at,
            issues_found=record.issues_found,
            performed_by_id=record.performed_by_id,
            performed_by_name=performed_by_name,
            notes=record.notes,
            created_at=record.created_at,
            updated_at=record.updated_at,
        )
