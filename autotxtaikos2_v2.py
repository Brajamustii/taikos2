import time
import json
from web3 import Web3
from datetime import datetime, timedelta
import pytz

web3 = Web3(Web3.HTTPProvider(input("Input RPC Taiko Using https:// : ")))
chainId = web3.eth.chain_id

#connecting web3
if  web3.is_connected() == True:
    print("Web3 Connected...\n")
else:
    print("Error Connecting Exit...")
    exit()

# Transaction limits
MAX_TX_PER_DAY = int(input("Input Max Transaction Limit Per Days : "))

# Store the number of transactions sent today
tx_count_today = 0

# Timezone for Jakarta (Asia/Jakarta timezone)
LOCAL_TIMEZONE = pytz.timezone("Asia/Jakarta")

print('Auto TX Fast Taiko | @ylasgamers')
print('')
voteaddr = web3.to_checksum_address("0x4D1E2145082d0AB0fDa4a973dC4887C7295e21aB")
voteabi = json.loads('[{"stateMutability":"payable","type":"fallback"},{"inputs":[],"name":"vote","outputs":[],"stateMutability":"payable","type":"function"}]')
vote_contract = web3.eth.contract(address=voteaddr, abi=voteabi)

# Input manual untuk jeda waktu antar transaksi dalam menit
delay_minutes = int(input("Input jeda waktu transaksi dalam menit: "))
delay_seconds = delay_minutes * 60

def get_next_reset_time():
    """Get the next scheduled reset time (7:01 AM Jakarta time)."""
    now = datetime.now(LOCAL_TIMEZONE)
    next_reset = now.replace(hour=7, minute=0, second=1, microsecond=0)
    if now >= next_reset:
        # If it's already past 7:01 AM, set the next reset to 7:01 AM tomorrow
        next_reset += timedelta(days=1)
    return next_reset

def reset_tx_count():
    """Reset the transaction count at the next 7:01 AM Jakarta time."""
    global tx_count_today
    next_reset_time = get_next_reset_time()

    # Wait until it's time for the reset
    time_to_wait = (next_reset_time - datetime.now(LOCAL_TIMEZONE)).total_seconds()
    if time_to_wait > 0:
        print(f"Waiting {time_to_wait:.0f} seconds until next reset at {next_reset_time}.")
        time.sleep(time_to_wait)

    # Reset the count
    tx_count_today = 0
    print(f"Transaction count reset at {next_reset_time} Jakarta time.")
    
def vote(wallet, key):
    global tx_count_today

    # Check if we can send more transactions today
    if tx_count_today >= MAX_TX_PER_DAY:
        print(f"Maximum daily transaction limit of {MAX_TX_PER_DAY} reached.")
        return
    try:
        nonce = web3.eth.get_transaction_count(wallet)
        gasAmount = vote_contract.functions.vote().estimate_gas({
            'chainId': chainId,
            'from': wallet
        })
        gasPrice = 5050/gasAmount
        votetx = vote_contract.functions.vote().build_transaction({
            'chainId': chainId,
            'from': wallet,
            'gas': gasAmount,
            'maxFeePerGas': web3.to_wei(gasPrice, 'gwei'),
            'maxPriorityFeePerGas': web3.to_wei(gasPrice, 'gwei'),
            'nonce': nonce
        })
        #sign & send the transaction
        print(f'Processing Vote For Wallet Address {wallet} ...')
        tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(votetx, key).rawTransaction)
        print(f'Processing Vote Success!')
        tx_count_today += 1
        print(f'TX-ID : {str(web3.to_hex(tx_hash))}')
        print(f'')
        time.sleep(delay_seconds)
    except Exception as e:
        print(f'Error: {e}')
        print(f'Will Try Again...')
        vote(wallet, key)
        pass

while True:
    with open('pvkeylist.txt', 'r') as file:
        pvkeylist = file.read().splitlines()
        for loadkey in pvkeylist:
            wallet = web3.eth.account.from_key(loadkey)
            vote(wallet.address, wallet.key)
            reset_tx_count()
