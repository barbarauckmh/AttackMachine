from modules.interfaces import SoftwareException
from utils.tools import helper, gas_checker
from modules import Minter, Logger
from config import ZKSTARS_CONTRACTS, ZKSTARS_ABI
from settings import ZKSTARS_NFT_CONTRACTS


class ZkStars(Minter, Logger):
    def __init__(self, client):
        self.client = client
        Logger.__init__(self)
        self.network = self.client.network.name

    async def get_new_nft_id(self):
        for contract_id, contract_address in list(ZKSTARS_CONTRACTS[self.network].items()):
            if ZKSTARS_NFT_CONTRACTS == 0 or contract_id in ZKSTARS_NFT_CONTRACTS:
                nft_contract = self.client.get_contract(contract_address=contract_address, abi=ZKSTARS_ABI)
                if not (await nft_contract.functions.balanceOf(self.client.address).call()):
                    return nft_contract, contract_id

        raise SoftwareException('All StarkStars NFT have been minted')

    @helper
    @gas_checker
    async def mint(self):
        nft_contract, contact_id = await self.get_new_nft_id()

        mint_price_in_wei = await nft_contract.functions.getPrice().call()
        mint_price = f"{(mint_price_in_wei / 10 ** 18):.5f}"

        self.logger_msg(*self.client.acc_info, msg=f"Mint zkStars#00{contact_id:0>2} NFT. Price: {mint_price} ETH")

        transaction = await nft_contract.functions.safeMint(
            "0x5f1a69Ec0B4860FF0FB7DA21fDd4e2C5837D14ca"
        ).build_transaction(await self.client.prepare_transaction(value=mint_price_in_wei))

        return await self.client.send_transaction(transaction)
