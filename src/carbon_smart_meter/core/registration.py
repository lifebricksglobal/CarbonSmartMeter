# src/carbon_smart_meter/core/registration.py
"""
Device Registration & Wallet Binding (Hard-Wired Security)

GDPR & MiCA-compliant: Primary storage in AWS (EU or SG), encrypted Azure backup.

- Device generates Ed25519 keypair on first boot
- Sends public key + device_id to backend via secure cable
- Backend binds public key → wallet address
- Enforces 1 device = 1 wallet
- Prevents spoofing, duplicates, and wallet swaps
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field
from nacl.signing import SigningKey, VerifyKey
from nacl.exceptions import BadSignatureError
import boto3
import azure.identity
import azure.storage.blob as azure_blob
import time

# === AZURE BACKUP ===
azure_cred = azure.identity.DefaultAzureCredential()
azure_blob_client = azure_blob.BlobServiceClient(
    account_url="https://backupstorage.blob.core.windows.net",
    credential=azure_cred
)

# === MODELS ===
class DeviceRegistrationRequest(BaseModel):
    device_id: bytes = Field(..., min_length=32, max_length=32)
    public_key: bytes = Field(..., min_length=32, max_length=32)
    signature: bytes = Field(..., min_length=64, max_length=64)
    wallet_address: str

class DeviceBinding(BaseModel):
    device_id: bytes
    public_key: bytes
    wallet_address: str
    registered_at: int
    verified: bool = True


# === SECURE, REGION-AWARE STORAGE ===
class SecureRegistrationDB:
    def __init__(self, user_region: str):
        self.user_region = user_region
        self.aws_bucket = "ccm-bindings-eu" if user_region == "EU" else "ccm-bindings-sg"
        self.s3 = boto3.client("s3")

    def insert(self, binding: DeviceBinding):
        key = f"bindings/{binding.device_id.hex()}.json"
        data = binding.json().encode()

        self.s3.put_object(
            Bucket=self.aws_bucket,
            Key=key,
            Body=data,
            ServerSideEncryption="AES256"
        )

        blob_client = azure_blob_client.get_blob_client(
            container="registration-backup", blob=key
        )
        blob_client.upload_blob(data, overwrite=True, encryption_scope="gdpr-scope")


# === REGISTRATION MANAGER ===
class RegistrationManager:
    def __init__(self, db):
        self.db = db
        self.active_devices: Dict[bytes, DeviceBinding] = {}

    def register_device(self, request: DeviceRegistrationRequest) -> Optional[DeviceBinding]:
        if not self._verify_device_signature(request.device_id, request.public_key, request.signature):
            return None

        if self.db.exists(device_id=request.device_id):
            return None
        if self.db.exists(public_key=request.public_key):
            return None
        if self.db.wallet_in_use(request.wallet_address):
            return None

        binding = DeviceBinding(
            device_id=request.device_id,
            public_key=request.public_key,
            wallet_address=request.wallet_address,
            registered_at=int(time.time())
        )

        self.db.insert(binding)
        self.active_devices[request.device_id] = binding
        return binding

    def _verify_device_signature(self, device_id: bytes, public_key: bytes, signature: bytes) -> bool:
        try:
            verify_key = VerifyKey(public_key)
            verify_key.verify(device_id, signature)
            return True
        except BadSignatureError:
            return False

    def get_binding(self, device_id: bytes) -> Optional[DeviceBinding]:
        return self.active_devices.get(device_id)

    def is_wallet_bound(self, wallet: str) -> bool:
        return self.db.wallet_in_use(wallet)


# === MOCK DB (for testing) ===
class MockRegistrationDB:
    def __init__(self):
        self.bindings = {}
        self.wallet_set = set()

    def exists(self, device_id: Optional[bytes] = None, public_key: Optional[bytes] = None) -> bool:
        if device_id:
            return device_id in self.bindings
        if public_key:
            return any(b.public_key == public_key for b in self.bindings.values())
        return False

    def wallet_in_use(self, wallet: str) -> bool:
        return wallet in self.wallet_set

    def insert(self, binding: DeviceBinding):
        self.bindings[binding.device_id] = binding
        self.wallet_set.add(binding.wallet_address)

    def get(self, device_id: bytes) -> Optional[DeviceBinding]:
        return self.bindings.get(device_id)


# === DEVICE-SIDE: Generate Keypair & Register ===
def generate_device_registration(wallet_address: str) -> DeviceRegistrationRequest:
    signing_key = SigningKey.generate()
    public_key = signing_key.verify_key.encode()
    device_id = b"0" * 32  # In real: hardware UID
    signature = signing_key.sign(device_id).signature

    return DeviceRegistrationRequest(
        device_id=device_id,
        public_key=public_key,
        signature=signature,
        wallet_address=wallet_address
    )