# Carbon Smart Meter
At Carbon Credits Marketplace we broker the transparent purchase and retiring of verified carbon credits, both on-chain and in the real world. Our flagship innovation, the Carbon Smart Meter, transforms portable solar panels into verifiable offset devices. Capturing real time energy data, estimating avoided emissions, and triggering smart contract rewards. This positions CCM at the intersection of decentralized physical infrastructure (DePIN), climate finance, and on chain utility.

Project Introduction Video: https://youtu.be/hq5Qa1ZrDtM?si=-YKWUaBQCdo8NVBT

## The Vision

Buy a panel. Charge your device. Earn rewards. Offset CO₂. All on-chain.

Carbon Smart Meter turns every solar charge into verified, tokenized carbon offsets and rewards, powered by DePIN hardware and open source smart contracts.

We are Carbon Credits Marketplace (CCM) — NZ founded, globally operational, and building CORSIA/IATA compliant offset pipelines from Argentina. We bridge aviation decarbonization with off grid energy access.

## How It Works (3 Steps)
1. Buy a CCM certified portable solar panel (20–100W)
2. Download the Carbon Smart Meter web app
3. Bond device to wallet → Start charging → Start mining → Earn rewards → Generate offsets

## Market Opportunity
1) Aviation CORSIA offset supply ($300B+), Solar IoT off-grid charging ($200B+), Environmental monitoring field science ($100B+). Source: Global Growth Insights – Carbon Offset Market.
2) A large majority of EU resident Europeans continue to view climate change as a serious global threat, with 85% of citizens identifying it as a major problem. Support for EU climate policy remains strong: 81% back the EU wide goal of climate neutrality by 2050. According to a 2021 Eurobarometer survey, a large majority of European Union (EU) citizens (82%) are prepared to change their habits to support sustainable tourism. Travel statistics also confirm a significant and growing base of potential customers who align with our product's value proposition. The potential market size is in the hundreds of millions within a multi-billion-dollar portable solar market.
3) Retrofit installation to existing solar panel systems: Into the billions of dollars across multipple regions.

## Target Users
- Aviation professionals
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
- Home owners and landlords
- Commercial property owners

## Tech Stack
Hardware (field-tested): 20–100W foldable panels (Asia, Africa, South America testing complete), embedded VIR sensor (voltage, current, resistance → kWh), tamper proof USB-C/ Type C/ 12v adapter, smartphone/tablet hosts wallet + app.

Software (open source): Web app (kWh → CO₂ avoided using region specific grid intensity), Smart contract (Bitcoin style halving, threshold rewards), Wallet binding (device ID + on chain registration), Multi chain ready (Solana, Ethereum, Polkadot, Cosmos).

Apache-2.0: use, modify, deploy. Build your own node.

## Security & Verification
- Physical connection required
- Device + wallet binding prevents spoofing
- On chain immutability: all rewards traceable
- Gold Standard pipeline: verified offset issuance attainable with correct funding.

## Validation
DePIN Presentation (2:45) — How we validate kWh → offsets on-chain. Watch on YouTube: https://youtu.be/hq5Qa1ZrDtM?si=dpDBE9hjaM7-akEi&t=105

## Architecture
[Hardware] → VIR Sensor + Microchip → Web App → kWh conversion → Smart Contract → [rewards + Offset]

Adapter layer: plug in any L1 (blockchain/adapter.py)  
Rust BPF program: on-chain logic (examples/solana_program/)  
Python backend: off-chain processing (src/carbon_smart_meter/)

## Sustainable Payout Model
- 9 kWh/day cap per device, future proofing retro fit customers
- Rewards tied to the market cost of electricity in the given region. So 10–30% of regional electricity price paid in rewards
- Inverse token scaling: early users get more rewards
- Revenue backed: brokerage and verification fees, anonymized data on renewable energy generation sales and hardware sales margin.

## Get Started
pip install -e .  
python examples1/run_solana.py

## Built for Scale
- Open-source core (Apache-2.0)
- Multi-chain adapters (one repo, 20+ L1s)
- Real-world tested panels deployed globally
- CORSIA/IATA compliant design for aviation grade offset standards
- Plenty of upside to develop retrofit products that can be shipped and sold globally.

Built by Carbon Credits Marketplace (CCM)  
Powered by rewards  
Anchored in real offsets  
Designed for global adoption

License: Apache License 2.0 (see LICENSE)
