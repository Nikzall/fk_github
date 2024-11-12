import aiohttp
import asyncio
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def read_addresses(file_path):
    try:
        with open(file_path, 'r') as file:
            addresses = file.read().splitlines()
        logging.info(f"Successfully read {len(addresses)} addresses from {file_path}")
        return addresses
    except Exception as e:
        logging.error(f"Failed to read addresses from {file_path}: {e}")
        return []

async def fetch_address_info(session, address, max_retries=3):
    headers = {
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'X-OYL-API-KEY': 'd6aebfed1769128379aca7d215f0b689',
    }
    json_data = {'address': address}

    for attempt in range(max_retries):
        try:
            async with session.post(
                'https://mainnet-api.oyl.gg/get-whitelist-leaderboard', 
                headers=headers, 
                json=json_data
            ) as response:
                if response.status == 200:
                    logging.info(f"Response recieved for address {address}")
                    return await response.json()
                
            # Если не 200, подождем и попробуем снова
            await asyncio.sleep(1)
            logging.info(f"Request made for address {address}: Status Code {response.status} \n")

        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed for address {address}: {e}")
            if attempt < max_retries - 1:  # Если есть еще попытки
                await asyncio.sleep(1)
                continue
            return None
            
    return None

async def process_addresses(file_path, output_excel):
    addresses = await read_addresses(file_path)
    data = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_address_info(session, address) for address in addresses]
        responses = await asyncio.gather(*tasks)

        # Process each response
        for address, info in zip(addresses, responses):
            if info:
                data.append({
                    'address': address,
                    'wallet_rank': info.get('walletRank'),
                    'whale': info.get('whale'),
                    'priority': info.get('priority'),
                    'fatMeter': info.get('fatMeter'),
                    'guaranteedMint': info.get('guaranteedMint'),
                })
    
    # Convert the data list to a DataFrame and save it to Excel
    df = pd.DataFrame(data)
    try:
        df.to_excel(output_excel, index=False)
        logging.info(f"Data successfully saved to {output_excel}")
    except Exception as e:
        logging.error(f"Failed to save data to {output_excel}: {e}")

def main():
    file_path = "addresses_check.txt"
    output_excel = "results.xlsx"
    asyncio.run(process_addresses(file_path, output_excel))

if __name__ == "__main__":
    main()
