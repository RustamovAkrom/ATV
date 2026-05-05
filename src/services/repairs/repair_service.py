"""Repair service for managing repair workflows."""

from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from core.exceptions import NotFoundException, ValidationError
from repositories.repairs.repair_repo import RepairRepository


class RepairService:
    """Service for repair management."""

    def __init__(self, session: AsyncSession):
        """Initialize service."""
        self.repository = RepairRepository(session)

    async def list_repairs(
        self,
        page: int = 1,
        size: int = 20,
        status: str | None = None,
        asset_id: UUID | None = None,
        assigned_to: UUID | None = None,
    ) -> dict:
        """List repairs with pagination and filters."""
        items, total = await self.repository.list_repairs(
            page=page,
            size=size,
            status=status,
            asset_id=asset_id,
            assigned_to=assigned_to,
        )

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [self._repair_to_dict(item) for item in items],
        }

    async def create_repair(
        self,
        asset_id: UUID,
        description: str,
        repair_type: str = "corrective",
        reported_by: UUID | None = None,
    ) -> dict:
        """Create a new repair."""
        repair = await self.repository.create_repair(
            asset_id=asset_id,
            description=description,
            repair_type=repair_type,
            reported_by=reported_by,
        )
        await self.repository.session.commit()

        return {
            **self._repair_to_dict(repair),
            "message": "Repair created successfully",
        }

    async def get_repair(self, repair_id: UUID) -> dict:
        """Get a specific repair."""
        repair = await self.repository.get_by_id(repair_id)
        if not repair:
            raise NotFoundException(f"Repair {repair_id} not found")
        return self._repair_to_dict(repair)

    async def update_repair(self, repair_id: UUID, data: dict) -> dict:
        """Update a repair."""
        await self.get_repair(repair_id)  # Check exists

        repair = await self.repository.update_repair(repair_id, data)
        await self.repository.session.commit()

        return {
            **self._repair_to_dict(repair),
            "message": "Repair updated successfully",
        }

    async def delete_repair(self, repair_id: UUID) -> None:
        """Delete a repair."""
        await self.get_repair(repair_id)  # Check exists
        await self.repository.delete(repair_id)
        await self.repository.session.commit()

    async def assign_repair(
        self, repair_id: UUID, assigned_to: UUID, assigned_by: UUID
    ) -> dict:
        """Assign a repair to a technician."""
        repair = await self.get_repair(repair_id)

        assigned = await self.repository.assign_repair(
            repair_id=repair_id,
            assigned_to=assigned_to,
            assigned_by=assigned_by,
        )
        await self.repository.session.commit()

        return {
            **self._repair_to_dict(assigned),
            "message": "Repair assigned successfully",
        }

    async def start_repair(self, repair_id: UUID, started_by: UUID) -> dict:
        """Start working on a repair."""
        repair = await self.get_repair(repair_id)

        started = await self.repository.start_repair(
            repair_id=repair_id,
            started_by=started_by,
        )
        await self.repository.session.commit()

        return {
            **self._repair_to_dict(started),
            "message": "Repair started",
        }

    async def complete_repair(
        self,
        repair_id: UUID,
        completion_notes: str | None = None,
        total_cost: float | None = None,
        completed_by: UUID | None = None,
    ) -> dict:
        """Complete a repair."""
        repair = await self.get_repair(repair_id)

        completed = await self.repository.complete_repair(
            repair_id=repair_id,
            completion_notes=completion_notes,
            total_cost=total_cost,
            completed_by=completed_by,
        )
        await self.repository.session.commit()

        return {
            **self._repair_to_dict(completed),
            "message": "Repair completed successfully",
        }

    async def cancel_repair(
        self,
        repair_id: UUID,
        cancellation_reason: str | None = None,
        cancelled_by: UUID | None = None,
    ) -> dict:
        """Cancel a repair."""
        repair = await self.get_repair(repair_id)

        cancelled = await self.repository.cancel_repair(
            repair_id=repair_id,
            cancellation_reason=cancellation_reason,
            cancelled_by=cancelled_by,
        )
        await self.repository.session.commit()

        return {
            **self._repair_to_dict(cancelled),
            "message": "Repair cancelled successfully",
        }

    async def add_repair_part(
        self,
        repair_id: UUID,
        part_id: UUID,
        quantity_used: int,
        unit_price: float | None = None,
    ) -> dict:
        """Add a part to a repair."""
        await self.get_repair(repair_id)

        if quantity_used <= 0:
            raise ValidationError("Quantity must be positive")

        part = await self.repository.add_repair_part(
            repair_id=repair_id,
            part_id=part_id,
            quantity_used=quantity_used,
            unit_price=unit_price,
        )
        await self.repository.session.commit()

        return {
            "id": str(part.id),
            "repair_id": str(part.repair_id),
            "part_id": str(part.part_id),
            "quantity_used": part.quantity_used,
            "unit_price": float(part.unit_price) if part.unit_price else 0,
            "message": "Part added to repair successfully",
        }

    async def get_repair_parts(self, repair_id: UUID) -> list[dict]:
        """Get all parts used in a repair."""
        await self.get_repair(repair_id)
        parts = await self.repository.get_repair_parts(repair_id)

        return [
            {
                "id": str(p.id),
                "repair_id": str(p.repair_id),
                "part_id": str(p.part_id),
                "quantity_used": p.quantity_used,
                "unit_price": float(p.unit_price) if p.unit_price else 0,
                "total_cost": p.quantity_used * (float(p.unit_price) if p.unit_price else 0),
            }
            for p in parts
        ]

    async def remove_repair_part(self, repair_id: UUID, part_id: UUID) -> None:
        """Remove a part from a repair."""
        await self.get_repair(repair_id)
        await self.repository.remove_repair_part(repair_id, part_id)
        await self.repository.session.commit()

    async def get_repair_history(self, repair_id: UUID) -> list[dict]:
        """Get status history for a repair."""
        await self.get_repair(repair_id)
        history = await self.repository.get_repair_history(repair_id)

        return [
            {
                "status": h.status,
                "changed_at": h.changed_at.isoformat() if hasattr(h, 'changed_at') else None,
                "changed_by": str(h.changed_by) if h.changed_by else None,
                "notes": h.notes if hasattr(h, 'notes') else None,
            }
            for h in history
        ]

    async def get_asset_repairs(
        self,
        asset_id: UUID,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """Get all repairs for an asset."""
        items, total = await self.repository.get_asset_repairs(
            asset_id=asset_id,
            page=page,
            size=size,
        )

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [self._repair_to_dict(item) for item in items],
        }

    async def get_technician_repairs(
        self,
        technician_id: UUID,
        status: str | None = None,
        page: int = 1,
        size: int = 20,
    ) -> dict:
        """Get all repairs for a technician."""
        items, total = await self.repository.get_technician_repairs(
            technician_id=technician_id,
            status=status,
            page=page,
            size=size,
        )

        return {
            "total": total,
            "page": page,
            "size": size,
            "items": [self._repair_to_dict(item) for item in items],
        }

    async def get_repair_statistics(
        self,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
    ) -> dict:
        """Get repair statistics."""
        stats = await self.repository.get_repair_statistics(start_date, end_date)

        return {
            "total_repairs": stats.get("total_repairs", 0),
            "completed_repairs": stats.get("completed_repairs", 0),
            "in_progress": stats.get("in_progress", 0),
            "cancelled_repairs": stats.get("cancelled_repairs", 0),
            "total_cost": float(stats.get("total_cost", 0)),
            "average_cost": float(stats.get("average_cost", 0)),
            "by_type": stats.get("by_type", {}),
            "by_status": stats.get("by_status", {}),
        }

    @staticmethod
    def _repair_to_dict(repair) -> dict:
        """Convert repair model to dictionary."""
        return {
            "id": str(repair.id),
            "asset_id": str(repair.asset_id) if repair.asset_id else None,
            "status": repair.status if hasattr(repair, 'status') else None,
            "repair_type": repair.repair_type if hasattr(repair, 'repair_type') else None,
            "description": repair.description if hasattr(repair, 'description') else None,
            "reported_by": str(repair.reported_by) if repair.reported_by else None,
            "assigned_to": str(repair.assigned_to) if hasattr(repair, 'assigned_to') and repair.assigned_to else None,
            "completed_by": str(repair.completed_by) if hasattr(repair, 'completed_by') and repair.completed_by else None,
            "total_cost": float(repair.total_cost) if hasattr(repair, 'total_cost') and repair.total_cost else 0,
            "downtime_hours": repair.downtime_hours if hasattr(repair, 'downtime_hours') else None,
            "reported_at": repair.reported_at.isoformat() if hasattr(repair, 'reported_at') and repair.reported_at else None,
            "repair_date": repair.repair_date.isoformat() if hasattr(repair, 'repair_date') and repair.repair_date else None,
            "created_at": repair.created_at.isoformat() if hasattr(repair, 'created_at') and repair.created_at else None,
        }
