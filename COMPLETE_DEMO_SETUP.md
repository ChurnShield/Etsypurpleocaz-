# 🚀 Complete Demo Setup Guide

## What I Can Handle vs What You Need to Do

### ✅ What I've Prepared For You:

1. **Complete Offline Demo** (`offline-demo.html`) - Interactive walkthrough
2. **Live Demo Setup Guide** (`LIVE_DEMO_SETUP.md`) - Step-by-step instructions
3. **Demo Script** (`LIVE_DEMO_SCRIPT.md`) - Professional presentation script
4. **Troubleshooting Guide** (`DEMO_TROUBLESHOOTING.md`) - Fix common issues
5. **Readiness Checker** (`demo-readiness-check.html`) - Pre-demo verification

### 🔧 What You Need to Do:

## Step 1: Install Node.js (If Not Already Installed)

**Download:** https://nodejs.org/ (LTS version recommended)

**Verify Installation:**
```bash
node --version  # Should show v18.x or higher
npm --version   # Should show 9.x or higher
```

## Step 2: Set Up the Development Environment

**Navigate to the project:**
```bash
cd "c:\Users\andyn\OneDrive\Desktop\NEW AI PROJECT\keep-them-happy"
```

**Install dependencies:**
```bash
npm install
```

**Start the development server:**
```bash
npm run dev
```

**Verify it's working:**
- Open http://localhost:5173 in your browser
- You should see the ChurnShield frontend

## Step 3: Set Up Stripe Test Data

**Create a Stripe account** (if you don't have one):
- Go to https://dashboard.stripe.com/
- Sign up for a free account

**Create test customer:**
1. Go to Customers → Create Customer
2. Email: `demo@churnshield.com`
3. Name: `Demo Customer`

**Create test subscription:**
1. Go to Products → Create Product
2. Name: "ChurnShield Pro" - $49/month
3. Go to Subscriptions → Create Subscription
4. Select the demo customer and product

**Get the IDs:**
- Customer ID: `cus_xxx...` (from customer details)
- Subscription ID: `sub_xxx...` (from subscription details)

## Step 4: Configure the Widget

**Open the test page:**
- Go to http://localhost:5173/widget-test.html

**Update the configuration:**
- Replace `cus_YOUR_TEST_CUSTOMER_ID` with your test customer ID
- Replace `sub_YOUR_TEST_SUBSCRIPTION_ID` with your test subscription ID

## Step 5: Enable Development Domains

**In ChurnShield Dashboard:**
1. Go to your ChurnShield dashboard
2. Navigate to Cancel Flow Builder
3. Go to Embed Widget tab
4. Check "Allow development domains"
5. Add `localhost:5173` to allowed domains

## Step 6: Run the Readiness Check

**Open the readiness checker:**
- Open `demo-readiness-check.html` in your browser
- Click each "Check" button
- Fix any issues that come up

## Step 7: Practice the Demo

**Use the offline demo first:**
- Open `offline-demo.html` in your browser
- Click through each step to practice your presentation

**Then try the live demo:**
- Open http://localhost:5173/widget-test.html
- Click "Cancel My Subscription"
- Practice the full flow

## Step 8: Run the Live Demo

**Follow the script:**
- Open `LIVE_DEMO_SCRIPT.md`
- Follow the timing and narration
- Use the troubleshooting guide if issues arise

---

## 🎯 Demo Flow Summary

1. **Customer clicks cancel** → Widget opens
2. **Exit survey appears** → Customer selects reason
3. **Personalized offer shown** → Based on their reason
4. **Customer accepts/declines** → Stripe integration happens
5. **Analytics updated** → Show the save in dashboard

---

## 🔧 Quick Troubleshooting

### If widget doesn't open:
- Check "Allow development domains" is enabled
- Verify token in widget config
- Check browser console for errors

### If Stripe doesn't update:
- Use test mode credentials
- Verify customer/subscription IDs
- Check Stripe dashboard permissions

### If server won't start:
- Make sure port 5173 is free
- Try `npm run dev -- --port 3000`
- Check for Node.js version conflicts

---

## 📞 If You Get Stuck

The offline demo (`offline-demo.html`) works without any setup and shows the complete flow. Use it as a backup if the live demo has issues.

**Remember:** The live demo connects to real Stripe and Supabase, so it shows actual functionality. The offline demo is for practice and fallbacks.

---

## 🎬 Final Demo Checklist

- [ ] Node.js installed and working
- [ ] Development server running (`npm run dev`)
- [ ] Stripe test customer and subscription created
- [ ] Widget configuration updated with real IDs
- [ ] Development domains enabled
- [ ] Readiness check passes all tests
- [ ] Offline demo practiced
- [ ] Live demo tested end-to-end
- [ ] Backup materials ready
- [ ] Internet connection stable

**You're all set! 🚀**