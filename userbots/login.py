from pyrogram import Client


if __name__ == '__main__':
    username = input('Введите username: ')
    api_id = input('Введите api_id: ')
    api_hash = input('Введите api_hash: ')
    phone_number = input('Введите номер телефона: ')

    client_data = dict(
        name=username,
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number,
    )

    client = Client(
        name=username,
        api_id=api_id,
        api_hash=api_hash,
        phone_number=phone_number,
    )

    client.run()


