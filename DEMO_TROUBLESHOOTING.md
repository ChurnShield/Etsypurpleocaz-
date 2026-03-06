# 🔧 Live Demo Troubleshooting Guide

## Quick Fixes for Common Issues

### Issue: Widget Won't Open
**Symptoms:** Clicking "Cancel" does nothing, no modal appears

**Solutions:**
1. **Check Console:** Open browser DevTools (F12) → Console tab
2. **CORS Error:** Enable "Allow development domains" in dashboard
3. **Token Invalid:** Verify token in `widget-test.html` matches your profile
4. **Network Error:** Check if Supabase URL is accessible

**Quick Test:**
```javascript
// In console, test basic connectivity
fetch('https://rdstyfaveeokocztayri.supabase.co/functions/v1/cancel-session/test')
  .then(r => console.log('Connection OK'))
  .catch(e => console.error('Connection failed:', e));
```

---

### Issue: "Session not found" Error
**Symptoms:** Widget opens but shows error message

**Solutions:**
1. **Invalid IDs:** Double-check customer and subscription IDs from Stripe
2. **Test Mode:** Ensure using Stripe test mode, not live mode
3. **Subscription Status:** Make sure subscription is active in Stripe
4. **Token Mismatch:** Verify the token matches the profile that owns the flow

---

### Issue: Offer Not Applied to Stripe
**Symptoms:** Customer accepts offer but Stripe doesn't update

**Solutions:**
1. **Subscription ID:** Must be in format `sub_xxxxxxxxx`
2. **Permissions:** Ensure Stripe API keys have write permissions
3. **Test Mode:** Confirm using test mode credentials
4. **Rate Limits:** Stripe test mode has limits - wait if hitting them

**Check Stripe:**
- Go to subscription details
- Look for "Discounts" or "Credits" section
- Verify the amount and duration

---

### Issue: Analytics Not Updating
**Symptoms:** Demo works but dashboard doesn't show new data

**Solutions:**
1. **Wait:** Analytics may have 30-second delay
2. **Refresh:** Hard refresh the analytics page
3. **Profile:** Ensure viewing the correct profile's analytics
4. **Test Data:** Test interactions may be filtered out

---

### Issue: Styling Looks Broken
**Symptoms:** Widget appears but CSS is messed up

**Solutions:**
1. **Dev Server:** Ensure `npm run dev` is running
2. **Cache:** Hard refresh (Ctrl+F5) the test page
3. **CORS:** CSS may be blocked - check network tab
4. **Branding:** Verify branding settings in dashboard

---

## Emergency Fallbacks

### Fallback 1: HTML Mockups
If live demo fails, use the static HTML files:
- `ChurnShield-Launch/screenshots/1-exit-survey.html`
- `ChurnShield-Launch/screenshots/2-discount-offer.html`

**Script:** "While we troubleshoot the live connection, let me show you the actual screens customers see..."

### Fallback 2: Pre-recorded Demo
Have a screen recording ready showing the full flow.

### Fallback 3: Simplified Demo
Use test mode parameters for offline demonstration:
```
http://localhost:5173/cancel/test-token?test=true&name=Demo&email=demo@test.com&plan=Pro&amount=49
```

---

## Pre-Demo Checklist

### 30 Minutes Before
- [ ] Start dev server: `npm run dev`
- [ ] Verify Stripe test customer exists
- [ ] Check widget token is correct
- [ ] Test widget opening manually
- [ ] Open Stripe dashboard in another tab
- [ ] Open analytics dashboard
- [ ] Clear browser cache

### 5 Minutes Before
- [ ] Test full flow end-to-end
- [ ] Verify internet connection
- [ ] Check microphone/audio
- [ ] Have fallback materials ready
- [ ] Close unnecessary browser tabs

### During Demo
- [ ] Keep browser console open (F12)
- [ ] Have Stripe dashboard ready
- [ ] Speak slowly and clearly
- [ ] Pause after each step
- [ ] Have backup explanations ready

---

## Common Error Messages & Fixes

| Error Message | Likely Cause | Quick Fix |
|---------------|--------------|-----------|
| "CORS error" | Dev domains not enabled | Enable in dashboard settings |
| "Invalid token" | Wrong profile token | Check token in widget config |
| "Customer not found" | Wrong customer ID | Verify in Stripe dashboard |
| "Subscription not found" | Wrong subscription ID | Verify in Stripe dashboard |
| "Network error" | Supabase down | Use fallback demo |
| "Stripe error" | API key issues | Check Stripe credentials |

---

## Recovery Phrases

**When something breaks:**
- "That's interesting - let me show you what normally happens..."
- "While we sort this out, let me demonstrate the concept..."
- "This actually shows how robust the error handling is..."

**Keep the demo moving forward!**