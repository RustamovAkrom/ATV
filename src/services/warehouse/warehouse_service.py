"""Warehouse service for stock and inventory management."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions.errors import NotFound, ValidationError
from repositories.warehouse.warehouse_repo import WarehouseRepository


class WarehouseService:
    """Service for warehouse and stock management."""

    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.repository = WarehouseRepository(session)

    async def list_warehouses(
        self,
        page: int = 1,
        size: int = 20,
        region_id: UUID | None = None,
        service_id: UUID | None = None,
    ) -> dict:
        """List warehouses with pagination."""
        items, total = await self.repository.list_warehouses(
            page=page,
            size=size,
            region_id=region_id,
            service_id=service_id,
        )

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [
                {
                    "id": str(item.id),
                    "name": item.name,
                    "code": item.code,
                    "region_id": str(item.region_id) if item.region_id else None,
                    "service_id": str(item.service_id) if item.service_id else None,
                    "manager_user_id": str(item.manager_user_id) if item.manager_user_id else None,
                    "is_active": item.is_active,
                    "created_at": item.created_at.isoformat() if hasattr(item, 'created_at') else None,
                }
                for item in items
            ],
        }

    async def create_warehouse(
        self,
        name: str,
        region_id: UUID,
        code: str | None = None,
        service_id: UUID | None = None,
        manager_user_id: UUID | None = None,
    ) -> dict:
        """Create a new warehouse."""
        warehouse = await self.repository.create_warehouse(
            name=name,
            code=code,
            region_id=region_id,
            service_id=service_id,
            manager_user_id=manager_user_id,
        )
        await self.repository.session.commit()

        return {
            "id": str(warehouse.id),
            "name": warehouse.name,
            "code": warehouse.code,
            "region_id": str(warehouse.region_id) if warehouse.region_id else None,
            "service_id": str(warehouse.service_id) if warehouse.service_id else None,
            "manager_user_id": str(warehouse.manager_user_id) if warehouse.manager_user_id else None,
            "is_active": warehouse.is_active,
            "message": "Warehouse created successfully",
        }

    async def get_warehouse(self, warehouse_id: UUID) -> dict:
        """Get a specific warehouse."""
        warehouse = await self.repository.get_by_id(warehouse_id)
        if not warehouse:
            raise NotFound(f"Warehouse {warehouse_id} not found")

        return {
            "id": str(warehouse.id),
            "name": warehouse.name,
            "code": warehouse.code,
            "region_id": str(warehouse.region_id) if warehouse.region_id else None,
            "service_id": str(warehouse.service_id) if warehouse.service_id else None,
            "manager_user_id": str(warehouse.manager_user_id) if warehouse.manager_user_id else None,
            "is_active": warehouse.is_active,
            "created_at": warehouse.created_at.isoformat() if hasattr(warehouse, 'created_at') else None,
        }

    async def update_warehouse(self, warehouse_id: UUID, data: dict) -> dict:
        """Update a warehouse."""
        warehouse = await self.get_warehouse(warehouse_id)  # Check exists

        updated = await self.repository.update_warehouse(warehouse_id, data)
        await self.repository.session.commit()

        return {
            "id": str(updated.id),
            "name": updated.name,
            "code": updated.code,
            "region_id": str(updated.region_id) if updated.region_id else None,
            "service_id": str(updated.service_id) if updated.service_id else None,
            "manager_user_id": str(updated.manager_user_id) if updated.manager_user_id else None,
            "is_active": updated.is_active,
            "message": "Warehouse updated successfully",
        }

    async def delete_warehouse(self, warehouse_id: UUID) -> None:
        """Delete a warehouse."""
        await self.get_warehouse(warehouse_id)  # Check exists
        await self.repository.delete(warehouse_id)
        await self.repository.session.commit()

    async def get_warehouse_stock(self, warehouse_id: UUID) -> list[dict]:
        """Get current stock levels for a warehouse."""
        await self.get_warehouse(warehouse_id)  # Check warehouse exists
        stock = await self.repository.get_warehouse_stock(warehouse_id)

        return [
            {
                "part_id": str(item[0]) if item[0] else None,
                "part_name": item[1],
                "part_code": item[2],
                "quantity_on_hand": int(item[3]) if item[3] else 0,
                "min_quantity": int(item[4]) if item[4] else 0,
                "unit_price": float(item[5]) if item[5] else 0,
                "total_value": float(int(item[3]) * float(item[5])) if item[3] and item[5] else 0,
                "status": "low" if item[3] and item[4] and item[3] <= item[4] else "ok",
            }
            for item in stock
        ]

    async def record_stock_in(
        self,
        warehouse_id: UUID,
        part_id: UUID,
        quantity: int,
        moved_by: UUID,
        reference_type: str = "purchase",
        reference_id: UUID | None = None,
    ) -> dict:
        """Record incoming stock."""
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        movement = await self.repository.record_stock_in(
            warehouse_id=warehouse_id,
            part_id=part_id,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            moved_by=moved_by,
        )
        await self.repository.session.commit()

        return {
            "id": str(movement.id),
            "warehouse_id": str(movement.warehouse_id),
            "part_id": str(movement.part_id),
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
            "reference_type": movement.reference_type,
            "reference_id": str(movement.reference_id) if movement.reference_id else None,
            "moved_by": str(movement.moved_by),
            "moved_at": movement.moved_at.isoformat() if hasattr(movement, 'moved_at') else None,
            "message": f"{quantity} units recorded as IN",
        }

    async def record_stock_out(
        self,
        warehouse_id: UUID,
        part_id: UUID,
        quantity: int,
        moved_by: UUID,
        reference_type: str = "repair",
        reference_id: UUID | None = None,
    ) -> dict:
        """Record outgoing stock."""
        if quantity <= 0:
            raise ValidationError("Quantity must be positive")

        movement = await self.repository.record_stock_out(
            warehouse_id=warehouse_id,
            part_id=part_id,
            quantity=quantity,
            reference_type=reference_type,
            reference_id=reference_id,
            moved_by=moved_by,
        )
        await self.repository.session.commit()

        return {
            "id": str(movement.id),
            "warehouse_id": str(movement.warehouse_id),
            "part_id": str(movement.part_id),
            "movement_type": movement.movement_type,
            "quantity": movement.quantity,
            "reference_type": movement.reference_type,
            "reference_id": str(movement.reference_id) if movement.reference_id else None,
            "moved_by": str(movement.moved_by),
            "moved_at": movement.moved_at.isoformat() if hasattr(movement, 'moved_at') else None,
            "message": f"{quantity} units recorded as OUT",
        }

    async def get_warehouse_movements(
        self,
        warehouse_id: UUID,
        movement_type: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """Get warehouse movements with pagination."""
        await self.get_warehouse(warehouse_id)  # Check warehouse exists
        items, total = await self.repository.get_warehouse_movements(
            warehouse_id=warehouse_id,
            movement_type=movement_type,
            page=page,
            size=size,
        )

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [
                {
                    "id": str(item.id),
                    "warehouse_id": str(item.warehouse_id),
                    "part_id": str(item.part_id),
                    "movement_type": item.movement_type,
                    "quantity": item.quantity,
                    "reference_type": item.reference_type,
                    "reference_id": str(item.reference_id) if item.reference_id else None,
                    "moved_by": str(item.moved_by),
                    "moved_at": item.moved_at.isoformat() if hasattr(item, 'moved_at') else None,
                }
                for item in items
            ],
        }

    async def get_part_movements(self, warehouse_id: UUID, part_id: UUID) -> list[dict]:
        """Get movement history for a specific part."""
        await self.get_warehouse(warehouse_id)  # Check warehouse exists
        movements = await self.repository.get_part_movements(warehouse_id, part_id)

        return [
            {
                "id": str(m.id),
                "warehouse_id": str(m.warehouse_id),
                "part_id": str(m.part_id),
                "movement_type": m.movement_type,
                "quantity": m.quantity,
                "reference_type": m.reference_type,
                "reference_id": str(m.reference_id) if m.reference_id else None,
                "moved_by": str(m.moved_by),
                "moved_at": m.moved_at.isoformat() if hasattr(m, 'moved_at') else None,
            }
            for m in movements
        ]

    async def list_parts(
        self,
        warehouse_id: UUID | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """List all parts."""
        items, total = await self.repository.list_parts(
            warehouse_id=warehouse_id,
            page=page,
            size=size,
        )

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [
                {
                    "id": str(item.id),
                    "name": item.name,
                    "code": item.code,
                    "description": item.description,
                    "unit_price": float(item.unit_price) if item.unit_price else 0,
                    "created_at": item.created_at.isoformat() if hasattr(item, 'created_at') else None,
                }
                for item in items
            ],
        }

    async def create_part(
        self,
        name: str,
        code: str | None = None,
        description: str | None = None,
        unit_price: float | None = None,
    ) -> dict:
        """Create a new part."""
        part = await self.repository.create_part(
            name=name,
            code=code,
            description=description,
            unit_price=unit_price,
        )
        await self.repository.session.commit()

        return {
            "id": str(part.id),
            "name": part.name,
            "code": part.code,
            "description": part.description,
            "unit_price": float(part.unit_price) if part.unit_price else 0,
            "message": "Part created successfully",
        }

    async def get_part(self, part_id: UUID) -> dict:
        """Get a specific part."""
        part = await self.repository.get_part_by_id(part_id)
        if not part:
            raise NotFound(f"Part {part_id} not found")

        return {
            "id": str(part.id),
            "name": part.name,
            "code": part.code,
            "description": part.description,
            "unit_price": float(part.unit_price) if part.unit_price else 0,
            "created_at": part.created_at.isoformat() if hasattr(part, 'created_at') else None,
        }

    async def update_part(self, part_id: UUID, data: dict) -> dict:
        """Update a part."""
        await self.get_part(part_id)  # Check exists

        part = await self.repository.update_part(part_id, data)
        await self.repository.session.commit()

        return {
            "id": str(part.id),
            "name": part.name,
            "code": part.code,
            "description": part.description,
            "unit_price": float(part.unit_price) if part.unit_price else 0,
            "message": "Part updated successfully",
        }

    async def delete_part(self, part_id: UUID) -> None:
        """Delete a part."""
        await self.get_part(part_id)  # Check exists
        await self.repository.delete_part(part_id)
        await self.repository.session.commit()
