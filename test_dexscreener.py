import aiohttp
import asyncio
import json

async def test_dexscreener():
    print("Testing DexScreener API...")
    
    async with aiohttp.ClientSession() as session:
        # Test with token-profiles endpoint
        url = "https://api.dexscreener.com/token-profiles/latest/v1"
        print(f"\nTesting URL: {url}")
        
        try:
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(json.dumps(data, indent=2))
                else:
                    print(f"Error response: {await response.text()}")
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_dexscreener())
