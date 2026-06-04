from datetime import datetime
from decimal import Decimal
from typing import Any, cast
from uuid import UUID

from core.events.warehouse_events import WarehouseEventService
from core.exceptions.errors import BadRequest, Conflict, NotFound
from core.security.access_control import AccessControl
from db.models.warehouse.warehouse import Warehouse
from repositories.assets.asset_repo import AssetRepository
from repositories.assets.warehouse_repo import WarehouseRepository
from schemas.assets.part import PartCreateSchema
from schemas.assets.stock import StockMovementCreateSchema
from schemas.assets.warehouses import (
    WarehouseCreateSchema,
    WarehouseMoveRequest,
    WarehouseOutSchema,
    WarehouseUpdateSchema,
    WarehouseWithDetailsOutSchema,
)
from schemas.auth.auth import CurrentUserSchema
from schemas.pagination import PaginationParamsSchema
from utils.department import normalize_department_scope


class WarehouseService:
    def __init__(
        self,
        repo: WarehouseRepository,
        asset_repo: AssetRepository,
        warehouse_events: WarehouseEventService,
    ):
        self.repo = repo
        self.asset_repo = asset_repo
        self.warehouse_events = warehouse_events

    @staticmethod
    def _to_uuid(value: Any) -> UUID:
        return cast(UUID, UUID(str(value)))

    async def list_warehouses(
        self,
        pagination: PaginationParamsSchema,
        department_id: UUID | None = None,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
        is_active: bool | None = None,
    ) -> tuple[list[WarehouseOutSchema], int]:
        warehouses, total = await self.repo.list(
            region_id=region_id,
            service_id=service_id,
            is_active=is_active,
            limit=pagination.limit,
            offset=pagination.offset(),
        )

        items = []
        for warehouse in warehouses:
            assets_count = await self.repo.get_assets_count(self._to_uuid(warehouse.id))
            items.append(self._to_out_schema(warehouse, assets_count))

        return items, total

    async def get_warehouse(self, warehouse_id: UUID) -> WarehouseWithDetailsOutSchema:
        warehouse = await self.repo.get(warehouse_id)
        if warehouse is None:
            raise NotFound(f"Warehouse {warehouse_id} not found")

        assets_count = await self.repo.get_assets_count(warehouse_id)
        return self._to_details_schema(warehouse, assets_count)

    async def create_warehouse(self, data: WarehouseCreateSchema) -> WarehouseOutSchema:
        payload = data.model_dump(exclude_unset=True)
        payload = await normalize_department_scope(
            getattr(self.asset_repo, "session", None), payload
        )

        warehouse = await self.repo.create(payload)
        return self._to_out_schema(warehouse)

    async def update_warehouse(
        self,
        warehouse_id: UUID,
        data: WarehouseUpdateSchema | dict[str, Any],
    ) -> WarehouseOutSchema:
        warehouse = await self.repo.get(warehouse_id)
        if not warehouse:
            raise NotFound(f"Warehouse {warehouse_id} not found")

        if isinstance(data, dict):
            data = WarehouseUpdateSchema(**data)

        update_data = data.model_dump(exclude_unset=True)
        if update_data.get("department_id") is not None:
            update_data = await normalize_department_scope(
                getattr(self.asset_repo, "session", None), update_data
            )

        updated = await self.repo.update(warehouse_id, update_data)
        if updated is None:
            raise NotFound(f"Warehouse {warehouse_id} not found")
        return self._to_out_schema(updated)

    async def delete_warehouse(self, warehouse_id: UUID) -> None:
        warehouse = await self.repo.get(warehouse_id)
        if not warehouse:
            raise NotFound(f"Warehouse {warehouse_id} not found")

        assets_count = await self.repo.get_assets_count(warehouse_id)
        if assets_count > 0:
            raise Conflict(f"Cannot delete warehouse with {assets_count} assets")

        await self.repo.delete(warehouse_id)

    async def move_asset_to_warehouse(
        self,
        asset_id: UUID,
        data: WarehouseMoveRequest,
        actor: CurrentUserSchema,
    ) -> UUID:
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            asset.department_id,
            asset.region_id,
            asset.service_id,
        )

        warehouse = await self.repo.get(data.warehouse_id)
        if not warehouse:
            raise NotFound("Warehouse not found")

        if not warehouse.is_active:
            raise BadRequest("Warehouse is inactive")

        if (
            asset.department_id is not None
            and warehouse.department_id is not None
            and asset.department_id != warehouse.department_id
        ):
            raise BadRequest(
                "Warehouse department is incompatible with asset department"
            )

        if asset.region_id is not None and asset.region_id != warehouse.region_id:
            raise BadRequest("Warehouse region is incompatible with asset region")

        if (
            asset.service_id is not None
            and warehouse.service_id is not None
            and asset.service_id != warehouse.service_id
        ):
            raise BadRequest("Warehouse service is incompatible with asset service")

        asset.current_warehouse_id = self._to_uuid(warehouse.id)
        await self.asset_repo.flush()

        await self.warehouse_events.asset_moved_to_warehouse(
            asset_id=self._to_uuid(asset.id),
            actor_id=self._to_uuid(actor.id),
            warehouse_id=self._to_uuid(warehouse.id),
            warehouse_name=getattr(warehouse, "name", None),
        )

        return self._to_uuid(asset.id)

    def _to_out_schema(
        self, warehouse: Warehouse, assets_count: int = 0
    ) -> WarehouseOutSchema:
        created_at = getattr(warehouse, "created_at", datetime.utcnow())
        updated_at = getattr(warehouse, "updated_at", created_at)
        return WarehouseOutSchema(
            id=self._to_uuid(warehouse.id),
            name=warehouse.name,
            slug=getattr(warehouse, "slug", None),
            region_id=self._to_uuid(getattr(warehouse, "region_id", None)),
            department_id=(
                self._to_uuid(getattr(warehouse, "department_id", None))
                if getattr(warehouse, "department_id", None) is not None
                else None
            ),
            service_id=(
                self._to_uuid(getattr(warehouse, "service_id", None))
                if getattr(warehouse, "service_id", None) is not None
                else None
            ),
            manager_user_id=(
                self._to_uuid(getattr(warehouse, "manager_user_id", None))
                if getattr(warehouse, "manager_user_id", None) is not None
                else None
            ),
            is_active=getattr(warehouse, "is_active", True),
            created_at=created_at,
            updated_at=updated_at,
            assets_count=assets_count,
        )

    def _to_details_schema(
        self,
        warehouse: Warehouse,
        assets_count: int = 0,
    ) -> WarehouseWithDetailsOutSchema:
        created_at = getattr(warehouse, "created_at", datetime.utcnow())
        updated_at = getattr(warehouse, "updated_at", created_at)
        return WarehouseWithDetailsOutSchema(
            id=self._to_uuid(warehouse.id),
            name=warehouse.name,
            slug=getattr(warehouse, "slug", None),
            region_id=self._to_uuid(getattr(warehouse, "region_id", None)),
            department_id=(
                self._to_uuid(getattr(warehouse, "department_id", None))
                if getattr(warehouse, "department_id", None) is not None
                else None
            ),
            service_id=(
                self._to_uuid(getattr(warehouse, "service_id", None))
                if getattr(warehouse, "service_id", None) is not None
                else None
            ),
            manager_user_id=(
                self._to_uuid(getattr(warehouse, "manager_user_id", None))
                if getattr(warehouse, "manager_user_id", None) is not None
                else None
            ),
            is_active=getattr(warehouse, "is_active", True),
            created_at=created_at,
            updated_at=updated_at,
            assets_count=assets_count,
            region_name=getattr(getattr(warehouse, "region", None), "name", None),
            service_name=getattr(getattr(warehouse, "service", None), "name", None),
            manager_name=getattr(
                getattr(warehouse, "manager_user", None), "full_name", None
            ),
        )

    async def create_warehouse_legacy(
        self,
        name: str,
        region_id: UUID,
        service_id: UUID | None = None,
        manager_user_id: UUID | None = None,
        is_active: bool = True,
    ) -> WarehouseOutSchema:
        data = WarehouseCreateSchema(
            name=name,
            region_id=region_id,
            service_id=service_id,
            manager_user_id=manager_user_id,
            is_active=is_active,
        )
        return await self.create_warehouse(data)

    async def get_warehouse_legacy(
        self, warehouse_id: UUID
    ) -> WarehouseWithDetailsOutSchema:
        return await self.get_warehouse(warehouse_id)

    async def update_warehouse_legacy(
        self,
        warehouse_id: UUID,
        data: dict[str, Any],
    ) -> WarehouseOutSchema:
        update_data = WarehouseUpdateSchema(**data)
        return await self.update_warehouse(warehouse_id, update_data)

    async def delete_warehouse_legacy(self, warehouse_id: UUID) -> None:
        await self.delete_warehouse(warehouse_id)

    async def record_stock_in(
        self,
        warehouse_id: UUID,
        part_id: UUID,
        quantity: int,
        user_id: UUID,
    ) -> dict[str, Any]:
        if quantity <= 0:
            raise BadRequest("Quantity must be greater than zero")
        data = StockMovementCreateSchema(quantity=quantity, reference_type="manual")
        movement = await self.repo.record_stock_in(
            warehouse_id=warehouse_id,
            part_id=part_id,
            quantity=data.quantity,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            moved_by=user_id,
        )
        return self._to_movement_dict(movement)

    async def record_stock_out(
        self,
        warehouse_id: UUID,
        part_id: UUID,
        quantity: int,
        user_id: UUID,
    ) -> dict[str, Any]:
        if quantity <= 0:
            raise BadRequest("Quantity must be greater than zero")
        data = StockMovementCreateSchema(quantity=quantity, reference_type="manual")
        movement = await self.repo.record_stock_out(
            warehouse_id=warehouse_id,
            part_id=part_id,
            quantity=data.quantity,
            reference_type=data.reference_type,
            reference_id=data.reference_id,
            moved_by=user_id,
        )
        return self._to_movement_dict(movement)

    async def get_warehouse_stock(self, warehouse_id: UUID) -> list[dict[str, Any]]:
        rows = await self.repo.get_warehouse_stock(warehouse_id)
        items: list[dict[str, Any]] = []
        for part_id, name, code, quantity, threshold, unit_price in rows:
            status = "low" if quantity <= threshold else "ok"
            items.append(
                {
                    "part_id": str(part_id),
                    "name": name,
                    "code": code,
                    "quantity": quantity,
                    "threshold": threshold,
                    "unit_price": unit_price,
                    "status": status,
                }
            )
        return items

    async def get_warehouse_movements(
        self,
        warehouse_id: UUID,
        movement_type: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        items, total = await self.repo.get_warehouse_movements(
            warehouse_id=warehouse_id,
            movement_type=movement_type,
            page=page,
            size=size,
        )
        return {
            "items": [self._to_movement_dict(item) for item in items],
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_part_movements(
        self, warehouse_id: UUID, part_id: UUID
    ) -> list[dict[str, Any]]:
        items = await self.repo.get_part_movements(warehouse_id, part_id)
        return [self._to_movement_dict(item) for item in items]

    async def create_part(
        self,
        name: str,
        slug: str | None = None,
        unit_price: Decimal | None = None,
        description: str | None = None,
    ) -> dict[str, Any]:
        data = PartCreateSchema(
            name=name, unit_price=unit_price, description=description
        )
        part = await self.repo.create_part(
            name=data.name,
            unit_price=data.unit_price if data.unit_price is not None else None,
            description=data.description,
        )  # type: ignore[attr-defined]
        return self._to_part_dict(part)

    async def list_parts(
        self,
        warehouse_id: UUID | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict[str, Any]:
        items, total = await self.repo.list_parts(
            warehouse_id=warehouse_id, page=page, size=size
        )
        return {
            "items": [self._to_part_dict(item) for item in items],
            "total": total,
            "page": page,
            "size": size,
        }

    async def get_part(self, part_id: UUID) -> dict[str, Any]:
        part = await self.repo.get_part_by_id(part_id)
        if not part:
            raise NotFound(f"Part {part_id} not found")
        return self._to_part_dict(part)

    async def update_part(self, part_id: UUID, data: dict[str, Any]) -> dict[str, Any]:
        part = await self.repo.get_part_by_id(part_id)
        if not part:
            raise NotFound(f"Part {part_id} not found")
        updated = await self.repo.update_part(part_id, data)
        if not updated:
            raise NotFound(f"Part {part_id} not found after update")
        return self._to_part_dict(updated)

    async def delete_part(self, part_id: UUID) -> None:
        part = await self.repo.get_part_by_id(part_id)
        if not part:
            raise NotFound(f"Part {part_id} not found")
        await self.repo.delete_part(part_id)

    @staticmethod
    def _to_movement_dict(movement: Any) -> dict[str, Any]:
        return {
            "id": str(movement.id),
            "warehouse_id": str(movement.warehouse_id),
            "part_id": str(movement.part_id),
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
            "reference_type": getattr(movement, "reference_type", None),
            "reference_id": (
                str(getattr(movement, "reference_id", ""))
                if getattr(movement, "reference_id", None)
                else None
            ),
            "moved_by": str(movement.moved_by),
            "moved_at": movement.moved_at,
        }

    @staticmethod
    def _to_part_dict(part: Any) -> dict[str, Any]:
        return {
            "id": str(part.id),
            "name": part.name,
            "slug": getattr(part, "slug", None),
            "description": getattr(part, "description", None),
            "unit_price": getattr(part, "unit_price", None),
            "created_at": getattr(part, "created_at", None),
        }
