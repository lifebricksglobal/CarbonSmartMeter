# tests/test_registration.py
from carbon_smart_meter.core.registration import RegistrationManager, generate_device_registration, MockRegistrationDB

def test_device_registration():
    db = MockRegistrationDB()
    manager = RegistrationManager(db)

    request = generate_device_registration("9vA1B2cD...")
    binding = manager.register_device(request)

    assert binding is not None
    assert binding.device_id == request.device_id
    assert binding.wallet_address == "9vA1B2cD..."

    # Duplicate fails
    assert manager.register_device(request) is None