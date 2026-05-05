from __future__ import annotations

from uuid import UUID

from core.audit.stream import audit_stream
from core.exceptions.errors import BadRequest, NotFound
from db.models.assets.asset import Asset
from db.models.assets.asset_assignment import AssetAssignment
from db.models.assets.asset_history import AssetHistory
from db.models.enums import AssetStatus, UserStatus
from repositories.assets.asset_repo import AssetRepository
from schemas.assets.assets import (
    AssetAssignRequest,
    AssetCreate,
    AssetDetailSchema,
    AssetFilters,
    AssetHistorySchema,
    AssetSchema,
    AssetStatusChangeRequest,
    AssetUpdate,
    AssetPage,
)
from schemas.pagination import PageSchema, PaginationParamsSchema, build_page
from utils.helpers import utc_now
from schemas.auth.auth import CurrentUserSchema
from core.security.access_control import AccessControl
from core.events.asset_events import AssetEventService


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

    def __init__(
        self,
        asset_repo: AssetRepository,
        asset_events: AssetEventService,
    ):
        self.asset_repo = asset_repo
        self.asset_events = asset_events

    async def list(
        self,
        filters: AssetFilters,
        pagination: PaginationParamsSchema,
        actor: CurrentUserSchema,
    ) -> PageSchema[AssetSchema]:

        if actor.assigned_region_id:
            filters.region_id = actor.assigned_region_id

        if actor.assigned_service_id:
            filters.service_id = actor.assigned_service_id

        items, total = await self.asset_repo.list(filters, pagination)

        return build_page(
            schema=AssetPage,
            items=[AssetSchema.model_validate(i) for i in items],
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get(self, asset_id: UUID, actor: CurrentUserSchema) -> AssetDetailSchema:
        asset = await self._get_asset(asset_id)

        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        return AssetDetailSchema.model_validate(asset, from_attributes=True)

    async def get_history(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> list[AssetHistorySchema]:
        asset = await self._get_asset(asset_id)

        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        return [
            AssetHistorySchema.model_validate(entry, from_attributes=True)
            for entry in asset.history_entries
        ]

    async def create(
        self, data: AssetCreate, actor: CurrentUserSchema
    ) -> AssetDetailSchema:
        AccessControl.check_region_access(actor, data.region_id)
        AccessControl.check_service_access(actor, data.service_id)

        if data.owner_id:
            owner = await self.asset_repo.get_user(data.owner_id)
            if not owner:
                raise BadRequest("Invalid owner")

            AccessControl.check_region_access(actor, owner.region_id)
            AccessControl.check_service_access(actor, owner.service_id)

        await self._validate_references(
            data.model_id,
            data.region_id,
            data.service_id,
            data.owner_id,
            data.class_id,
        )
        await self._validate_uniques(data.asset_tag, data.serial_number)

        asset = Asset(
            name=data.name.strip(),
            type=data.type.strip(),
            model_id=data.model_id,
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
            owner_id=data.owner_id,
            status=AssetStatus.ASSIGNED if data.owner_id else AssetStatus.ACTIVE,
        )

        await self.asset_repo.create(asset)
        await self.asset_repo.flush()

        await self.asset_events.created(
            asset_id=asset.id,
            actor_id=actor.id,
            user_id=asset.owner_id,
            asset_name=asset.name,
            status=asset.status.value,
        )

        return await self.get(asset.id, actor)

    async def update(
        self, asset_id: UUID, data: AssetUpdate, actor: CurrentUserSchema
    ) -> AssetDetailSchema:
        asset = await self._get_asset(asset_id, include_history=False, for_update=True)

        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        payload = data.model_dump(exclude_unset=True)
        if not payload:
            return await self.get(asset.id, actor)

        await self._validate_update_references(payload)

        if "region_id" in payload:
            AccessControl.check_region_access(actor, payload["region_id"])
        if "service_id" in payload:
            AccessControl.check_service_access(actor, payload["service_id"])

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
            return await self.get(asset.id, actor)

        await self.asset_repo.flush()

        await self.asset_events.updated(
            asset_id=asset.id,
            actor_id=actor.id,
            owner_id=asset.owner_id,
            asset_name=asset.name,
            fields=sorted(changes),
        )

        return await self.get(asset.id, actor)

    async def change_status(
        self,
        asset_id: UUID,
        data: AssetStatusChangeRequest,
        actor: CurrentUserSchema,
    ) -> AssetDetailSchema:
        asset = await self._get_asset(asset_id, include_history=False, for_update=True)

        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        new_status = data.status
        if asset.status == new_status:
            return await self.get(asset.id, actor)

        self._validate_status_change(asset, new_status)
        previous_status = asset.status
        asset.status = new_status
        await self.asset_repo.flush()

        await self.asset_events.status_changed(
            asset_id=asset.id,
            actor_id=actor.id,
            owner_id=asset.owner_id,
            from_status=previous_status.value,
            to_status=new_status.value,
        )

        return await self.get(asset.id, actor)

    async def delete(self, asset_id: UUID, actor: CurrentUserSchema) -> None:
        asset = await self._get_asset(asset_id, include_history=False, for_update=True)

        AccessControl.check_region_access(actor, asset.region_id)
        AccessControl.check_service_access(actor, asset.service_id)

        if asset.status in {
            AssetStatus.ACTIVE,
            AssetStatus.ASSIGNED,
            AssetStatus.IN_REPAIR,
        }:
            raise BadRequest("Only archived assets can be deleted")

        await self.asset_events.deleted(
            asset_id=asset.id,
            actor_id=actor.id,
            owner_id=asset.owner_id,
            asset_name=asset.name,
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

    @staticmethod
    def _clean_optional(value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value
