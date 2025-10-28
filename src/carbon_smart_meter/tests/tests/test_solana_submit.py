# tests/test_solana_submit.py
from carbon_smart_meter.blockchain.solana import SolanaSubmitter
from solana.keypair import Keypair

def test_submit_signature_verification():
    wallet = Keypair()
    submitter = SolanaSubmitter(wallet)

    # Invalid signature → fails
    tx_sig = submitter.submit_kwh(
        device_id=b"0"*32,
        public_key=b"a"*32,
        kwh=1000,
        signature=b"bad"*64
    )
    assert tx_sig is None