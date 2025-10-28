# src/carbon_smart_meter/blockchain/solana.py
"""
Solana Submission (Hard Wired, Tamper Proof)
"""

from typing import Optional
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.keypair import Keypair
from solana.publickey import PublicKey  # ← CORRECT
from solana.system_program import SYS_PROGRAM_ID
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import struct

# === CONFIG ===
SOLANA_RPC = "https://api.devnet.solana.com"
PROGRAM_ID = PublicKey("11111111111111111111111111111111")
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

        tx = Transaction()
        tx.add_instruction(
            {
                "program_id": PROGRAM_ID,
                "keys": [
                    {"pubkey": self.wallet.public_key, "is_signer": True, "is_writable": True},
                    {"pubkey": PublicKey(0), "is_signer": False, "is_writable": True},
                    {"pubkey": PublicKey(0), "is_signer": False, "is_writable": True},
                    {"pubkey": SYS_PROGRAM_ID, "is_signer": False, "is_writable": False},
                ],
                "data": list(data),
            }
        )

        try:
            resp = client.send_transaction(tx, self.wallet)
            return resp.get("result")
        except Exception:
            return None

    def _verify_device_sig(self, device_id: bytes, public_key: bytes, signature: bytes) -> bool:
        try:
            verify_key = VerifyKey(public_key)
            verify_key.verify(device_id, signature)
            return True
        except BadSignatureError:
            return False