import requests
import hashlib
import sys
from getpass import getpass

class DataBreachNotifier:
    def __init__(self):
        self.apis = {
            'HIBP': {
                'email_url': "https://haveibeenpwned.com/api/v3/breachedaccount/",
                'headers': {
                    "User-Agent": "DataBreachNotifier/1.0",
                    "hibp-api-key": ""  # Add your HIBP API key here if available
                }
            },
            'BreachDirectory': {
                'email_url': "https://breachdirectory.p.rapidapi.com/",
                'headers': {
                    'x-rapidapi-key': "",
                    'x-rapidapi-host': "breachdirectory.p.rapidapi.com"
                }
            }
        }
        
    def check_email_breach(self, email, api_choice='auto'):
        """Check if an email has been involved in a data breach"""
        if api_choice == 'auto':
            # Try HIBP first if API key exists, otherwise fallback
            if self.apis['HIBP']['headers']['hibp-api-key']:
                api_choice = 'HIBP'
            else:
                api_choice = 'BreachDirectory'
        
        try:
            if api_choice == 'HIBP':
                response = requests.get(
                    f"{self.apis['HIBP']['email_url']}{email}",
                    headers=self.apis['HIBP']['headers'],
                    params={"truncateResponse": "false"}
                )
                
                if response.status_code == 200:
                    breaches = response.json()
                    print(f"\n\033[91m[!] Email found in {len(breaches)} breaches (via HIBP):\033[0m")
                    for breach in breaches:
                        print(f"- {breach['Name']} ({breach['BreachDate']})")
                        print(f"  Details: {breach['Description']}")
                        print(f"  Compromised data: {', '.join(breach['DataClasses'])}")
                    return True
                elif response.status_code == 404:
                    print("\n\033[92m[+] No breaches found for this email (HIBP)\033[0m")
                    return False
                else:
                    print(f"\n\033[93m[?] HIBP API Error: {response.status_code}\033[0m")
                    # Fallback to BreachDirectory if HIBP fails
                    return self.check_email_breach(email, api_choice='BreachDirectory')
            
            elif api_choice == 'BreachDirectory':
                try:
                    response = requests.post(
                        self.apis['BreachDirectory']['email_url'],
                        headers=self.apis['BreachDirectory']['headers'],
                        json={"query": email}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if data.get('found', False):
                            print(f"\n\033[91m[!] Email found in breaches (via BreachDirectory):\033[0m")
                            for result in data.get('results', []):
                                print(f"- {result.get('name', 'Unknown')}")
                                if 'password' in result:
                                    print(f"  Password hash exposed: {result['password'][:10]}...")
                            return True
                        else:
                            print("\n\033[92m[+] No breaches found for this email (BreachDirectory)\033[0m")
                            return False
                    elif response.status_code == 404:
                        print("\n\033[92m[+] No breaches found for this email (BreachDirectory)\033[0m")
                        return False
                    else:
                        print(f"\n\033[93m[?] BreachDirectory API Error: {response.status_code}\033[0m")
                        print(f"Response content: {response.text[:200]}...")  # Debug info
                        return None
                        
                except requests.exceptions.RequestException as e:
                    print(f"\n\033[93m[!] Connection error: {e}\033[0m")
                    return None
                
        except requests.exceptions.RequestException as e:
            print(f"\n\033[93m[!] Connection error: {e}\033[0m")
            return None
    
    def check_password_breach(self, password):
        """Check if a password has been exposed in data breaches (always uses free HIBP API)"""
        try:
            # Hash the password using SHA-1
            sha1_password = hashlib.sha1(password.encode('utf-8')).hexdigest().upper()
            prefix, suffix = sha1_password[:5], sha1_password[5:]
            
            # Make a k-anonymity request (this part is always free)
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
        print("3. Configure API settings")
        print("4. Exit")
        
        choice = input("\nSelect an option (1-4): ")
        
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
            print("\nAPI Configuration:")
            print("1. Enter Have I Been Pwned API key")
            print("2. Enter BreachDirectory API key")
            print("3. Back to main menu")
            
            config_choice = input("Select option (1-3): ")
            if config_choice == "1":
                key = input("Enter HIBP API key: ").strip()
                notifier.apis['HIBP']['headers']['hibp-api-key'] = key
                print("HIBP API key saved!")
            elif config_choice == "2":
                key = input("Enter BreachDirectory API key: ").strip()
                notifier.apis['BreachDirectory']['headers']['X-RapidAPI-Key'] = key
                print("BreachDirectory API key saved!")
            
        elif choice == "4":
            print("\nExiting... Stay safe online!")
            sys.exit(0)
            
        else:
            print("Invalid choice. Please select 1, 2, 3, or 4.")

if __name__ == "__main__":
    print("Note: This tool can use multiple breach databases:")
    print("1. Have I Been Pwned (requires API key)")
    print("2. BreachDirectory (free tier available via RapidAPI)")
    print("You can configure API keys from the main menu")
    main()
