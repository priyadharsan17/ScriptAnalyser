# Configuration Folder

This folder contains configuration files for broker integrations.

## Quick Start

1. **Copy the example config:**
   ```powershell
   copy angel_config.example.json angel_config.json
   ```

2. **Edit with your actual credentials:**
   ```powershell
   notepad angel_config.json
   ```

3. **Fill in ALL fields including TOTP secret:**
   ```json
   {
     "api_key": "your_actual_api_key",
     "client_id": "your_actual_client_id",
     "password": "your_actual_password",
     "totp_secret": "YOUR_BASE32_TOTP_SECRET"
   }
   ```

## ⚠️ IMPORTANT: TOTP Secret Required

Angel One requires a **TOTP secret** (not the 6-digit code) for authentication.

- **What it is:** A base32 string like `JBSWY3DPEHPK3PXP` (16-32 characters)
- **Where to find it:** See [TOTP_SETUP.md](TOTP_SETUP.md) for detailed instructions
- **Why needed:** The app auto-generates TOTP codes for seamless authentication

**See [TOTP_SETUP.md](TOTP_SETUP.md) for complete TOTP setup guide!**

## Security

⚠️ **IMPORTANT:**
- `angel_config.json` is automatically excluded from git via `.gitignore`
- **Never commit actual credentials to version control**
- Only `*.example.json` files are tracked in git
- Keep your credentials secure and rotate them regularly

## Available Configs

- `angel_config.example.json` - Template for Angel One SmartAPI credentials
- `angel_config.json` - Your actual credentials (create this, not tracked in git)

## Getting Angel One Credentials

See [Documentation/AngelOne_SmartAPI_Setup.md](../Documentation/AngelOne_SmartAPI_Setup.md) for detailed setup instructions.
