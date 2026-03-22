# TOTP Secret Setup for Angel One

## What is TOTP Secret?

The TOTP (Time-based One-Time Password) secret is a **base32-encoded string** (typically 16-32 characters) that your authenticator app uses to generate 6-digit codes.

## ⚠️ Important

- **TOTP Secret** ≠ **TOTP Code**
- The **secret** is the base32 string (e.g., `JBSWY3DPEHPK3PXP`)
- The **code** is the 6-digit number (e.g., `123456`)

You need the **SECRET**, not the code!

## How to Get Your TOTP Secret

### Method 1: During 2FA Setup (Easiest)

When you first enable 2FA on Angel One:

1. **Look for the manual entry option** or "Can't scan QR code?"
2. You'll see a **base32 string** like: `JBSWY3DPEHPK3PXP`
3. **Save this string** - this is your TOTP secret
4. Add it to `config/angel_config.json`

### Method 2: From QR Code

If you already set up 2FA with a QR code:

1. **Scan the QR code again** using a QR reader (not authenticator app)
2. The QR contains a URL like:
   ```
   otpauth://totp/AngelOne:your_client_id?secret=JBSWY3DPEHPK3PXP&issuer=AngelOne
   ```
3. The **secret** parameter is your TOTP secret
4. Copy just the secret value (e.g., `JBSWY3DPEHPK3PXP`)

### Method 3: From Authenticator App

Some authenticator apps let you export/view the secret:

**Google Authenticator:**
- No built-in export (use Method 1 or 2)

**Authy:**
- Settings → Authenticator Accounts → View account details

**Microsoft Authenticator:**
- No built-in export (use Method 1 or 2)

**2FAS, Aegis, andOTP:**
- Usually have export/backup features that show the secret

### Method 4: Reset 2FA (Last Resort)

If you can't find your secret:

1. Log in to Angel One web platform
2. Go to Settings → Security
3. **Disable 2FA**
4. **Re-enable 2FA** and follow Method 1 above
5. Save the secret this time!

## Configuration

Once you have your TOTP secret, add it to `config/angel_config.json`:

```json
{
  "api_key": "your_api_key",
  "client_id": "your_client_id",
  "password": "your_password",
  "totp_secret": "JBSWY3DPEHPK3PXP"
}
```

## How It Works

The application uses the `pyotp` library to:

1. Read your TOTP secret from config
2. Generate the current 6-digit code automatically
3. Use it for authentication with Angel One
4. Codes refresh every 30 seconds

**You never need to manually enter the 6-digit codes!**

## Testing

To verify your TOTP secret works:

```powershell
.\.venv\Scripts\python.exe -c "import pyotp; print(pyotp.TOTP('YOUR_SECRET_HERE').now())"
```

This should print a 6-digit number that matches your authenticator app.

## Security

⚠️ **Keep your TOTP secret secure!**

- Never commit `angel_config.json` to git (already in `.gitignore`)
- Don't share the secret with anyone
- The secret is equivalent to your 2FA access
- If compromised, reset your 2FA immediately

## Common Issues

### "Invalid TOTP" Error

If you see this error:

1. **Check the secret format**: Must be base32 (A-Z, 2-7)
2. **No spaces**: Remove any spaces from the secret
3. **Correct length**: Usually 16 or 32 characters
4. **Time sync**: Ensure your system clock is accurate

### "No TOTP secret provided"

Your config has a placeholder like:
- `"optional_totp_secret"`
- `"YOUR_TOTP_SECRET_HERE"`
- `""`
- `null`

Replace it with your actual TOTP secret!

## Example

**Bad (won't work):**
```json
{
  "totp_secret": "123456"  // ❌ This is a TOTP code, not secret
}
```

**Good (will work):**
```json
{
  "totp_secret": "JBSWY3DPEHPK3PXP"  // ✅ Base32 secret
}
```

---

**Need help?** See [AngelOne_SmartAPI_Setup.md](../Documentation/AngelOne_SmartAPI_Setup.md) for complete setup guide.
