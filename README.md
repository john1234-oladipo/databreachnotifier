# Data Breach Notifier
![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Python tool that checks if your email address or password has been compromised in known data breaches using the Have I Been Pwned API.

## Features

- ✅ Check email addresses against known breaches
- 🔒 Securely check passwords (using k-anonymity)
- 📋 View breach details (dates, data types)
- 🔔 Get security recommendations

## Prerequisites

- Python 3.6+
- `requests` library
- [Have I Been Pwned API key](https://haveibeenpwned.com/API/Key) (free)

## Installation

```bash
git clone https://github.com/yourusername/data-breach-notifier.git
cd data-breach-notifier
pip install requests
```

## Configuration

1. Get your API key from [Have I Been Pwned](https://haveibeenpwned.com/API/Key)
2. Add it to `breach_notifier.py`:

```python
self.headers = {
    "User-Agent": "DataBreachNotifier/1.0",
    "hibp-api-key": "your-api-key-here"  # ← Add your key here
}
```

## Usage

```bash
python breach_notifier.py
```

Menu Options:
1. Check email address
2. Check password
3. Exit

## Example Output

![Example Screenshot](https://via.placeholder.com/600x400?text=Example+Output+Screenshot)

## Security

- 🔐 Only password hash prefixes are transmitted
- 📧 No data is stored locally
- ⚠️ Always change breached passwords immediately

## Contributing

Pull requests are welcome. For major changes, please open an issue first.

## License

[MIT](LICENSE)

