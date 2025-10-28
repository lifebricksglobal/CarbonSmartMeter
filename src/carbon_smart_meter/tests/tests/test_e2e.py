# tests/test_e2e.py
def test_full_flow():
    from carbon_smart_meter.core.mining import EnergyProcessor
    from carbon_smart_meter.core.registration import RegistrationManager, generate_device_registration
    from carbon_smart_meter.core.offset import OffsetEngine
    from carbon_smart_meter.blockchain.solana import SolanaSubmitter
    from solana.keypair import Keypair

    # 1. Register
    reg_manager = RegistrationManager(MockRegistrationDB())
    req = generate_device_registration("wallet123")
    binding = reg_manager.register_device(req)
    assert binding

    # 2. Mine
    processor = EnergyProcessor(user_region="NZ")
    result = processor.process_packet(req.device_id, req.public_key, "type-c")
    assert result

    # 3. Offset
    offset_engine = OffsetEngine(SecureOffsetDB("NZ"))
    offset = offset_engine.process_verified_reading(
        device_id=req.device_id,
        wallet_address="wallet123",
        kwh=1.0,
        timestamp=1000000000,
        region="NZ"
    )
    assert offset.co2_kg > 0

    # 4. Submit
    submitter = SolanaSubmitter(Keypair())
    tx_sig = submitter.submit_kwh(
        device_id=req.device_id,
        public_key=req.public_key,
        kwh=1000,
        signature=req.signature
    )
    assert tx_sig is not None  # In real: check on-chain