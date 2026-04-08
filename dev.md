1. Requests(
    created_by -> users.id
    region_id -> regions.id
    service_id -> services.id
)
2. Request_items(
    request_id -> requests.id
    asset_model_id -> asset_models.id
)

3. Documents(
    types(TRANSFER_ACT, COMMISSION_ACT, REPAIR_ACT, WRITE_OFF_ACT)
    document_number
    document_type
    created_at
    updated_at
    signed_by
    file_url
)

4. asset_commissions(
    asset_id -> assets.id
    document_id -> documents.id
)

5. werehouse_documents(
    type(IN, OUT),
    document_id -> documents.id
)

6. asset_assignments(
    asset_id -> assets.id
    region_id -> regions.id
    service_id -> services.id
    assigned_by -> users.id
)
