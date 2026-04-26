from __future__ import annotations

from uuid import UUID

from core.audit.stream import audit_stream
from core.exceptions.errors import BadRequest, NotFound
from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_history import AssetHistory
from db.models.enums import AssetStatus, UserStatus
from repositories.asset_repo import AssetRepository
from schemas.assets import (
    AssetAssignRequest,
    AssetCreate,
    AssetDetailSchema,
    AssetFilters,
    AssetHistorySchema,
    AssetSchema,
    AssetStatusChangeRequest,
    AssetUpdate,
)
from schemas.pagination import PageSchema, PaginationParamsSchema
from utils.helpers import utc_now


class AssetService:
    _ALLOWED_TRANSITIONS = {
        AssetStatus.ACTIVE: {
            AssetStatus.ASSIGNED,
            AssetStatus.IN_REPAIR,
            AssetStatus.ARCHIVED,
        },
        AssetStatus.ASSIGNED: {AssetStatus.ACTIVE, AssetStatus.IN_REPAIR},
        AssetStatus.IN_REPAIR: {AssetStatus.ACTIVE, AssetStatus.ARCHIVED},
        AssetStatus.ARCHIVED: set(),
    }

    def __init__(self, asset_repo: AssetRepository):
        self.asset_repo = asset_repo

    async def list(
        self, filters: AssetFilters, pagination: PaginationParamsSchema
    ) -> PageSchema[AssetSchema]:
        items, total = await self.asset_repo.list(filters, pagination)
        return PageSchema[AssetSchema](
            items=[
                AssetSchema.model_validate(item, from_attributes=True) for item in items
            ],
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get(self, asset_id: UUID) -> AssetDetailSchema:
        asset = await self._get_asset(asset_id)
        return AssetDetailSchema.model_validate(asset, from_attributes=True)

    async def get_history(self, asset_id: UUID) -> list[AssetHistorySchema]:
        asset = await self._get_asset(asset_id)
        return [
            AssetHistorySchema.model_validate(entry, from_attributes=True)
            for entry in asset.history_entries
        ]

    async def create(self, data: AssetCreate, actor_id: UUID) -> AssetDetailSchema:
        await self._validate_references(
            data.model_id,
            data.region_id,
            data.service_id,
            data.owner_id,
            data.class_id,
        )
        await self._validate_uniques(data.asset_tag, data.serial_number)

        initial_status = AssetStatus.ASSIGNED if data.owner_id else AssetStatus.ACTIVE
        asset = Asset(
            name=data.name.strip(),
            type=data.type.strip(),
            model_id=data.model_id,
            owner_id=data.owner_id,
            class_id=data.class_id,
            region_id=data.region_id,
            service_id=data.service_id,
            asset_tag=self._clean_optional(data.asset_tag),
            serial_number=self._clean_optional(data.serial_number),
            commission_date=data.commission_date,
            warranty_end=data.warranty_end,
            condition_percent=data.condition_percent,
            purchase_date=data.purchase_date,
            purchase_cost=data.purchase_cost,
            last_repair_date=data.last_repair_date,
            failure_count=data.failure_count,
            usage_intensity=data.usage_intensity,
            meta=data.metadata,
            status=initial_status,
        )
        await self.asset_repo.create(asset)

        if asset.owner_id is not None:
            await self.asset_repo.add_assignment(
                AssetAssignment(asset_id=asset.id, user_id=asset.owner_id)
            )

        await self._add_history(
            asset_id=asset.id,
            user_id=actor_id,
            action="created",
            description=f"Asset created with status '{asset.status.value}'",
        )
        if asset.owner_id is not None:
            await self._add_history(
                asset_id=asset.id,
                user_id=actor_id,
                action="owner_changed",
                description=f"Owner assigned to user {asset.owner_id}",
            )

        await self._publish_event(
            "asset.created",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor_id),
                "status": asset.status.value,
                "owner_id": str(asset.owner_id) if asset.owner_id else None,
            },
        )
        return await self.get(asset.id)

    async def update(
        self, asset_id: UUID, data: AssetUpdate, actor_id: UUID
    ) -> AssetDetailSchema:
        asset = await self._get_asset(asset_id, include_history=False, for_update=True)
        payload = data.model_dump(exclude_unset=True)
        if not payload:
            return await self.get(asset_id)

        await self._validate_update_references(payload)
        await self._validate_uniques(
            self._clean_optional(payload.get("asset_tag")),
            self._clean_optional(payload.get("serial_number")),
            exclude_id=asset_id,
        )

        changes: list[str] = []
        for field_name, value in payload.items():
            target_field = "meta" if field_name == "metadata" else field_name
            normalized_value = (
                self._clean_optional(value)
                if field_name in {"asset_tag", "serial_number"}
                else value
            )
            if getattr(asset, target_field) == normalized_value:
                continue
            setattr(asset, target_field, normalized_value)
            changes.append(field_name)

        if not changes:
            return await self.get(asset_id)

        await self.asset_repo.flush()
        await self._add_history(
            asset_id=asset.id,
            user_id=actor_id,
            action="updated",
            description=f"Updated fields: {', '.join(sorted(changes))}",
        )
        await self._publish_event(
            "asset.updated",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor_id),
                "fields": sorted(changes),
            },
        )
        return await self.get(asset.id)

    async def assign(
        self, asset_id: UUID, data: AssetAssignRequest, actor_id: UUID
    ) -> AssetDetailSchema:
        asset = await self._get_asset(asset_id, include_history=False, for_update=True)
        if asset.status == AssetStatus.ARCHIVED:
            raise BadRequest("Cannot assign archived asset")

        user = await self.asset_repo.get_user(data.user_id)
        if not user:
            raise NotFound("Owner not found")
        if user.status != UserStatus.ACTIVE.value:
            raise BadRequest("Cannot assign asset to inactive user")
        if asset.owner_id == user.id and asset.status == AssetStatus.ASSIGNED:
            raise BadRequest("Asset is already assigned to this user")

        now = utc_now()
        previous_owner_id = asset.owner_id
        previous_status = asset.status

        active_assignment = await self.asset_repo.get_active_assignment(asset.id)
        if active_assignment is not None:
            await self.asset_repo.close_active_assignment(active_assignment, now)

        asset.owner_id = user.id
        asset.status = AssetStatus.ASSIGNED
        await self.asset_repo.flush()
        await self.asset_repo.add_assignment(
            AssetAssignment(asset_id=asset.id, user_id=user.id)
        )

        if previous_owner_id != user.id:
            await self._add_history(
                asset_id=asset.id,
                user_id=actor_id,
                action="owner_changed",
                description=f"Owner changed from {previous_owner_id} to {user.id}",
            )
        if previous_status != AssetStatus.ASSIGNED:
            await self._add_history(
                asset_id=asset.id,
                user_id=actor_id,
                action="status_changed",
                description=(
                    f"Status changed from '{previous_status.value}' "
                    f"to '{AssetStatus.ASSIGNED.value}'",
                ),
            )

        await self._publish_event(
            "asset.ownership_changed",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor_id),
                "previous_owner_id": (
                    str(previous_owner_id) if previous_owner_id else None
                ),
                "owner_id": str(user.id),
            },
        )
        if previous_status != AssetStatus.ASSIGNED:
            await self._publish_event(
                "asset.status_changed",
                {
                    "asset_id": str(asset.id),
                    "actor_id": str(actor_id),
                    "from_status": previous_status.value,
                    "to_status": AssetStatus.ASSIGNED.value,
                },
            )
        return await self.get(asset.id)

    async def change_status(
        self,
        asset_id: UUID,
        data: AssetStatusChangeRequest,
        actor_id: UUID,
    ) -> AssetDetailSchema:
        asset = await self._get_asset(asset_id, include_history=False, for_update=True)
        new_status = data.status
        if asset.status == new_status:
            return await self.get(asset_id)

        self._validate_status_change(asset, new_status)
        previous_status = asset.status
        asset.status = new_status
        await self.asset_repo.flush()

        await self._add_history(
            asset_id=asset.id,
            user_id=actor_id,
            action="status_changed",
            description=(
                f"Status changed from '{previous_status.value}' "
                f"to '{new_status.value}'",
            ),
        )
        await self._publish_event(
            "asset.status_changed",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor_id),
                "from_status": previous_status.value,
                "to_status": new_status.value,
            },
        )
        return await self.get(asset.id)

    async def delete(self, asset_id: UUID, actor_id: UUID) -> None:
        asset = await self._get_asset(asset_id, include_history=False, for_update=True)
        if asset.status in {
            AssetStatus.ACTIVE,
            AssetStatus.ASSIGNED,
            AssetStatus.IN_REPAIR,
        }:
            raise BadRequest("Only archived assets can be deleted")

        await self._add_history(
            asset_id=asset.id,
            user_id=actor_id,
            action="deleted",
            description="Asset deleted",
        )
        await self._publish_event(
            "asset.deleted",
            {
                "asset_id": str(asset.id),
                "actor_id": str(actor_id),
            },
        )
        await self.asset_repo.delete(asset)

    async def _get_asset(
        self, asset_id: UUID, include_history: bool = True, for_update: bool = False
    ) -> Asset:
        asset = await (
            self.asset_repo.get_by_id_for_update(
                asset_id, include_history=include_history
            )
            if for_update
            else self.asset_repo.get_by_id(asset_id, include_history=include_history)
        )
        if not asset:
            raise NotFound("Asset not found")
        return asset

    async def _validate_references(
        self,
        model_id: UUID,
        region_id: UUID | None,
        service_id: UUID | None,
        owner_id: UUID | None,
        class_id: UUID | None,
    ) -> None:
        model = await self.asset_repo.get_model(model_id)
        if not model:
            raise BadRequest("Invalid asset model")
        if region_id is not None and not await self.asset_repo.get_region(region_id):
            raise BadRequest("Invalid region")
        if service_id is not None and not await self.asset_repo.get_service(service_id):
            raise BadRequest("Invalid service")
        if class_id is not None:
            if not await self.asset_repo.get_asset_class(class_id):
                raise BadRequest("Invalid asset class")
        if owner_id is not None:
            owner = await self.asset_repo.get_user(owner_id)
            if not owner:
                raise BadRequest("Invalid owner")
            if owner.status != UserStatus.ACTIVE.value:
                raise BadRequest("Owner must be active")

    async def _validate_update_references(self, payload: dict) -> None:
        if "model_id" in payload and payload["model_id"] is not None:
            if not await self.asset_repo.get_model(payload["model_id"]):
                raise BadRequest("Invalid asset model")
        if "region_id" in payload and payload["region_id"] is not None:
            if not await self.asset_repo.get_region(payload["region_id"]):
                raise BadRequest("Invalid region")
        if "service_id" in payload and payload["service_id"] is not None:
            if not await self.asset_repo.get_service(payload["service_id"]):
                raise BadRequest("Invalid service")
        if "class_id" in payload and payload["class_id"] is not None:
            if not await self.asset_repo.get_asset_class(payload["class_id"]):
                raise BadRequest("Invalid asset class")

    async def _validate_uniques(
        self,
        asset_tag: str | None,
        serial_number: str | None,
        exclude_id: UUID | None = None,
    ) -> None:
        if asset_tag and await self.asset_repo.asset_tag_exists(
            asset_tag, exclude_id=exclude_id
        ):
            raise BadRequest("Asset tag already exists")
        if serial_number and await self.asset_repo.serial_number_exists(
            serial_number, exclude_id=exclude_id
        ):
            raise BadRequest("Serial number already exists")

    def _validate_status_change(self, asset: Asset, new_status: AssetStatus) -> None:
        allowed = self._ALLOWED_TRANSITIONS[asset.status]
        if new_status not in allowed:
            raise BadRequest(
                f"Cannot change asset status from '{asset.status.value}'"
                f"to '{new_status.value}'"
            )
        if new_status == AssetStatus.ASSIGNED and asset.owner_id is None:
            raise BadRequest("Assigned status requires an owner")
        if new_status == AssetStatus.ACTIVE and asset.owner_id is not None:
            raise BadRequest(
                "Assigned asset cannot be moved to active without reassignment handling"
            )
        if new_status == AssetStatus.ARCHIVED and asset.owner_id is not None:
            raise BadRequest("Cannot archive assigned asset")

    async def _add_history(
        self, asset_id: UUID, user_id: UUID, action: str, description: str
    ) -> None:
        await self.asset_repo.add_history(
            AssetHistory(
                asset_id=asset_id,
                user_id=user_id,
                action=action,
                description=description,
            )
        )

    async def _publish_event(self, event: str, payload: dict) -> None:
        try:
            await audit_stream.publish(
                {"event": event, **payload, "timestamp": utc_now().timestamp()}
            )
        except Exception:
            return

    @staticmethod
    def _clean_optional(value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value
