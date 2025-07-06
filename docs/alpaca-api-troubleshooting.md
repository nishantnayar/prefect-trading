# Alpaca API 403 Forbidden Error - Troubleshooting Guide

## Issue Summary

You're experiencing 403 Forbidden errors when trying to access Alpaca API endpoints. This indicates that your API credentials are not being accepted by Alpaca's servers.

## Root Cause

The 403 Forbidden error typically occurs when:
- API keys have been revoked or expired
- Secret key is incorrect
- Account is not properly activated
- Account has trading restrictions
- API keys don't have the right permissions

## Diagnosis Results

✅ **API Key Format**: Correct (starts with "PK" for paper trading)  
❌ **Authentication**: Failing on all endpoints (account, orders, data)  
🔍 **Error Type**: 403 Forbidden across all Alpaca services  

## Solution Steps

### 1. Regenerate API Keys

1. **Log into Alpaca Dashboard**
   - Visit: https://app.alpaca.markets/
   - Sign in to your paper trading account

2. **Navigate to API Keys**
   - Go to Account → API Keys
   - Or directly visit: https://app.alpaca.markets/account/api-keys

3. **Regenerate Keys**
   - Click "Regenerate" or "Create New Key"
   - **Important**: Copy both the API Key and Secret Key immediately
   - You will only see the Secret Key once!

4. **Verify Key Format**
   - Paper trading API keys should start with "PK"
   - Live trading API keys start with "AK"

### 2. Update Your Credentials

#### Option A: Use the Update Script (Recommended)
```bash
python scripts/update_alpaca_credentials.py
```

This script will:
- Prompt you for new API keys
- Test the credentials
- Update your `.env` file
- Update Prefect secrets
- Provide validation

#### Option B: Manual Update

1. **Update Environment Variables**
   - Create or update `config/.env` file
   - Set your new credentials:
   ```env
   ALPACA_API_KEY=your_new_api_key_here
   ALPACA_SECRET_KEY=your_new_secret_key_here
   ```

2. **Update Prefect Secrets**
   ```bash
   python scripts/setup_alpaca_secrets.py
   ```

### 3. Test the Connection

After updating credentials, test the connection:

```bash
python scripts/test_alpaca_credentials.py
```

You should see:
```
✅ Account info retrieved successfully!
✅ Market data retrieved successfully!
✅ Orders endpoint working!
🎉 All tests passed!
```

### 4. Restart Your Application

After updating credentials:
1. Stop your current application
2. Clear any cached data
3. Restart the application

## Prevention

To avoid this issue in the future:

1. **Keep API Keys Secure**
   - Don't share API keys in code repositories
   - Use environment variables or secure secret management
   - Regularly rotate API keys

2. **Monitor Account Status**
   - Check your Alpaca account status regularly
   - Ensure your account is active and not restricted
   - Keep your account information up to date

3. **Use Paper Trading for Development**
   - Always test with paper trading keys first
   - Only use live trading keys when ready for production

## Error Handling Improvements

The portfolio manager has been updated with better error handling:

- **Clear Error Messages**: Specific guidance for different error types
- **Authentication Detection**: Automatic detection of 403/401 errors
- **Helpful Instructions**: Direct links to Alpaca dashboard
- **Graceful Degradation**: Returns empty data instead of crashing

## Common Issues and Solutions

### Issue: "API key format is unexpected"
**Solution**: Ensure you're using paper trading keys (start with "PK")

### Issue: "Account not found"
**Solution**: Verify you're using the correct account type (paper vs live)

### Issue: "Trading blocked"
**Solution**: Check your account status in the Alpaca dashboard

### Issue: "Rate limit exceeded"
**Solution**: Wait before making more requests, implement rate limiting

## Support Resources

- **Alpaca Documentation**: https://alpaca.markets/docs/
- **Alpaca Support**: https://alpaca.markets/support/
- **API Status**: https://status.alpaca.markets/
- **Community Forum**: https://forum.alpaca.markets/

## Scripts Created

1. **`scripts/test_alpaca_credentials.py`** - Test API connection
2. **`scripts/diagnose_alpaca_issue.py`** - Detailed diagnosis
3. **`scripts/update_alpaca_credentials.py`** - Update credentials
4. **Enhanced error handling** in `portfolio_manager.py`

## Next Steps

1. ✅ **Immediate**: Regenerate API keys in Alpaca dashboard
2. ✅ **Update**: Run the update script with new credentials
3. ✅ **Test**: Verify connection works
4. ✅ **Restart**: Restart your application
5. ✅ **Monitor**: Watch for any remaining issues

Your trading system should work properly once you complete these steps! 