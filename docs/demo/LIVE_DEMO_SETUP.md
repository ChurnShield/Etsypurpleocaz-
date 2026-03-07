# 🚀 Live Demo Setup: ChurnShield Cancel Flow Widget

## Prerequisites

### 1. Node.js & npm
```bash
# Check if installed
node --version
npm --version

# If not installed, download from https://nodejs.org/
```

### 2. Stripe Test Account
- Sign up at [Stripe Dashboard](https://dashboard.stripe.com/)
- Create test customers and subscriptions for demo

---

## Step 1: Set Up the Development Environment

### Install Dependencies
```bash
cd keep-them-happy
npm install
```

### Start the Development Server
```bash
npm run dev
```

This will start the frontend at `http://localhost:5173`

---

## Step 2: Prepare Test Data in Stripe

### Create a Test Customer
1. Go to [Stripe Dashboard → Customers](https://dashboard.stripe.com/customers)
2. Click "Create customer"
3. Fill in:
   - **Email:** `demo@churnshield.com`
   - **Name:** `Demo Customer`
   - **Description:** `ChurnShield Demo User`

### Create a Test Subscription
1. Go to [Stripe Dashboard → Products](https://dashboard.stripe.com/products)
2. Create a product: "ChurnShield Pro" - $49/month
3. Go to [Subscriptions](https://dashboard.stripe.com/subscriptions)
4. Click "Create subscription"
5. Select the demo customer and product

### Get the IDs
- **Customer ID:** `cus_xxx...` (from customer details)
- **Subscription ID:** `sub_xxx...` (from subscription details)

---

## Step 3: Configure the Widget

### Open the Test Page
Navigate to: `http://localhost:5173/widget-test.html`

### Update the Configuration
In the test page, update these values:

```javascript
ChurnShield.init({
  token: '43a3cad2-42a6-4a79-9391-ae03a293bcb4', // Your profile token
  customerId: 'cus_xxx...',    // From Stripe
  subscriptionId: 'sub_xxx...', // From Stripe
  onSave: function() {
    console.log('Customer saved!');
  },
  onCancel: function() {
    console.log('Customer cancelled');
  }
});
```

---

## Step 4: Enable Development Domains

### In ChurnShield Dashboard
1. Go to your ChurnShield dashboard
2. Navigate to **Cancel Flow Builder**
3. Go to **Embed Widget** tab
4. Check **"Allow development domains"**
5. Add `localhost:5173` to allowed domains

---

## Step 5: Run the Live Demo

### Demo Flow Script

**Narrator:** "Let's see the cancel flow widget in action with real Stripe integration!"

#### Step 1: Show the Setup
- Open `http://localhost:5173/widget-test.html`
- Show the customer and subscription IDs
- Click "Cancel My Subscription"

#### Step 2: Exit Survey
- Widget opens with survey
- Select a reason (e.g., "It's too expensive")
- Add optional feedback
- Click "Continue"

#### Step 3: Personalized Offer
- Widget shows tailored offer (discount/pause)
- Show the offer details
- **Accept the offer** to see save flow
- **Decline** to see cancel flow

#### Step 4: Stripe Integration
- If accepted: Check Stripe dashboard - discount applied automatically
- If cancelled: Subscription cancelled in Stripe

#### Step 5: Analytics
- Show the save/cancel recorded in ChurnShield analytics

---

## Demo Scenarios

### Scenario 1: Successful Save (Happy Path)
1. Select "It's too expensive" → Gets discount offer
2. Accept offer → Customer saved, discount applied to Stripe

### Scenario 2: Cancellation (Sad Path)
1. Select "Found a better alternative" → May get pause offer
2. Decline offer → Subscription cancelled

### Scenario 3: Custom Feedback
1. Select "Other reason" → Add custom feedback
2. Shows how feedback is captured for analysis

---

## Troubleshooting

### Widget Won't Open
- ✅ Check "Allow development domains" is enabled
- ✅ Verify token is correct
- ✅ Check browser console for errors

### Stripe Errors
- ✅ Use test mode Stripe keys
- ✅ Verify customer/subscription IDs are correct
- ✅ Check Stripe dashboard for test data

### Network Errors
- ✅ Ensure Supabase URL is accessible
- ✅ Check browser CORS settings
- ✅ Verify Edge Functions are deployed

---

## Advanced Demo Features

### Test Mode Parameters
Add URL parameters for enhanced testing:
```
http://localhost:5173/cancel/:token?test=true&name=Demo&email=demo@test.com&plan=Pro&amount=49
```

### Multiple Scenarios
- Create multiple test customers with different subscription states
- Demo different offer types (discount vs pause)
- Show analytics updating in real-time

### Integration Demo
- Show the widget embedded in a real SaaS app
- Demonstrate the full customer journey
- Highlight the seamless Stripe integration

---

## Demo Checklist

- [ ] Development server running (`npm run dev`)
- [ ] Stripe test customer and subscription created
- [ ] Widget configuration updated with real IDs
- [ ] Development domains enabled in dashboard
- [ ] Browser console open for debugging
- [ ] Stripe dashboard ready to show changes
- [ ] Analytics dashboard ready to show metrics

**Ready to demo! 🚀**