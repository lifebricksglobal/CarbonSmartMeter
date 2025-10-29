# src/carbon_smart_meter/core/mining.py
"""
VIR Data Capture & kWh Conversion (Hard-Wired, Type-C / 12V Cable)

GDPR & MiCA-compliant: Primary storage in AWS (EU or SG), encrypted Azure backup.

Receives real-time VIR from microcontroller via cable → converts to kWh → verifies Ed25519 → stores.
"""

import time
import struct
from typing import Optional
from pydantic import BaseModel, Field
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import boto3
import azure.identity
import azure.storage.blob as azure_blob

# === CONFIG ===
DAILY_KWH_CAP = 1.5
POWER_SAMPLE_INTERVAL = 1.0

# === AZURE (GLOBAL BACKUP) ===
azure_cred = azure.identity.DefaultAzureCredential()
azure_blob_client = azure_blob.BlobServiceClient(
    account_url="https://backupstorage.blob.core.windows.net",
    credential=azure_cred
)

# === MODELS ===
from pydantic import ConfigDict

class VIRPacket(BaseModel):
    device_id: bytes = Field(..., min_length=32, max_length=32)
    voltage: float
    current: float
    resistance: float
    timestamp: int
    signature: bytes = Field(..., min_length=64, max_length=64)

    model_config = ConfigDict(arbitrary_types_allowed=True)

class EnergyReading(BaseModel):
    device_id: bytes
    kwh: float
    timestamp: int
    verified: bool
    cable_type: str
    user_region: str


# === ED25519 VERIFICATION ===
def verify_packet(packet: VIRPacket, public_key: bytes) -> bool:
    verify_key = VerifyKey(public_key)
    signed_data = (
        packet.device_id +
        struct.pack("<fffq", packet.voltage, packet.current, packet.resistance, packet.timestamp)
    )
    try:
        verify_key.verify(signed_data, packet.signature)
        return True
    except BadSignatureError:
        return False


# === kWh CONVERSION ===
def vir_to_kwh(voltage: float, current: float, duration_sec: float) -> float:
    power_watts = voltage * current
    energy_wh = power_watts * (duration_sec / 3600)
    return energy_wh / 1000


# === SECURE, REGION-AWARE STORAGE ===
class SecureEnergyDB:
    def __init__(self, user_region: str, azure_container: str = "energy-backup"):
        self.azure_container = azure_container
        self.aws_bucket = "ccm-energy-eu" if user_region == "EU" else "ccm-energy-sg"
        self.s3 = boto3.client("s3")

    def insert(self, reading: EnergyReading):
        key = f"energy/{reading.device_id.hex()}/{reading.timestamp}.json"
        data = reading.json().encode()

        self.s3.put_object(
            Bucket=self.aws_bucket,
            Key=key,
            Body=data,
            ServerSideEncryption="AES256"
        )

        blob_client = azure_blob_client.get_blob_client(container=self.azure_container, blob=key)
        blob_client.upload_blob(data, overwrite=True, encryption_scope="gdpr-scope")


# === MAIN PROCESSOR ===
class EnergyProcessor:
    def __init__(self, user_region: str = "EU"):
        self.user_region = user_region
        self.db = SecureEnergyDB(user_region=user_region)
        self.daily_usage = {}

    def process_packet(
        self,
        packet: VIRPacket,
        public_key: bytes,
        cable_type: str = "type-c"
    ) -> Optional[EnergyReading]:
        if cable_type not in {"type-c", "12v"}:
            return None

        if not verify_packet(packet, public_key):
            return None

        kwh = vir_to_kwh(packet.voltage, packet.current, POWER_SAMPLE_INTERVAL)

        today = packet.timestamp // 86400
        key = (packet.device_id, today)
        current_day_kwh = self.daily_usage.get(key, 0.0) + kwh

        if current_day_kwh > DAILY_KWH_CAP:
            kwh = max(0.0, DAILY_KWH_CAP - self.daily_usage.get(key, 0.0))
            if kwh <= 0:
                return None

        reading = EnergyReading(
            device_id=packet.device_id,
            kwh=kwh,
            timestamp=packet.timestamp,
            verified=True,
            cable_type=cable_type,
            user_region=self.user_region
        )
        self.db.insert(reading)
        self.daily_usage[key] = current_day_kwh

        return reading
