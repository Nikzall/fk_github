from eth_account import Account
import secrets
from datetime import datetime

def generate_wallet():
    # Генерируем случайный приватный ключ
    priv = secrets.token_hex(32)
    private_key = "0x" + priv
    
    # Создаем аккаунт из приватного ключа
    acct = Account.from_key(private_key)
    
    return {
        'address': acct.address,
        'private_key': private_key
    }

def save_wallets_to_file(wallets, filename=None):
    # Если имя файла не указано, создаем имя с текущей датой
    if filename is None:
        now = datetime.now()
        filename = f'wallets_{now.strftime("%Y%m%d_%H%M%S")}.txt'
    
    # Записываем все кошельки в файл
    with open(filename, 'w') as f:
        for wallet in wallets:
            # Записываем адрес и приватный ключ через запятую
            f.write(f"{wallet['address']},{wallet['private_key']}\n")
    
    return filename

def main():
    # Количество кошельков для генерации
    num_wallets = int(input("Сколько кошельков вы хотите создать? "))
    
    # Список для хранения всех сгенерированных кошельков
    wallets = []
    
    # Генерируем кошельки
    for i in range(num_wallets):
        wallet = generate_wallet()
        wallets.append(wallet)
        print(f"\nКошелек #{i+1} создан")
        print(f"Адрес: {wallet['address']}")
        print(f"Приватный ключ: {wallet['private_key']}")
    
    # Сохраняем все кошельки в один файл
    filename = save_wallets_to_file(wallets)
    print(f"\nВсе кошельки сохранены в файл: {filename}")

if __name__ == "__main__":
    main()