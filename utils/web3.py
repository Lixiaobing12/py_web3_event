from web3 import Web3, HTTPProvider
import os
from web3.middleware import geth_poa_middleware


def getW3():
    w3 = Web3(HTTPProvider(os.getenv("RPC")))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)

    return w3
