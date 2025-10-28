python<br>from abc import ABC, abstractmethod<br><br>class BlockchainAdapter(ABC):<br>    @abstractmethod<br>    def submit_kwh(self, device_id: bytes, kwh: int, sig: bytes) -> str:<br>        pass<br>

