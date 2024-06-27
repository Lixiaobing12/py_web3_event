from utils.web3 import getW3
import os
import json


def getContract():
    w3 = getW3()
    address = os.getenv("MINER")
    abi = None
    with open("utils/abis/miner.json", "r") as f:
        abi = json.load(f)
    contract = w3.eth.contract(address=address, abi=abi)
    return contract
