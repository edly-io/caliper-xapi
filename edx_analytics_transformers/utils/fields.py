"""
Custom django model fields.
"""
from jsonfield.fields import JSONField
from fernet_fields import EncryptedField


class EncryptedJSONField(EncryptedField, JSONField):
    description = 'Field to store encrypted JSON data.'
