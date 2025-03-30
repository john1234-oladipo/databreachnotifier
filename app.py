import requests
import hashlib
import sys
from getpass import getpass

class DataBreachNotifier:
    def __init__(self):
        self.api_url = "https://haveibeenpwned.com/api/v3/"
        self.headers = {
            "User-Agent": "DataBreachNotifier/1.0",
            "hibp-api-key": ""  # You'll need to get an API key from HIBP
        }
        
    def check_email_breach(self, email):
        """Check if an email has been involved in a data breach"""
        try:
            response = requests.get(
                f"{self.api_url}breachedaccount/{email}",
                headers=self.headers,
                params={"truncateResponse": "false"}
            )
            
            if response.status_code == 200:
                breaches = response.json()
                print(f"\n\033[91m[!] Email found in {len(breaches)} breaches:\033[0m")
                for breach in breaches:
                    print(f"- {breach['Name']} ({breach['BreachDate']})")
                    print(f"  Details: {breach['Description']}")
                    print(f"  Compromised data: {', '.join(breach['DataClasses'])}")
                return True
            elif response.status_code == 404:
                print("\n\033[92m[+] No breaches found for this email\033[0m")
                return False
            else:
                print(f"\n\033[93m[?] API Error: {response.status_code}\033[0m")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"\n\033[93m[!] Connection error: {e}\033[0m")
            return None
    
    def check_password_breach(self, password):
        """Check if a password has been exposed in data breaches"""
        try:
            # Hash the password using SHA-1
            sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix, suffix = sha1_password[:5], sha1_password[5:]
            
            # Make a k-anonymity request
            response = requests.get(
                f"https://api.pwnedpasswords.com/range/{prefix}",
                headers={"User-Agent": "DataBreachNotifier/1.0"}
            )
            
            if response.status_code == 200:
                hashes = (line.split(':') for line in response.text.splitlines())
                for h, count in hashes:
                    if h == suffix:
                        print(f"\n\033[91m[!] Password has been found in {count} breaches!\033[0m")
                        print("You should change this password immediately.")
                        return True
                print("\n\033[92m[+] Password not found in any known breaches\033[0m")
                return False
            else:
                print(f"\n\033[93m[?] API Error: {response.status_code}\033[0m")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"\n\033[93m[!] Connection error: {e}\033[0m")
            return None

def main():
    print("\n\033[1mData Breach Notifier\033[0m")
    print("Checks if your email or password has been compromised in known data breaches\n")
    
    notifier = DataBreachNotifier()
    
    while True:
        print("\nOptions:")
        print("1. Check email address")
        print("2. Check password")
        print("3. Exit")
        
        choice = input("\nSelect an option (1-3): ")
        
        if choice == "1":
            email = input("Enter email address to check: ").strip()
            if "@" not in email or "." not in email:
                print("Please enter a valid email address")
                continue
                
            result = notifier.check_email_breach(email)
            if result:
                print("\n\033[1mRecommendations:\033[0m")
                print("- Change passwords for any accounts using this email")
                print("- Enable two-factor authentication where available")
                print("- Consider using a password manager")
                
        elif choice == "2":
            print("\nWarning: For security, this will only send the first 5 characters of your password's hash")
            password = getpass("Enter password to check (input hidden): ").strip()
            if not password:
                print("Please enter a password")
                continue
                
            notifier.check_password_breach(password)
            
        elif choice == "3":
            print("\nExiting... Stay safe online!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please select 1, 2, or 3.")

if __name__ == "__main__":
    # Note: You need to get an API key from Have I Been Pwned and add it to the headers
    print("Note: Before using this tool, you need to:")
    print("1. Get a free API key from https://haveibeenpwned.com/API/Key")
    print("2. Add it to the 'hibp-api-key' in the headers dictionary")
    main()
