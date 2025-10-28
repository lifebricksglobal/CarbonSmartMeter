# Carbon Smart Meter
CORSIA/IATA Methodology compliant Carbon Credit Broker + DePIN Solar Mining Network

Buy a panel. Charge your device. Earn $CARBON. Offset CO₂. All on-chain.

## The Vision
Carbon Smart Meter turns every solar charge into verified, tokenized carbon offsets and $CARBON rewards — powered by DePIN hardware and open source smart contracts.

We are Carbon Credits Marketplace (CCM) — NZ founded, globally operational, and building CORSIA/IATA compliant offset pipelines from Argentina. We bridge aviation decarbonization with off grid energy access.

## How It Works (3 Steps)
1. Buy a CCM certified portable solar panel (20–100W)
2. Download the Carbon Smart Meter web app
3. Bond device to wallet → Start charging → Start mining → Earn $CARBON → Generate offsets

## Market Opportunity
Aviation CORSIA offset supply ($300B+), Solar IoT off-grid charging ($200B+), Environmental monitoring field science ($100B+). Source: Global Growth Insights – Carbon Offset Market.

## Target Users
- Mobile phone manufacturers and distributers
- Campervans and travellers
- Beach goers and beach workers
- Holiday resorts: Pool side charging stations
- Military & Defense: silent charging in stealth ops
- Maritime: fishermen, coast guards, sailors
- Scientists & Conservationists: field research in protected zones
- Off-Grid Communities: energy + blockchain access
- Construction & Mining: remote site ESG reporting
- Events & ESG Retail: branded solar onboarding
- Migration Corridors: millions onboarded via solar rewards

One panel = one user = one offset = one $CARBON miner.

## Tech Stack
Hardware (field-tested): 20–100W foldable panels (Asia, Africa, South America), embedded VIR sensor (voltage, current, resistance → kWh), tamper proof USB-C/ Type C/ 12v adapter, smartphone/tablet hosts wallet + app.

Software (open source): Web app (kWh → CO₂ avoided using region specific grid intensity), Smart contract (Bitcoin style halving, threshold rewards), Wallet binding (device ID + on chain registration), Multi chain ready (Solana, Ethereum, Polkadot, Cosmos).

Apache-2.0 — use, modify, deploy. Build your own node.

## Security & Verification
- Physical connection required
- Device + wallet binding prevents spoofing
- On chain immutability: all rewards traceable
- Gold Standard pipeline: verified offset issuance attainable with correct funding.

## Validation
DePIN Presentation (2:45) — How we validate kWh → offsets on-chain. Watch on YouTube: https://youtu.be/hq5Qa1ZrDtM?si=dpDBE9hjaM7-akEi&t=105

## Architecture
[Hardware] → VIR Sensor + Microchip → Web App → kWh conversion → Smart Contract → [$CARBON + Offset]

Adapter layer: plug in any L1 (blockchain/adapter.py)  
Rust BPF program: on-chain logic (examples/solana_program/)  
Python backend: off-chain processing (src/carbon_smart_meter/)

## Get Started
pip install -e .  
python examples1/run_solana.py

## Built for Scale
- Open-source core (Apache-2.0)
- Multi-chain adapters (one repo, 20+ L1s)
- Real-world tested panels deployed globally
- CORSIA/IATA-compliant design for aviation-grade offset standards

Built by Carbon Credits Marketplace (CCM)  
Powered by $CARBON  
Anchored in real offsets  
Designed for global adoption

License: Apache License 2.0 (see LICENSE)