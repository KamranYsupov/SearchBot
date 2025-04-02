import asyncio

from pyrogram import Client


async def login(
        name: str,
        api_id: int | str,
        api_hash: str,
        phone_number: str,
):
    async with Client(
        name=name,
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number,
    ) as client:
        print(f'session string: {await client.export_session_string()}')

sesstion_str = """
AgGB-aMAkdKcUKr8jjlzO8CkMX6qL8FgNsZshn0NNGzn0ts9xgxo8I76oDHPDvV_3TJj91klyXpJ-sHxSY_MrOWANFQ8q40WOGiHTxR2tTlU8Lmo5C7JnyTn8tgmOf4oE8RuRgy3XT2cJHHCUGiNmVIgIFVoEZaOgj5-q5RacLnegv1m6PfZNiMbIdY7EWcFmERhHln0vbQN2J9HvTKvXw-UKyHWDa_9DzsU9FpEcGhlK0sFcFBX4Um_s9pclU-mVesI4uVyD_G2gYIzlqXF2TaIvCOYjDEH9VgJKYdDgg3SOFNqGYm0f5zUSNH1EN6U8cl2hpDvNRsjzrKzWOkWVb6SGux6-wAAAAHIkacVAA
"""
if __name__ == '__main__':
    name = input('Введите username: ')
    api_id = input('Введите api_id: ')
    api_hash = input('Введите api_hash: ')
    phone_number = input('Введите номер телефона: ')

    asyncio.run(
        login(
            name=name,
            api_id=api_id,
            api_hash=api_hash,
            phone_number=phone_number,
        )
    )


