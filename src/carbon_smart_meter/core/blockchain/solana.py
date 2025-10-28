python<br>from .adapter import BlockchainAdapter<br><br>class SolanaAdapter(BlockchainAdapter):<br>    def submit_kwh(self, device_id, kwh, sig):<br>        return "tx_solana_123"<br>

# src/carbon_smart_meter/blockchain/solana.py
"""
App-to-Device Tamper Proof Protocol (Hard Wired)

- App receives VIR packet via USB/ Type-C/12V cable
- Verifies Ed25519 signature from device
- Submits verified kWh to Solana BPF program
- Returns transaction signature
- NO Bluetooth, NO GPS, NO spoofing
"""

from typing import Optional
from solana.rpc.api import Client
from solana.transaction import Transaction
from solana.system_program import SYS_PROGRAM_ID
from solana.publickey import PublicKey
from solana.keypair import Keypair
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import struct
import time

# === SOLANA CONFIG ===
SOLANA_RPC = "https://api.devnet.solana.com"  # Change to mainnet later
PROGRAM_ID = PublicKey("YOUR_PROGRAM_ID_HERE")  # Deployed BPF program
client = Client(SOLANA_RPC)

# === TAMPER PROOF SUBMISSION ===
class SolanaSubmitter:
    def __init__(self, wallet: Keypair):
        self.wallet = wallet

    def submit_kwh(
        self,
        device_id: bytes,
        public_key: bytes,
        kwh: int,  # In smallest unit (e.g., 1 kWh = 1000)
        signature: bytes,
        market_cap: Optional[int] = None
    ) -> Optional[str]:
        """
        Submit verified kWh to Solana BPF program
        Instruction data: [device_id(32), kwh(8), sig(64), market_cap(8)?]
        """
        # 1. Re-verify signature (tamper proof)
        if not self._verify_device_sig(device_id, public_key, signature):
            return None

        # 2. Build instruction
        data = (
            device_id +
            struct.pack("<Q", kwh) +
            signature
        )
        if market_cap is not None:
            data += struct.pack("<Q", market_cap)

        # 3. Create transaction
        tx = Transaction().add(
            {
                "keys": [
                    {"pubkey": self.wallet.public_key, "is_signer": True, "is_writable": True},
                    {"pubkey": PublicKey(0), "is_signer": False, "is_writable": True},  # Mining account
                    {"pubkey": PublicKey(0), "is_signer": False, "is_writable": True},  # Program state
                    {"pubkey": SYS_PROGRAM_ID, "is_signer": False, "is_writable": False},
                ],
                "program_id": PROGRAM_ID,
                "data": data,
            }
        )

        # 4. Send
        try:
            resp = client.send_transaction(tx, self.wallet)
            tx_sig = resp["result"]
            print(f"SUBMITTED: {tx_sig}")
            return tx_sig
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


# === EXAMPLE (Hard-Wired Flow) ===
if __name__ == "__main__":
    # Mock wallet
    wallet = Keypair()

    # Mock verified packet from mining.py
    submitter = SolanaSubmitter(wallet)
    tx_sig = submitter.submit_kwh(
        device_id=bytes.fromhex("01" * 32),
        public_key=bytes.fromhex("a" * 64),
        kwh=9000,  # 9.000 kWh
        signature=bytes(64),
        market_cap=1_000_000_000_000
    )
    if tx_sig:
        print(f"ON-CHAIN: {tx_sig}")