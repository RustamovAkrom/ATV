/asset/{asset_id}/approval-requests/assignment:
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\IIB ATV\src\api\v1\approvals\requests.py", line 36, in request_assignment
    return await service.create(
           ^^^^^^^^^^^^^^^^^^^^^
  File "E:\IIB ATV\src\services\approvals\approval_service.py", line 107, in create
    return ApprovalSchema.model_validate(approval, from_attributes=True)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "E:\IIB ATV\.venv\Lib\site-packages\pydantic\main.py", line 716, in model_validate
    return cls.__pydantic_validator__.validate_python(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pydantic_core._pydantic_core.ValidationError: 2 validation errors for ApprovalSchema
id
  UUID input should be a string, bytes or UUID object [type=uuid_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.12/v/uuid_type
created_at
  Input should be a valid datetime [type=datetime_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.12/v/datetime_type
