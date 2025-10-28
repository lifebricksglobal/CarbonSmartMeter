python<br>from carbon_smart_meter.blockchain.solana import SolanaAdapter<br>from carbon_smart_meter.core.mining import submit_measurement, Measurement<br><br>adapter = SolanaAdapter()<br>meas = Measurement(device_id=b'0'*32, kwh=1, signature=b'0'*64)<br>print("Tx:", submit_measurement(meas, adapter))<br>

