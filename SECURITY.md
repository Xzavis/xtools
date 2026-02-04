# Security Features

## HF Token Protection

### 1. Encryption at Rest
- Token dienkripsi menggunakan AES-256 via Fernet
- Key derived dari machine-specific ID menggunakan PBKDF2 (480k iterations)
- Token tidak pernah disimpan dalam plaintext

### 2. Environment Variable Priority
1. **Environment Variable** (`HF_TOKEN` atau `HUGGINGFACE_TOKEN`) - Paling aman
2. **Encrypted File Storage** - Fallback jika env var tidak tersedia

### 3. Rate Limiting & Lockout
- Max 5 percobaan gagal berturut-turut
- Lockout 5 menit setelah max attempts tercapai
- Counter reset setelah lockout period selesai

### 4. Audit Logging
- Semua akses token di-log ke `.xtools_audit.log`
- Tidak menyimpan token plaintext di log
- Hanya menyimpan hash prefix untuk identifikasi

### 5. Token Validation
- Validasi format: harus dimulai dengan `hf_`
- Minimum length: 20 karakter
- Verifikasi integrity dengan SHA-256 hash

### 6. Secure File Permissions
File yang mengandung data sensitif:
```
.xtools_secure.json      # Encrypted settings
.xtools_lockout.json     # Lockout status
.xtools_audit.log        # Audit trail
```

### 7. Session Security
- Flask secret key untuk session encryption
- CSRF protection via SameSite cookies

## Best Practices

### Production Deployment
```bash
# Set token via environment variable (recommended)
export HF_TOKEN=hf_your_token_here

# Atau buat .env file (jangan commit!)
echo "HF_TOKEN=hf_your_token_here" > .env
```

### Token Rotation
- Rotasi token secara berkala (30-90 hari)
- Revoke token lama segera setelah rotasi
- Monitor audit log untuk akses mencurigakan

### File Permissions
```bash
# Set restrictive permissions
chmod 600 .xtools_secure.json
chmod 600 .xtools_lockout.json
chmod 600 .xtools_audit.log
```

## API Security Endpoints

### Check Security Status
```bash
GET /api/security/status
```

### View Audit Log
```bash
GET /api/security/audit-log
```

### Clear Lockout
```bash
POST /api/security/clear-lockout
```

## Incident Response

Jika token terekspos:
1. Segera revoke token di https://huggingface.co/settings/tokens
2. Clear lockout: `POST /api/security/clear-lockout`
3. Generate token baru
4. Review audit log untuk akses mencurigakan
5. Update token di environment variable
