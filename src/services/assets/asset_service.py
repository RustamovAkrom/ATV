from __future__ import annotations

from types import SimpleNamespace
from uuid import UUID

from pydantic import ValidationError

from core.events.asset_events import AssetEventService
from core.exceptions.errors import BadRequest, NotFound
from core.security.access_control import AccessControl
from db.models.assets.asset import Asset
from db.models.enums import AssetStatus, UserStatus
from repositories.assets.asset_repo import AssetRepository
from schemas.assets.assets import (
    AssetCreate,
    AssetDetailSchema,
    AssetFilters,
    AssetHistorySchema,
    AssetSchema,
    AssetStatusChangeRequest,
    AssetUpdate,
)
from schemas.auth.auth import CurrentUserSchema
from schemas.pagination import PageOutSchema, PaginationParamsSchema
from utils.department import normalize_department_scope
from utils.helpers import utc_now


class AssetService:
    _ALLOWED_TRANSITIONS = {
        AssetStatus.ACTIVE: {
            AssetStatus.ASSIGNED,
            AssetStatus.IN_REPAIR,
            AssetStatus.ARCHIVED,
        },
        AssetStatus.ASSIGNED: {
            AssetStatus.ACTIVE,
            AssetStatus.IN_REPAIR,
            AssetStatus.ARCHIVED,
        },
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
    ) -> PageOutSchema[AssetSchema]:

        (
            filters.department_id,
            filters.region_id,
            filters.service_id,
        ) = AccessControl.normalize_scope_filters(
            actor,
            filters.department_id,
            filters.region_id,
            filters.service_id,
        )

        items, total = await self.asset_repo.list(filters, pagination)

        normalized_items: list[AssetSchema] = []
        for item in items:
            try:
                normalized_items.append(AssetSchema.model_validate(item))
            except ValidationError:
                normalized_items.append(self._normalize_asset_schema(item))

        return PageOutSchema(
            items=normalized_items,
            total=total,
            page=pagination.page,
            limit=pagination.limit,
        )

    async def get(self, asset_id: UUID, actor: CurrentUserSchema) -> AssetDetailSchema:
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        return self._to_detail_schema(asset)

    async def get_history(
        self, asset_id: UUID, actor: CurrentUserSchema
    ) -> list[AssetHistorySchema]:
        asset = await self.asset_repo.get_by_id(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        history: list[AssetHistorySchema] = []
        for entry in asset.history_entries:
            user = getattr(entry, "user", None)
            description = getattr(entry, "description", None)
            if not description:
                details = getattr(entry, "details", None)
                description = str(details) if details is not None else ""

            history.append(
                AssetHistorySchema.model_validate(
                    {
                        "id": entry.id,
                        "action": entry.action,
                        "description": description,
                        "created_at": entry.created_at,
                        "user": (
                            {
                                "id": user.id,
                                "login": user.login,
                            }
                            if user is not None
                            else {
                                "id": getattr(entry, "user_id", None)
                                or UUID("00000000-0000-0000-0000-000000000000"),
                                "login": "system",
                            }
                        ),
                    }
                )
            )
        return history

    async def create(
        self, data: AssetCreate, actor: CurrentUserSchema
    ) -> AssetDetailSchema:
        owner_id = actor.id if data.assign_to_self else None
        payload = data.model_dump(exclude_unset=True)
        payload = await normalize_department_scope(
            getattr(self.asset_repo, "session", None), payload
        )

        region_id = payload.get("region_id")
        service_id = payload.get("service_id")

        AccessControl.check_scope_access(
            actor,
            payload.get("department_id"),
            region_id,
            service_id,
        )

        if owner_id:
            owner = await self.asset_repo.get_user(owner_id)
            if not owner:
                raise BadRequest("Invalid owner")

            if owner.status != UserStatus.ACTIVE.value:
                raise BadRequest("Owner must be active")

            if (
                owner.assigned_region_id
                and region_id
                and owner.assigned_region_id != region_id
            ):
                raise BadRequest(
                    f"Owner is assigned to region {owner.assigned_region_id}, "
                    f"but asset belongs to region {region_id}"
                )
            if (
                owner.assigned_service_id
                and service_id
                and owner.assigned_service_id != service_id
            ):
                raise BadRequest(
                    f"Owner is assigned to service {owner.assigned_service_id}, "
                    f"but asset belongs to service {service_id}"
                )

        if data.class_id is not None and not await self.asset_repo.get_asset_class(
            data.class_id
        ):
            raise BadRequest("Invalid asset class")

        asset = Asset(
            name=data.name,
            model_id=data.model_id,
            serial_number=data.serial_number,
            owner_id=owner_id,
            status=AssetStatus.ASSIGNED if owner_id else AssetStatus.ACTIVE,
            department_id=payload.get("department_id"),
            class_id=data.class_id,
            service_id=service_id,
            region_id=region_id,
            commission_date=data.commission_date,
            warranty_end=data.warranty_end,
            condition_percent=data.condition_percent,
            purchase_date=data.purchase_date,
            purchase_cost=data.purchase_cost,
            last_repair_date=data.last_repair_date,
            failure_count=data.failure_count,
            usage_intensity=data.usage_intensity,
            meta=data.metadata or {},
        )

        created = await self.asset_repo.create(asset)
        asset = created or asset

        await self.asset_events.created(
            asset_id=asset.id,
            actor_id=actor.id,
            user_id=owner_id,
            asset_name=asset.name,
            status=asset.status,
        )
        return self._to_detail_schema(asset)

    async def update(
        self, asset_id: UUID, data: AssetUpdate, actor: CurrentUserSchema
    ) -> AssetDetailSchema:
        asset = await self.asset_repo.get_by_id_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        payload = data.model_dump(exclude_unset=True)
        if not payload:
            return await self.get(asset_id, actor)

        if "metadata" in payload:
            payload["meta"] = payload.pop("metadata") or {}

        await self._validate_update_references(payload)
        await self._validate_uniques(payload.get("serial_number"), exclude_id=asset_id)

        if "department_id" in payload:
            payload = await normalize_department_scope(
                getattr(self.asset_repo, "session", None), payload
            )

        next_region_id = payload.get("region_id", asset.region_id)
        next_service_id = payload.get("service_id", asset.service_id)
        AccessControl.check_scope_access(
            actor,
            payload.get("department_id", asset.department_id),
            next_region_id,
            next_service_id,
        )

        owner_id = payload.get("owner_id")
        if owner_id is not None:
            owner = await self.asset_repo.get_user(owner_id)
            if not owner:
                raise BadRequest("Invalid owner")
            if owner.status != UserStatus.ACTIVE.value:
                raise BadRequest("Owner must be active")

        changed_fields: list[str] = []
        for field, value in payload.items():
            value = self._clean_optional(value)
            if getattr(asset, field, None) != value:
                setattr(asset, field, value)
                changed_fields.append(field)

        if changed_fields:
            await self.asset_repo.flush()
            if hasattr(self.asset_repo, "refresh"):
                await self.asset_repo.refresh(asset)
            await self.asset_events.updated(
                asset_id=asset.id,
                actor_id=actor.id,
                owner_id=asset.owner_id,
                asset_name=asset.name,
                fields=changed_fields,
            )

        return self._to_detail_schema(asset)

    async def delete(self, asset_id: UUID, actor: CurrentUserSchema) -> None:
        asset = await self.asset_repo.get_by_id_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        if asset.status != AssetStatus.ARCHIVED:
            raise BadRequest("Only archived assets can be deleted")

        owner_id = asset.owner_id
        asset_name = asset.name
        await self.asset_repo.delete(asset)
        await self.asset_events.deleted(
            asset_id=asset_id,
            actor_id=actor.id,
            owner_id=owner_id,
            asset_name=asset_name,
        )

    async def change_status(
        self,
        asset_id: UUID,
        data: AssetStatusChangeRequest,
        actor: CurrentUserSchema,
    ) -> AssetDetailSchema:
        asset = await self.asset_repo.get_by_id_for_update(asset_id)
        if not asset:
            raise NotFound("Asset not found")

        AccessControl.check_scope_access(
            actor,
            getattr(asset, "department_id", None),
            getattr(asset, "region_id", None),
            getattr(asset, "service_id", None),
        )

        old_status = AssetStatus(asset.status)
        new_status = AssetStatus(data.status)
        if old_status == new_status:
            return await self.get(asset_id, actor)

        self._validate_status_change(asset, new_status)
        previous_owner_id = asset.owner_id

        if new_status == AssetStatus.ARCHIVED and asset.owner_id is not None:
            active_assignment = await self.asset_repo.get_active_assignment(asset.id)
            if active_assignment:
                await self.asset_repo.close_active_assignment(
                    active_assignment, utc_now()
                )
            asset.owner_id = None

        asset.status = new_status

        await self.asset_repo.flush()
        if hasattr(self.asset_repo, "refresh"):
            await self.asset_repo.refresh(asset)
        await self.asset_events.status_changed(
            asset_id=asset.id,
            actor_id=actor.id,
            owner_id=previous_owner_id,
            from_status=old_status.value,
            to_status=new_status.value,
        )

        return self._to_detail_schema(asset)

    async def _get_asset(self, asset_id: UUID) -> Asset:
        asset = await self.asset_repo.get_by_id(asset_id)
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
        await self._validate_update_references(
            {
                "model_id": model_id,
                "region_id": region_id,
                "service_id": service_id,
                "class_id": class_id,
            }
        )
        if owner_id is not None:
            owner = await self.asset_repo.get_user(owner_id)
            if not owner:
                raise BadRequest("Invalid owner")
            if owner.status != UserStatus.ACTIVE.value:
                raise BadRequest("Owner must be active")

    async def _validate_update_references(self, payload: dict) -> None:
        if (
            "model_id" in payload
            and payload["model_id"] is not None
            and not await self.asset_repo.get_model(payload["model_id"])
        ):
            raise BadRequest("Invalid asset model")
        if (
            "region_id" in payload
            and payload["region_id"] is not None
            and not await self.asset_repo.get_region(payload["region_id"])
        ):
            raise BadRequest("Invalid region")
        if (
            "service_id" in payload
            and payload["service_id"] is not None
            and not await self.asset_repo.get_service(payload["service_id"])
        ):
            raise BadRequest("Invalid service")
        if (
            "department_id" in payload
            and payload["department_id"] is not None
            and not await self.asset_repo.get_department(payload["department_id"])
        ):
            raise BadRequest("Invalid department")
        if (
            "class_id" in payload
            and payload["class_id"] is not None
            and not await self.asset_repo.get_asset_class(payload["class_id"])
        ):
            raise BadRequest("Invalid asset class")

    async def _validate_uniques(
        self,
        serial_number: str | None,
        exclude_id: UUID | None = None,
    ) -> None:
        if serial_number and await self.asset_repo.serial_number_exists(
            serial_number, exclude_id=exclude_id
        ):
            raise BadRequest("Serial number already exists")

    def _validate_status_change(self, asset: Asset, new_status: AssetStatus) -> None:
        current_status = AssetStatus(asset.status)
        allowed = self._ALLOWED_TRANSITIONS[current_status]
        if new_status not in allowed:
            raise BadRequest(
                f"Cannot change asset status from '{current_status.value}'"
                f"to '{new_status.value}'"
            )
        if new_status == AssetStatus.ASSIGNED and asset.owner_id is None:
            raise BadRequest("Assigned status requires an owner")
        if new_status == AssetStatus.ACTIVE and asset.owner_id is not None:
            raise BadRequest(
                "Assigned asset cannot be moved to active without reassignment handling"
            )

    @staticmethod
    def _clean_optional(value):
        if isinstance(value, str):
            value = value.strip()
            return value or None
        return value

    @classmethod
    def _to_detail_schema(cls, item) -> AssetDetailSchema:
        try:
            return AssetDetailSchema.model_validate(item, from_attributes=True)
        except ValidationError:
            payload = cls._normalize_asset_schema(item).model_dump(by_alias=True)
            payload["history_entries"] = getattr(item, "history_entries", []) or []
            payload["maintenances"] = getattr(item, "maintenances", []) or []
            return AssetDetailSchema.model_validate(payload)

    @staticmethod
    def _normalize_asset_schema(item) -> AssetSchema:
        created_at = getattr(item, "created_at", None) or utc_now()
        updated_at = getattr(item, "updated_at", None) or created_at

        model = getattr(item, "model", None)
        if model is None and getattr(item, "model_id", None):
            model = SimpleNamespace(id=item.model_id, name="")

        asset_class = getattr(item, "asset_class", None)
        if asset_class is None and getattr(item, "class_id", None):
            asset_class = SimpleNamespace(id=item.class_id, name="")

        region = getattr(item, "region", None)
        if region is None and getattr(item, "region_id", None):
            region = SimpleNamespace(id=item.region_id, name="")

        department = getattr(item, "department", None)
        if department is None and getattr(item, "department_id", None):
            department = SimpleNamespace(id=item.department_id, name="")

        service = getattr(item, "service", None)
        if service is None and getattr(item, "service_id", None):
            service = SimpleNamespace(id=item.service_id, name="")

        owner = getattr(item, "owner", None)
        if owner is None and getattr(item, "owner_id", None):
            owner = SimpleNamespace(id=item.owner_id, login="")

        payload = {
            "id": item.id,
            "name": getattr(item, "name", ""),
            "status": getattr(item, "status", AssetStatus.ACTIVE),
            "serial_number": getattr(item, "serial_number", None),
            "model": model,
            "asset_class": asset_class,
            "owner": owner,
            "department": department,
            "region": region,
            "service": service,
            "warehouse": getattr(item, "warehouse", None),
            "assignments": getattr(item, "assignments", []),
            "meta": getattr(item, "meta", {}) or {},
            "condition_percent": getattr(item, "condition_percent", 100),
            "commission_date": getattr(item, "commission_date", None),
            "warranty_end": getattr(item, "warranty_end", None),
            "purchase_date": getattr(item, "purchase_date", None),
            "purchase_cost": getattr(item, "purchase_cost", None),
            "last_repair_date": getattr(item, "last_repair_date", None),
            "failure_count": getattr(item, "failure_count", 0),
            "usage_intensity": getattr(item, "usage_intensity", 0),
            "created_at": created_at,
            "updated_at": updated_at,
        }
        return AssetSchema.model_validate(payload, from_attributes=True)
