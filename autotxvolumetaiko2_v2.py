from web3 import Web3, HTTPProvider
import json
from decimal import Decimal
from datetime import datetime, timedelta
import pytz

web3 = Web3(Web3.HTTPProvider(input("Input RPC Taiko Using https:// : ")))
chainId = web3.eth.chain_id

#connecting web3
if  web3.is_connected() == True:
    print("Web3 Connected...\n")
else:
    print("Error Connecting Please Try Again...")
    exit()

# Transaction limits
MAX_TX_PER_DAY = int(input("Input Max Transaction Limit Per Days : "))

# Store the number of transactions sent today
tx_count_today = 0

# Timezone for Jakarta (Asia/Jakarta timezone)
LOCAL_TIMEZONE = pytz.timezone("Asia/Jakarta")

print('Auto TX Volume Ether Fast Taiko | @ylasgamers')
amounteth = float(input('Input Amount Of ETH To Send : '))
print('')
sendetheraddr = web3.to_checksum_address("0x000010A9D6e564d0c7fC9c79BcA1798C2114B5Aa")
sendetherabi = json.loads('[{"inputs":[{"internalType":"address","name":"target","type":"address"}],"name":"send","outputs":[],"stateMutability":"payable","type":"function"}]')
sendether_contract = web3.eth.contract(address=sendetheraddr, abi=sendetherabi)

def get_next_reset_time():
    """Get the next scheduled reset time (7:00 AM Jakarta time)."""
    now = datetime.now(LOCAL_TIMEZONE)
    next_reset = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if now >= next_reset:
        # If it's already past 7:00 AM, set the next reset to 7:00 AM tomorrow
        next_reset += timedelta(days=1)
    return next_reset

def reset_tx_count():
    """Reset the transaction count at the next 7:00 AM Jakarta time."""
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

def send(wallet, key, amount):
    global tx_count_today

    # Check if we can send more transactions today
    if tx_count_today >= MAX_TX_PER_DAY:
        print(f"Maximum daily transaction limit of {MAX_TX_PER_DAY} reached.")
        return
    try:
        for i in range(0,15):
            sendamount = web3.to_wei(amount, 'ether')
            nonce = web3.eth.get_transaction_count(wallet)+i
            gasAmount = sendether_contract.functions.send(wallet).estimate_gas({
                'chainId': chainId,
                'from': wallet,
                'value': sendamount
            })
            gasPrice = web3.from_wei(web3.eth.gas_price, 'gwei')
            sendtx = sendether_contract.functions.send(wallet).build_transaction({
                'chainId': chainId,
                'from': wallet,
                'gas': gasAmount,
                'value': sendamount,
                'maxFeePerGas': web3.to_wei(gasPrice*Decimal(1.1), 'gwei'),
                'maxPriorityFeePerGas': web3.to_wei(gasPrice*Decimal(1.1), 'gwei'),
                'nonce': nonce
            })
            #sign & send the transaction
            print(f'Processing Send Ether From Address {wallet} ...')
            tx_hash = web3.eth.send_raw_transaction(web3.eth.account.sign_transaction(sendtx, key).rawTransaction)
            print(f'Processing Send Ether To Address {wallet} Success!')
            tx_count_today += 1
            print(f'TX-ID : {str(web3.to_hex(tx_hash))}')
            print(f'')
    except Exception as e:
        print(f'Error: {e}')
        print(f'Will Try Again...')
        send(wallet, key, amount)
        pass

while True:
    with open('pvkeylist.txt', 'r') as file:
        pvkeylist = file.read().splitlines()
        for loadkey in pvkeylist:
            wallet = web3.eth.account.from_key(loadkey)
            send(wallet.address, wallet.key, amounteth)
            reset_tx_count()