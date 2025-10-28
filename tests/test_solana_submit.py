# tests/test_solana_submit.py
from unittest.mock import patch
from carbon_smart_meter.blockchain.solana import SolanaSubmitter
from solana.keypair import Keypair

# def test_invalid_signature():
    wallet = Keypair()
    submitter = SolanaSubmitter(wallet)

    with patch.object(submitter, '_verify_device_sig', return_value=False):
        result = submitter.submit_kwh(
            device_id=b"0"*32,
            public_key=b"a"*32,
            kwh=1000,
            signature=b"bad"*64
        )
        assert result is None