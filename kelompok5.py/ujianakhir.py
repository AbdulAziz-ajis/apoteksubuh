import mysql.connector
import pyfiglet
from colorama import Fore, Style, init

# Initialize colorama for color support in terminal
init(autoreset=True)


big_name = pyfiglet.figlet_format("ApotikSubuh")
print(Fore.CYAN + big_name)  # Print the big name in cyan color

# Establishing connection to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",  # Your MySQL host, usually localhost
        user="root",       # Your MySQL username
        password="",       # Your MySQL password
        database="perusahaan1"  # Database name
    )

# Function to view all items in the stock
def view_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM barang_barang")
    items = cursor.fetchall()

    print(Fore.CYAN + "\n===== Inventory List =====")
    print(f"{'ID':<5} {'Nama Obat':<25} {'Merek Obat':<20} {'Stok Obat':<10} {'Harga':>10}")
    print("=" * 70)

    for item in items:
        print(f"{item[0]:<5} {item[1]:<25} {item[2]:<20} {item[3]:<10} {item[4]:>10.2f}")
    cursor.close()
    conn.close()

# Function to add a new item to the stock
def add_item():
    print(Fore.GREEN + "\n===== Add New Item =====")
    name = input("Enter the name of the medicine: ")
    brand = input("Enter the brand of the medicine: ")
    stock = int(input("Enter the stock of the medicine: "))
    price = float(input("Enter the price of the medicine: "))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO barang_barang (nama_obat, merek_obat, stok_obat, harga) VALUES (%s, %s, %s, %s)", 
                   (name, brand, stock, price))
    conn.commit()
    print(Fore.GREEN + f"Item '{name}' added successfully!")
    cursor.close()
    conn.close()

# Function to edit an existing item (full edit)
def edit_item():
    view_items()  # Show current items to choose from
    item_id = int(input(Fore.YELLOW + "\nEnter the ID of the item you want to edit: "))
    name = input("Enter the new name of the medicine: ")
    brand = input("Enter the new brand of the medicine: ")
    stock = int(input("Enter the new stock of the medicine: "))
    price = float(input("Enter the new price of the medicine: "))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE barang_barang
        SET nama_obat = %s, merek_obat = %s, stok_obat = %s, harga = %s
        WHERE no_id = %s
    """, (name, brand, stock, price, item_id))
    conn.commit()
    print(Fore.GREEN + "Item updated successfully!")
    cursor.close()
    conn.close()

# Function to update only the stock of an existing item
def update_stock():
    view_items()  # Show current items to choose from
    item_id = int(input(Fore.YELLOW + "\nEnter the ID of the item whose stock you want to update: "))
    new_stock = int(input("Enter the new stock quantity: "))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE barang_barang
        SET stok_obat = %s
        WHERE no_id = %s
    """, (new_stock, item_id))
    conn.commit()
    print(Fore.GREEN + f"Stock for item ID {item_id} updated to {new_stock}!")
    cursor.close()
    conn.close()

# Function to delete an item from stock
def delete_item():
    view_items()  # Show current items to choose from
    item_id = int(input(Fore.RED + "\nEnter the ID of the item you want to delete: "))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM barang_barang WHERE no_id = %s", (item_id,))
    conn.commit()
    print(Fore.RED + "Item deleted successfully!")
    cursor.close()
    conn.close()

# Function to handle the purchasing process and update stock
def buy_item():
    view_items()  # Show current items to choose from
    item_id = int(input(Fore.YELLOW + "\nEnter the ID of the item you want to buy: "))
    quantity = int(input("Enter the quantity you want to buy: "))
    
    # Ask for buyer name and check if the buyer exists in the database
    buyer_name = input("Enter the buyer's name: ")

    # Check if buyer exists in the pembeli table
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id_pembeli FROM pembeli WHERE nama_pembeli = %s", (buyer_name,))
    buyer = cursor.fetchone()

    if not buyer:
        # If buyer doesn't exist, ask if they want to create a new buyer
        create_new_buyer = input(Fore.MAGENTA + f"Buyer '{buyer_name}' not found. Do you want to create a new buyer? (y/n): ").strip().lower()
        if create_new_buyer == 'y':
            # Add new buyer to the pembeli table
            cursor.execute("INSERT INTO pembeli (nama_pembeli) VALUES (%s)", (buyer_name,))
            conn.commit()
            # Retrieve the new buyer's ID
            cursor.execute("SELECT id_pembeli FROM pembeli WHERE nama_pembeli = %s", (buyer_name,))
            buyer = cursor.fetchone()
            print(Fore.GREEN + f"New buyer '{buyer_name}' created with ID: {buyer[0]}")
        else:
            print(Fore.RED + "Purchase aborted. Buyer not found and not created.")
            cursor.close()
            conn.close()
            return

    buyer_id = buyer[0]  # Get the buyer's ID

    # Fetch the item details
    cursor.execute("SELECT * FROM barang_barang WHERE no_id = %s", (item_id,))
    item = cursor.fetchone()

    if item:
        item_name, item_brand, stock, price = item[1], item[2], item[3], item[4]
        
        if stock >= quantity:  # Check if enough stock is available
            total_price = price * quantity
            new_stock = stock - quantity  # Update stock
            
            # Update stock in barang_barang table
            cursor.execute("UPDATE barang_barang SET stok_obat = %s WHERE no_id = %s", (new_stock, item_id))
            conn.commit()

            # Insert transaction into riwayat_transaksi
            cursor.execute("""
                INSERT INTO riwayat_transaksi (id_pembeli, nama_pembeli, nama_obat, harga_obat, jumlah_stok_yang_dibeli, total_harga)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (buyer_id, buyer_name, item_name, price, quantity, total_price))
            conn.commit()

            print(Fore.GREEN + f"Purchase successful! Total price: {total_price}")
        else:
            print(Fore.RED + "Not enough stock available!")
    else:
        print(Fore.RED + "Item not found!")
    
    cursor.close()
    conn.close()

# Function to view the transaction history
def view_transaction_history():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id_pembeli, nama_pembeli, nama_obat, harga_obat, jumlah_stok_yang_dibeli, total_harga, tgl_waktu
        FROM riwayat_transaksi
        ORDER BY tgl_waktu DESC
    """)
    transactions = cursor.fetchall()

    print(Fore.CYAN + "\n===== Transaction History =====")
    print(f"{'ID Pembeli':<15} {'Nama Pembeli':<20} {'Nama Obat':<25} {'Harga Obat':>10} {'Jumlah':<10} {'Total Harga':>10} {'Tanggal':<20}")
    print("=" * 90)

    for transaction in transactions:
        print(f"{transaction[0]:<15} {transaction[1]:<20} {transaction[2]:<25} {transaction[3]:>10.2f} {transaction[4]:<10} {transaction[5]:>10.2f} {transaction[6]:<20}")
    
    cursor.close()
    conn.close()



# Function to display the menu and prompt user for input
def display_menu():
    while True:
        print(Fore.CYAN + "\n===== Main Menu =====")
        print(Fore.YELLOW + "1. View items")
        print(Fore.YELLOW + "2. Add a new item")
        print(Fore.YELLOW + "3. Edit an existing item")
        print(Fore.YELLOW + "4. Update stock of an item")
        print(Fore.YELLOW + "5. Delete an item")
        print(Fore.YELLOW + "6. Buy an item")
        print(Fore.YELLOW + "8. View Transaction History")
        print(Fore.RED + "7. Exit")
        
        choice = input(Fore.WHITE + "Choose an option (1-7): ")
        
        if choice == '1':
            view_items()
        elif choice == '2':
            add_item()
        elif choice == '3':
            edit_item()
        elif choice == '4':
            update_stock()  # New option for updating stock
        elif choice == '5':
            delete_item()
        elif choice == '6':
            buy_item()
        elif choice == '8':
            view_transaction_history()
        elif choice == '7':
            print(Fore.GREEN + "Exiting the program...")
            break
        else:
            print(Fore.RED + "Invalid choice! Please choose again.")

# Main function to run the application
if __name__ == "__main__":
    display_menu()