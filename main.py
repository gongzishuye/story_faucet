import random
import time
import asyncio
from typing import List

from modules.faucet import Faucet
from modules.tools import load_wallets, load_proxies, logger, request_proxy_format, sleeping
from settings import SHUFFLE_WALLETS, INFINITY_MODE

def process_address(address: str, proxy: dict | None):
    try:
        logger.info(f'Account {address} started! {proxy["http"] if proxy else "None"}')
        faucet = Faucet(address, proxy)
        faucet.claim_tokens()  # 保存返回值
    except AttributeError as e:
        logger.error(f'Account {address} error: claim_tokens may not be async! Error: {e}')
    except Exception as e:
        logger.error(f'Account {address} error!\n{str(e)}')

async def process_address_group(addresses: List[str], accounts_proxy: List[dict] | None):
    tasks = [
        asyncio.to_thread(
            process_address, 
            address, 
            random.choice(accounts_proxy) if accounts_proxy else None
        )
        for address in addresses
    ]
    await asyncio.gather(*tasks)

async def main():
    addresses = load_wallets('addresses.txt')
    accounts_proxy = load_proxies('proxies.txt', addresses)

    if SHUFFLE_WALLETS:
        # random.seed()
        # random.shuffle(addresses)
        pass

    # 将地址列表分组，每组5个
    batch_size = 3
    address_groups = [addresses[i:i + batch_size] for i in range(0, len(addresses), batch_size)]

    for group in address_groups:
        await process_address_group(group, accounts_proxy)
        sleeping()

if __name__ == "__main__":
    try:
        asyncio.run(main())
        # while True:
        #     asyncio.run(main())
        #     if INFINITY_MODE:
        #         logger.success('Accounts done, waiting 24h')
        #         time.sleep(3600*24)
    except KeyboardInterrupt:
        logger.warning("Cancelled by the user")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
