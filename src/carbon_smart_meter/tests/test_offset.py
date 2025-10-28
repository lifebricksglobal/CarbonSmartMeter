# tests/test_offset.py
from carbon_smart_meter.core.offset import OffsetEngine, SecureOffsetDB

def test_offset_calculation():
    db = SecureOffsetDB(user_region="EU")
    engine = OffsetEngine(db)

    record = engine.process_verified_reading(
        device_id=b"0"*32,
        wallet_address="test",
        kwh=5.0,
        timestamp=1000000000,
        region="NZ"
    )
    assert record.co2_kg == 0.55  # 5 * 0.11

    record2 = engine.process_verified_reading(
        device_id=b"0"*32,
        wallet_address="test",
        kwh=3.0,
        timestamp=1000000001,
        region="CN"
    )
    assert record2.co2_kg == 1.71  # 3 * 0.57