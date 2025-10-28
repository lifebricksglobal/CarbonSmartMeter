python<br>from pydantic import BaseModel<br><br>class Measurement(BaseModel):<br>    device_id: bytes<br>    kwh: int<br>    signature: bytes<br><br>def submit(measurement, adapter):<br>    return adapter.submit_kwh(measurement.device_id, measurement.kwh, measurement.signature)<br>

