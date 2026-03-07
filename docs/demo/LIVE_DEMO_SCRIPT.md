# 🎤 Live Demo Script: ChurnShield Cancel Flow Widget

## Opening (30 seconds)

**You:** "Today I'm going to show you how ChurnShield turns customer cancellations into revenue-saving opportunities. We'll see the cancel flow widget in action with real Stripe integration."

*[Open browser to http://localhost:5173/widget-test.html]*

**You:** "Here's our test page. In a real app, this would be triggered when a customer clicks 'Cancel Subscription'."

---

## Setup Explanation (45 seconds)

**You:** "First, let's configure the widget with a real Stripe customer and subscription."

*[Point to the form fields]*

**You:** "We need:
- Customer ID from Stripe
- Subscription ID from Stripe
- Our ChurnShield profile token

This connects the widget to both our retention logic and Stripe's billing system."

*[Click the 'Cancel My Subscription' button]*

---

## Exit Survey Demo (1 minute)

**You:** "When the customer tries to cancel, instead of immediately losing them, we show a friendly survey."

*[Widget opens with survey]*

**You:** "This intelligence is crucial - different cancel reasons get different retention strategies. Let's select 'It's too expensive' and see what happens."

*[Select reason, add feedback, click Continue]*

---

## Personalized Offer Demo (1 minute)

**You:** "Based on the reason, ChurnShield presents a personalized offer. For price concerns, we offer a discount."

*[Show the discount offer]*

**You:** "The offer is automatically calculated and can be discounts, pauses, or custom deals. Let's accept this offer to see the save flow."

*[Click 'Accept Offer']*

---

## Stripe Integration Demo (1 minute)

**You:** "When the customer accepts, the widget communicates with Stripe to apply the discount automatically."

*[Show completion screen]*

**You:** "Let me check the Stripe dashboard to confirm the discount was applied."

*[Switch to Stripe dashboard, show the subscription with discount applied]*

**You:** "There it is! The discount is now active on their subscription. The customer is saved and continues paying."

---

## Analytics Demo (45 seconds)

**You:** "Every interaction is tracked in real-time analytics."

*[Show ChurnShield analytics dashboard]*

**You:** "We can see the save rate, revenue recovered, and get insights to optimize our retention strategies."

---

## Alternative Scenario (1 minute)

**You:** "Let's try a different scenario. What if the customer declines the offer?"

*[Reset and try again with different reason]*

**You:** "If they decline, we respect their decision and cancel the subscription cleanly."

*[Show cancellation flow]*

**You:** "But importantly, we captured their feedback for future analysis."

---

## Closing (30 seconds)

**You:** "That's ChurnShield in action - turning potential cancellations into saves with intelligent, automated retention offers.

Key benefits:
- ✅ Personalized offers based on cancel reasons
- ✅ Automatic Stripe integration
- ✅ Real-time analytics and optimization
- ✅ No development work required

Ready to stop losing customers and start saving them?"

---

## Timing Breakdown
- **Setup:** 45 seconds
- **Survey:** 1 minute
- **Offer:** 1 minute
- **Integration:** 1 minute
- **Analytics:** 45 seconds
- **Alternative:** 1 minute
- **Total:** ~5.5 minutes

## Backup Plans
- **If Stripe fails:** Use test mode parameters for offline demo
- **If widget doesn't load:** Show the HTML mockups as fallback
- **If network issues:** Demonstrate with pre-recorded flow

## Key Demo Tips
- Speak confidently and explain what's happening
- Pause after each step for audience to absorb
- Highlight the automation aspect ("no manual work!")
- Show real Stripe dashboard changes
- End with clear next steps for the audience