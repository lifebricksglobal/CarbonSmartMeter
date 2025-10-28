rust<br>use solana_program::{entrypoint::entrypoint, pubkey::Pubkey, account_info::AccountInfo, entrypoint::ProgramResult};<br><br>entrypoint!(process);<br><br>pub fn process(_program_id: &Pubkey, _accounts: &[AccountInfo], _data: &[u8]) -> ProgramResult {<br>    Ok(())\n}\n

