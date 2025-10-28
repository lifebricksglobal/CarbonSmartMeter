rust<br>use solana_program::{entrypoint::entrypoint, pubkey::Pubkey, account_info::AccountInfo, entrypoint::ProgramResult};<br><br>entrypoint!(process);<br><br>pub fn process(_program_id: &Pubkey, _accounts: &[AccountInfo], _data: &[u8]) -> ProgramResult {<br>    Ok(())\n}\n

// examples/solana_program/src/lib.rs
use solana_program::{
    account_info::{next_account_info, AccountInfo},
    clock::Clock,
    entrypoint,
    entrypoint::ProgramResult,
    msg,
    program_error::ProgramError,
    pubkey::Pubkey,
    sysvar::clock::Clock,
};
use borsh::{BorshDeserialize, BorshSerialize};

// === CONSTANTS ===
const DAILY_KWH_CAP: u64 = 9; // Max 9 kWh/day per device
const BASE_REWARD_PER_KWH: u64 = 25_000_000; // 25 CARBON per kWh (8 decimals)
const HALVING_INTERVAL: u64 = 1_051_200; // ~2 years
const BASE_MARKET_CAP: u64 = 1_000_000_000_000; // $1M in smallest unit
const MIN_REWARD_FACTOR: u64 = 50; // 0.5x
const MAX_REWARD_FACTOR: u64 = 200; // 2.0x

// === DATA STRUCTURES ===
#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct MiningAccount {
    pub device_id: [u8; 32],
    pub wallet: Pubkey,
    pub last_mined_day: u64,     // Unix day (UTC)
    pub daily_kwh: u64,          // kWh mined today
    pub cumulative_kwh: u64,
    pub last_reward_block: u64,
}

#[derive(BorshSerialize, BorshDeserialize, Debug)]
pub struct ProgramState {
    pub base_reward: u64,
    pub last_halving_block: u64,
    pub current_market_cap: u64,
}

// === ENTRYPOINT ===
entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &Pubkey,
    accounts: &[AccountInfo],
    instruction_data: &[u8],
) -> ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let mining_acc = next_account_info(accounts_iter)?;
    let state_acc = next_account_info(accounts_iter)?;
    let token_acc = next_account_info(accounts_iter)?;
    let user_wallet = next_account_info(accounts_iter)?;
    let clock = Clock::get()?;

    let mut mining = MiningAccount::try_from_slice(&mining_acc.data.borrow())?;
    let mut state = ProgramState::try_from_slice(&state_acc.data.borrow())?;

    // Parse: [device_id(32), kwh(8), sig(64), market_cap(8)]
    let device_id = &instruction_data[0..32];
    let kwh = u64::from_le_bytes(instruction_data[32..40].try_into().unwrap());
    let signature = &instruction_data[40..104];
    let market_cap = if instruction_data.len() >= 112 {
        u64::from_le_bytes(instruction_data[104..112].try_into().unwrap())
    } else {
        state.current_market_cap
    };

    // === VALIDATIONS ===
    if mining.device_id != *device_id {
        return Err(ProgramError::InvalidAccountData);
    }
    if !verify_signature(device_id, &mining.wallet, signature) {
        return Err(ProgramError::InvalidInstructionData);
    }

    let current_day = clock.unix_timestamp / 86_400;

    // Reset daily counter if new day
    if mining.last_mined_day < current_day {
        mining.daily_kwh = 0;
        mining.last_mined_day = current_day;
    }

    // Enforce 9 kWh/day cap
    let allowed_kwh = (DAILY_KWH_CAP - mining.daily_kwh).min(kwh);
    if allowed_kwh == 0 {
        return Err(ProgramError::Custom(1)); // "Daily cap reached"
    }

    // === DYNAMIC REWARD ===
    let reward_rate = calculate_reward_rate(&state, market_cap);
    let reward = allowed_kwh * reward_rate;

    // === HALVING ===
    if clock.slot - state.last_halving_block >= HALVING_INTERVAL {
        state.base_reward /= 2;
        state.last_halving_block = clock.slot;
    }

    // === PAYOUT ===
    transfer_tokens(token_acc, user_wallet, reward)?;
    mining.daily_kwh += allowed_kwh;
    mining.cumulative_kwh += allowed_kwh;
    mining.last_reward_block = clock.slot;

    // === SAVE ===
    mining.serialize(&mut &mut mining_acc.data.borrow_mut()[..])?;
    state.serialize(&mut &mut state_acc.data.borrow_mut()[..])?;

    msg!("Mined {} kWh → {} $CARBON", allowed_kwh, reward);
    Ok(())
}

// === REWARD CALCULATION ===
fn calculate_reward_rate(state: &ProgramState, market_cap: u64) -> u64 {
    let scaling = if market_cap > 0 {
        (BASE_MARKET_CAP as u128)
            .checked_div(market_cap as u128)
            .unwrap_or(1) as u64
    } else { 1 };

    let scaled = (state.base_reward as u128 * scaling as u128) as u64;
    let bounded = scaled
        .max(state.base_reward * MIN_REWARD_FACTOR / 100)
        .min(state.base_reward * MAX_REWARD_FACTOR / 100);

    bounded
}

// === HELPERS ===
fn verify_signature(device_id: &[u8], wallet: &Pubkey, sig: &[u8]) -> bool {
    let msg = [device_id, wallet.as_ref()].concat();
    solana_program::ed25519::verify(&msg, sig).is_ok()
}

fn transfer_tokens(_from: &AccountInfo, _to: &AccountInfo, _amount: u64) -> ProgramResult {
    // TODO: Invoke SPL Token transfer
    Ok(())
}