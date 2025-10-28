# src/carbon_smart_meter/blockchain/solana.py
"""
App-to-Device Tamper-Proof Protocol → Solana Submission

- Verifies Ed25519 signature from device
- Submits kWh to Solana BPF program
- Hard-wired only
"""

from typing import Optional
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.publickey import PublicKey
from solana.keypair import Keypair
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import struct

# === CONFIG ===
SOLANA_RPC = "https://api.devnet.solana.com"
PROGRAM_ID = PublicKey("YOUR_PROGRAM_ID_HERE")  # Replace after deploy
client = Client(SOLANA_RPC)


class SolanaSubmitter:
    def __init__(self, wallet: Keypair):
        self.wallet = wallet

    def submit_kwh(
        self,
        device_id: bytes,
        public_key: bytes,
        kwh: int,
        signature: bytes,
        market_cap: Optional[int] = None
    ) -> Optional[str]:
        if not self._verify_device_sig(device_id, public_key, signature):
            return None

        data = device_id + struct.pack("<Q", kwh) + signature
        if market_cap is not None:
            data += struct.pack("<Q", market_cap)

        tx = Transaction().add(
            {
                "keys": [
                    {"pubkey": self.wallet.public_key, "is_signer": True, "is_writable": True},
                    {"pubkey": PublicKey(0), "is_signer": False, "is_writable": True},
                    {"pubkey": PublicKey(0), "is_signer": False, "is_writable": True},
                    {"pubkey": PublicKey("SysvarC1ock11111111111111111111111111111111"), "is_signer": False, "is_writable": False},
                ],
                "program_id": PROGRAM_ID,
                "data": list(data),
            }
        )

        try:
            resp = client.send_transaction(tx, self.wallet)
            return resp["result"]
        except Exception as e:
            print(f"Submit failed: {e}")
            return None

    def _verify_device_sig(self, device_id: bytes, public_key: bytes, signature: bytes) -> bool:
        try:
            verify_key = VerifyKey(public_key)
            verify_key.verify(device_id, signature)
            return True
        except BadSignatureError:
            return False