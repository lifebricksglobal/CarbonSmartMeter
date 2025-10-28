# tests/test_mining.py
import pytest
from carbon_smart_meter.core.mining import EnergyProcessor, VIRPacket, SecureEnergyDB
from nacl.signing import SigningKey
import struct

def test_vir_to_kwh_conversion():
    from carbon_smart_meter.core.mining import vir_to_kwh
    assert vir_to_kwh(12.0, 1.0, 3600) == 12.0  # 12V * 1A * 1h = 12 kWh

def test_daily_cap_enforced():
    db = SecureEnergyDB(user_region="EU")
    processor = EnergyProcessor(user_region="EU")
    processor.db = db

    signing_key = SigningKey.generate()
    public_key = signing_key.verify_key.encode()
    device_id = b"0" * 32

    # First 9 kWh
    packet1 = VIRPacket(
        device_id=device_id,
        voltage=12.0, current=1.0, resistance=12.0,
        timestamp=1000000000,
        signature=signing_key.sign(device_id + struct.pack("<fffq", 12.0, 1.0, 12.0, 1000000000)).signature
    )
    result1 = processor.process_packet(packet1, public_key, "type-c")
    assert result1.kwh == 1.0  # 1 second sample

    # Exceed cap
    for _ in range(10):
        packet = VIRPacket(
            device_id=device_id,
            voltage=12.0, current=1.0, resistance=12.0,
            timestamp=1000000000 + _,
            signature=signing_key.sign(device_id + struct.pack("<fffq", 12.0, 1.0, 12.0, 1000000000 + _)).signature
        )
        processor.process_packet(packet, public_key, "type-c")

    assert processor.daily_usage.get((device_id, 1000000000 // 86400), 0) <= 9.0