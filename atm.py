class ATM:
    def __init__(self, initial_balance=1000, pin="1234"):
        self.balance = initial_balance
        self.pin = pin

    def authenticate(self):
        attempts = 3
        while attempts > 0:
            entered_pin = input("Enter your 4-digit PIN: ")
            if entered_pin == self.pin:
                print("Authentication successful!\n")
                return True
            else:
                attempts -= 1
                print(f"Incorrect PIN. {attempts} attempts remaining.")
        print("Too many incorrect attempts. Card blocked.")
        return False

    def check_balance(self):
        print(f"Your current balance is ₹{self.balance:.2f}\n")

    def deposit(self):
        try:
            amount = float(input("Enter amount to deposit: ₹"))
            if amount > 0:
                self.balance += amount
                print(f"Successfully deposited ₹{amount:.2f}")
                self.check_balance()
            else:
                print("Invalid amount. Please enter a positive number.")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    def withdraw(self):
        try:
            amount = float(input("Enter amount to withdraw: ₹"))
            if amount <= 0:
                print("Invalid amount. Please enter a positive number.")
            elif amount > self.balance:
                print("Insufficient balance.")
            else:
                self.balance -= amount
                print(f"Successfully withdrawn ₹{amount:.2f}")
                self.check_balance()
        except ValueError:
            print("Invalid input. Please enter a numeric value.")

    def run(self):
        if not self.authenticate():
            return
        while True:
            print("===== ATM Menu =====")
            print("1. Check Balance")
            print("2. Deposit Money")
            print("3. Withdraw Money")
            print("4. Exit")
            choice = input("Choose an option (1-4): ")

            if choice == "1":
                self.check_balance()
            elif choice == "2":
                self.deposit()
            elif choice == "3":
                self.withdraw()
            elif choice == "4":
                print("Thank you for using the ATM. Goodbye!")
                break
            else:
                print("Invalid option. Please choose again.\n")


if __name__ == "__main__":
    atm = ATM()
    atm.run()
