python<br>from pydantic import BaseModel<br><br>class Measurement(BaseModel):<br>    device_id: bytes<br>    kwh: int<br>    signature: bytes<br><br>def submit(measurement, adapter):<br>    return adapter.submit_kwh(measurement.device_id, measurement.kwh, measurement.signature)<br>

# src/carbon_smart_meter/core/mining.py
"""
VIR Data Capture & kWh Conversion (Hard-Wired Only)

Receives real-time VIR (Voltage, Current, Resistance) from microcontroller
via **Type-C USB or 12V charging cable** (mobile devices).

- Converts to kWh using P = V × I
- Verifies Ed25519 signature from device
- Stores timestamped, tamper-proof readings
- Enforces 9 kWh/day cap
- **No Bluetooth — cable-only for security & accuracy**
"""

import time
import struct
from typing import Tuple, Optional
from pydantic import BaseModel, Field
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

# === CONFIG ===
DAILY_KWH_CAP = 9.0  # Max 9 kWh/day per device
POWER_SAMPLE_INTERVAL = 1.0  # seconds between samples (configurable)

# === DATA MODELS ===
class VIRPacket(BaseModel):
    device_id: bytes = Field(..., min_length=32, max_length=32)
    voltage: float    # V (e.g., 5.0, 12.0)
    current: float    # A (e.g., 0.5, 2.0)
    resistance: float # Ω
    timestamp: int    # Unix timestamp (seconds)
    signature: bytes = Field(..., min_length=64, max_length=64)

    class Config:
        arbitrary_types_allowed = True


class EnergyReading(BaseModel):
    device_id: bytes
    kwh: float
    timestamp: int
    verified: bool
    cable_type: str  # "type-c" or "12v"


# === ED25519 VERIFICATION ===
def verify_packet(packet: VIRPacket, public_key: bytes) -> bool:
    """Verify Ed25519 signature over (device_id + data + timestamp)"""
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
    """P = V × I → Energy (Wh) = P × (t/3600) → kWh = Wh / 1000"""
    power_watts = voltage * current
    energy_wh = power_watts * (duration_sec / 3600)
    return energy_wh / 1000


# === MAIN PROCESSOR ===
class EnergyProcessor:
    def __init__(self, db):
        self.db = db  # Secure, indexed DB (SQLite/Postgres)
        self.daily_usage = {}  # {(device_id, date): kwh_today}

    def process_packet(
        self,
        packet: VIRPacket,
        public_key: bytes,
        cable_type: str = "type-c"  # or "12v"
    ) -> Optional[EnergyReading]:
        """
        Process hard-wired VIR packet:
        - Verify signature
        - Convert to kWh
        - Enforce 9 kWh/day cap
        - Store with cable type
        """
        if cable_type not in {"type-c", "12v"}:
            return None

        # 1. Verify Ed25519 signature
        if not verify_packet(packet, public_key):
            return None

        # 2. Convert to kWh
        kwh = vir_to_kwh(packet.voltage, packet.current, POWER_SAMPLE_INTERVAL)

        # 3. Enforce daily cap
        today = packet.timestamp // 86400
        key = (packet.device_id, today)
        current_day_kwh = self.daily_usage.get(key, 0.0) + kwh

        if current_day_kwh > DAILY_KWH_CAP:
            kwh = max(0.0, DAILY_KWH_CAP - self.daily_usage.get(key, 0.0))
            if kwh <= 0:
                return None  # Cap reached

        # 4. Store
        reading = EnergyReading(
            device_id=packet.device_id,
            kwh=kwh,
            timestamp=packet.timestamp,
            verified=True,
            cable_type=cable_type
        )
        self.db.insert(reading)
        self.daily_usage[key] = current_day_kwh

        return reading


# === MOCK DB (for testing) ===
class MockDB:
    def __init__(self):
        self.readings = []

    def insert(self, reading: EnergyReading):
        self.readings.append(reading.dict())
        print(f"STORED: {reading.kwh:.6f} kWh via {reading.cable_type} @ {reading.timestamp}")


# === EXAMPLE (Type-C Cable) ===
if __name__ == "__main__":
    db = MockDB()
    processor = EnergyProcessor(db)

    # Mock device public key (replace with real)
    public_key = bytes.fromhex("a" * 64)

    # Mock packet from Type-C cable
    packet = VIRPacket(
        device_id=bytes.fromhex("01" * 32),
        voltage=12.0,
        current=1.5,
        resistance=8.0,
        timestamp=int(time.time()),
        signature=bytes(64)  # Real signature in production
    )

    result = processor.process_packet(packet, public_key, cable_type="type-c")
    if result:
        print(f"MINED: {result.kwh:.6f} kWh via {result.cable_type}")
