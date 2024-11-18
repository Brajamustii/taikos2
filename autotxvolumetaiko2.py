from web3 import Web3, HTTPProvider
import json
from decimal import Decimal

web3 = Web3(Web3.HTTPProvider(input("Input RPC Taiko Using https:// : ")))
chainId = web3.eth.chain_id

#connecting web3
if  web3.is_connected() == True:
    print("Web3 Connected...\n")
else:
    print("Error Connecting Please Try Again...")
    exit()

print('Auto TX Volume Ether Fast Taiko | @ylasgamers')
amounteth = float(input('Input Amount Of ETH To Send : '))
print('')
sendetheraddr = web3.to_checksum_address("0x000010A9D6e564d0c7fC9c79BcA1798C2114B5Aa")
sendetherabi = json.loads('[{"inputs":[{"internalType":"address","name":"target","type":"address"}],"name":"send","outputs":[],"stateMutability":"payable","type":"function"}]')
sendether_contract = web3.eth.contract(address=sendetheraddr, abi=sendetherabi)

def send(wallet, key, amount):
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
            print(f'TX-ID : {str(web3.to_hex(tx_hash))}')
            print(f'')
    except Exception as e:
        print(f'Error: {e}')
        print(f'Will Try Again...')
        pass

while True:
    with open('pvkeylist.txt', 'r') as file:
        pvkeylist = file.read().splitlines()
        for loadkey in pvkeylist:
            wallet = web3.eth.account.from_key(loadkey)
            send(wallet.address, wallet.key, amounteth)