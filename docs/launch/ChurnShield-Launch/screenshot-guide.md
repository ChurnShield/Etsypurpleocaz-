# 📸 ChurnShield Screenshot Guide - Step by Step

## Why Screenshots Matter

Product Hunt users make snap judgments in 3-5 seconds. Your screenshots need to:
- Show the product clearly (no clutter)
- Tell a story (problem → solution)
- Look professional (clean UI, good data)
- Highlight key benefits (not just features)

**Good screenshots = 2-3x higher click-through rate**

---

## Screenshot Specifications

**Technical Requirements:**
- Format: PNG (not JPG - clearer quality)
- Minimum resolution: 1280x720px
- Maximum file size: 5MB each
- Aspect ratio: 16:9 preferred

**Design Requirements:**
- Clean browser (no bookmarks bar, extensions, clutter)
- Use incognito/private mode
- Hide your personal info (name, email if visible)
- Use good demo data (make numbers look impressive)
- Consistent browser zoom level (100%)

---

## Screenshot 1: Exit Survey (HERO IMAGE - Most Important!)

### What to Show
Customer viewing the exit survey when they click "Cancel Subscription"

### Where to Capture
Navigate to: `https://churnshield.app/cancel/:token` (your cancel widget)

### How to Set Up the Shot

**Step 1: Clean Your Browser**
```
1. Open Chrome/Firefox in Incognito mode
2. Navigate to your cancel widget demo
3. Zoom to 100% (Ctrl+0 / Cmd+0)
4. Hide bookmarks bar (Ctrl+Shift+B / Cmd+Shift+B)
5. Make window full screen (F11)
```

**Step 2: Perfect the View**
- Center the survey in the viewport
- Show company branding at top
- Display all survey options clearly:
  - "It's too expensive"
  - "I'm not using it enough"
  - "Missing features I need"
  - "Found a better alternative"
  - "Other reason"
- Button should say "Continue" or "Next"

**Step 3: Add Visual Interest**
- If possible, show cursor hovering over one option (shows interactivity)
- Make sure progress indicator is visible if you have one
- Include any trust indicators (lock icon, privacy text)

**Step 4: Capture**
- Press F12 to open DevTools
- Click the device toolbar icon (mobile/tablet view)
- Select "Responsive" and set to 1280x720
- Take screenshot: Ctrl+Shift+P → type "Capture screenshot"
- Or use built-in screenshot tool (Shift+Cmd+4 on Mac, Windows+Shift+S on Windows)

### Caption for Product Hunt
```
Smart exit surveys learn why customers are leaving - and show personalized offers based on their answer
```

### Annotations to Add (Optional but Powerful)
Use tool like Figma, Photoshop, or Canva to add:
- Arrow pointing to survey with text: "Customer sees this instead of instant cancellation"
- Highlight box around options with text: "Personalized offers based on answer"

---

## Screenshot 2: Personalized Retention Offer

### What to Show
The offer screen after customer selects a reason (e.g., "Too expensive")

### Where to Capture
Continue in cancel flow → After selecting "Too expensive" → Shows discount offer

### How to Set Up the Shot

**Perfect Offer Example:**
```
Headline: "We understand price is a concern"
Subtext: "We'd love to keep you as a customer. Here's a special offer:"

Offer Card:
"Stay for 40% off"
"For the next 3 months"
"$30/month → $18/month"

[Accept Offer] [No Thanks, Cancel]
```

**What Makes This Shot Powerful:**
- Shows empathy ("We understand...")
- Clear value (40% off, specific numbers)
- Low-pressure choice (two clear buttons)
- Time-limited (3 months)

### Capture Tips
- Show the full offer card prominently
- Include pricing comparison ($30 → $18)
- Make sure CTA buttons are visible
- Add any countdown timer if you have one

### Caption for Product Hunt
```
Personalized retention offers shown based on cancellation reason - in this case, a discount for price-sensitive customers
```

---

## Screenshot 3: Analytics Dashboard

### What to Show
Main dashboard with impressive (but realistic) metrics

### Where to Capture
Navigate to: `/dashboard`

### How to Set Up the Shot

**Key Metrics to Display:**

**Top Cards (Big Numbers):**
- Total Saves: **47** (or whatever looks good)
- Revenue Retained: **£1,840** (accumulated)
- Save Rate: **35%** (20-40% is realistic)
- Active Flows: **3**

**Charts to Show:**
- Line graph: "Save Rate Over Time" (trending up is good!)
- Bar chart: "Cancellation Reasons" (shows which reasons are most common)
- Pie chart: "Offer Performance" (which offers convert best)

**Recent Activity Feed:**
- "Customer saved - Accepted 40% discount - £30 retained"
- "Customer saved - Accepted pause option - £50 retained"
- "Exit survey completed - Reason: Missing features"

### Making It Look Professional

**Use Good Demo Data:**
```sql
-- If you can populate demo data, use these realistic numbers:
- 47 total saves out of 134 cancellation attempts = 35% save rate
- Revenue retained: £1,840 total
- Average save value: £39
- Most common reason: "Too expensive" (40%)
- Best performing offer: 40% discount (45% acceptance rate)
```

**Visual Polish:**
- Consistent color scheme (primary color for positive metrics)
- Clean spacing (not cramped)
- Readable fonts (zoom to make text crisp)
- Show date range selector: "Last 30 days"

### Capture Tips
- Zoom out slightly if needed to fit more info (90% zoom okay)
- Include header/navigation to show it's a real dashboard
- Make sure charts are readable
- Hide any personal customer data

### Caption for Product Hunt
```
Real-time analytics dashboard - track saves, revenue retained, cancellation reasons, and offer performance
```

---

## Screenshot 4: Cancel Flow Builder (No-Code Setup)

### What to Show
The interface where users build their cancellation flow

### Where to Capture
Navigate to: `/cancel-flow` or `/cancel-flow-builder`

### How to Set Up the Shot

**If You Have Visual Flow Builder:**
- Show boxes/cards connected with arrows
- Each box represents a step:
  1. "Exit Survey"
  2. "Show Offer (If Price)"
  3. "Show Offer (If Not Using)"
  4. "Thank You / Feedback"
- Include "Add Step" button or drag-and-drop indicator

**If You Have Form-Based Builder:**
- Show the configuration form with sections:
  - Survey Questions (toggles for each question)
  - Offer Settings (discount percentage, duration)
  - Email Notifications (who gets notified)
  - Branding (logo, colors)
- Make sure it looks easy to fill out

**Key Elements to Show:**
- "Preview" button (shows you can test before launching)
- "Save" or "Publish" button
- Toggle switches (visual, easy to understand)
- Rich text editor for custom messages

### Capture Tips
- Show a partially completed flow (demonstrates ease of use)
- Include helpful tooltips or guidance text if visible
- Make sure "No code required" is evident from the UI

### Caption for Product Hunt
```
Build custom cancellation flows in 10 minutes - no code or developer required
```

---

## Screenshot 5: Stripe Integration

### What to Show
Connected Stripe account OR the connection screen

### Where to Capture
Navigate to: `/connect-stripe` or `/settings` (integrations section)

### Option A: Connection Screen (Before Connected)

**Show:**
- Big "Connect with Stripe" button (official Stripe button styling)
- Security indicators: "Secure OAuth connection", "We never see your credentials"
- Benefits list:
  - "Sync subscribers automatically"
  - "Cancel/modify subscriptions"
  - "Track revenue retained"
- Time estimate: "Takes 30 seconds"

### Option B: Connected State (After Connected)

**Show:**
- ✓ "Connected" status with green checkmark
- Stripe account info: "account_name@business.com"
- Account ID: "acct_xxx" (hide sensitive parts)
- Connected date: "Connected on Jan 15, 2026"
- "Disconnect" button (shows it's reversible)
- Sync status: "Last synced: 2 minutes ago"

### Capture Tips
- Show trust indicators (lock icon, "Powered by Stripe")
- Make the connection process look EASY (one click)
- If possible, show both before and after in one split-screen image

### Caption for Product Hunt
```
Connect your Stripe account in 30 seconds with secure OAuth - no API keys, no developer needed
```

---

## Bonus Screenshots (If You Have Time)

### Screenshot 6: Churn Risk Analysis

**Where:** `/churn-risk` or `/dashboard/at-risk`

**Show:**
- List of at-risk customers with risk scores
- Factors: "Low usage", "Payment failed", "Downgraded recently"
- Action buttons: "Send offer", "Contact"

**Caption:** "Identify at-risk customers before they cancel - proactive retention"

---

### Screenshot 7: Recovery Inbox (Team Collaboration)

**Where:** `/recovery`

**Show:**
- Inbox-style interface with cancellation cases
- Status tags: "In Progress", "Saved", "Lost", "Awaiting Response"
- Team member assignments
- Notes/comments thread

**Caption:** "Team inbox for managing edge cases - collaborate on complex cancellations"

---

### Screenshot 8: Mobile View

**What:** Cancel widget on mobile device

**Show:**
- Exit survey on mobile (iPhone mockup)
- Responsive design
- Touch-friendly buttons

**Caption:** "Fully responsive - works perfectly on mobile where 60%+ of cancellations happen"

---

## Screenshot Creation Workflow

### Step-by-Step Process

**Day 1: Setup (30 minutes)**
1. [ ] Populate demo data in your database
   - Create 50+ dummy saves with realistic data
   - Vary cancellation reasons (40% price, 30% not using, 20% missing features, 10% other)
   - Set date range to last 30 days
2. [ ] Test all pages in incognito mode
3. [ ] Verify demo token works for cancel widget

**Day 2: Capture (1-2 hours)**
1. [ ] Screenshot 1: Exit Survey (15 min)
2. [ ] Screenshot 2: Offer Screen (15 min)
3. [ ] Screenshot 3: Dashboard (20 min)
4. [ ] Screenshot 4: Flow Builder (20 min)
5. [ ] Screenshot 5: Stripe Connection (15 min)
6. [ ] Bonus screenshots if time allows (30 min)

**Day 3: Edit & Enhance (1 hour)**
1. [ ] Crop all screenshots to 16:9 aspect ratio
2. [ ] Add annotations/arrows (optional but helpful)
3. [ ] Add device frames (use https://deviceframes.com)
4. [ ] Ensure consistent styling across all shots
5. [ ] Export as PNG, optimize file size if >5MB

---

## Tools for Screenshot Editing

### Free Tools

**Annotation/Arrows:**
- **Canva** (canva.com) - Easy drag-and-drop
- **Figma** (figma.com) - Professional design tool
- **Markup** (Mac built-in) - Simple annotations

**Device Frames:**
- **Screely** (screely.com) - Add browser frames
- **Device Frames** (deviceframes.com) - Add laptop/phone frames

**Optimization:**
- **TinyPNG** (tinypng.com) - Compress PNG files
- **Squoosh** (squoosh.app) - Image optimization

### Paid Tools (If You Want Pro Results)

- **CleanShot X** ($29, Mac) - Best screenshot tool for Mac
- **Snagit** ($63) - Professional screenshot + editing
- **Photoshop** ($10/mo) - Full control

---

## Screenshot Quality Checklist

Before uploading to Product Hunt, verify each screenshot:

### Technical Quality
- [ ] Resolution 1280x720px minimum
- [ ] PNG format (not JPG)
- [ ] File size under 5MB
- [ ] 16:9 aspect ratio
- [ ] No blur or pixelation

### Content Quality
- [ ] UI is clearly visible (no tiny text)
- [ ] Demo data looks realistic (not 0s everywhere)
- [ ] No personal/sensitive information visible
- [ ] Browser chrome is clean (no clutter)
- [ ] Colors are accurate (not washed out)

### Storytelling
- [ ] Each screenshot shows a distinct feature
- [ ] Sequence tells a story (survey → offer → dashboard → setup)
- [ ] Benefits are clear (not just features)
- [ ] Captions are descriptive but concise

---

## Demo GIF/Video Tips

### 30-Second Demo Script

**Recommended Flow:**
1. **[0-5s]** Show customer dashboard → click "Manage Subscription"
2. **[5-10s]** Click "Cancel Subscription" → redirected to ChurnShield survey
3. **[10-15s]** Select "Too expensive" → submitted
4. **[15-20s]** Offer appears: "Stay for 40% off for 3 months"
5. **[20-23s]** Click "Accept Offer" → success animation
6. **[23-27s]** Dashboard updates: +1 save, +£30 revenue retained
7. **[27-30s]** Final frame: "Save 20-40% of cancellations. Setup in 10 min."

### Recording Tips

**Technical Setup:**
- Use Loom (loom.com) - Free, easy, no watermark on short videos
- Record at 1920x1080 resolution
- Use incognito mode (clean browser)
- Disable notifications (Do Not Disturb mode)
- Close all other apps (avoid lag)

**Recording Best Practices:**
- Slow, deliberate mouse movements (no jitter)
- Pause 1 second on each screen (let viewers see it)
- No talking necessary (let the product speak)
- Add text captions if possible ("Customer clicks cancel..." etc.)
- End with strong CTA ("Try it free at churnshield.app")

**Tools:**
- **Loom** (Free) - Best for quick demos
- **ScreenToGif** (Free, Windows) - Create GIFs directly
- **CloudApp** (Free tier) - Screen recording with editing
- **iMovie/Camtasia** - If you want to edit professionally

---

## Example Screenshot Sequence (Storytelling)

**The Story Your Screenshots Should Tell:**

1. **Problem:** "Customers click cancel and... nothing. They're gone." (Exit survey screenshot)
2. **Solution:** "ChurnShield asks why and shows personalized offers." (Offer screenshot)
3. **Result:** "35% stay. Track everything in real-time." (Dashboard screenshot)
4. **Easy Setup:** "Build flows in minutes, no code." (Flow builder screenshot)
5. **Integration:** "Connect Stripe in 30 seconds." (Stripe screenshot)

This narrative arc = problem → solution → outcome → ease → trust

---

## Final Pre-Upload Checklist

**3 Days Before Launch:**
- [ ] All 5 screenshots captured
- [ ] Screenshots edited and annotated
- [ ] Demo GIF/video recorded (30 seconds)
- [ ] All files named clearly: `1-exit-survey.png`, `2-offer.png`, etc.
- [ ] Files backed up (don't lose them!)

**1 Day Before Launch:**
- [ ] Test upload screenshots to Product Hunt draft
- [ ] Verify they display correctly
- [ ] Order makes sense (tells the story)
- [ ] Hero image (Screenshot 1) looks compelling

**Launch Day:**
- [ ] Upload all assets
- [ ] Double-check sequence
- [ ] Click "Publish"
- [ ] 🚀 You're live!

---

## Need Help?

**Stuck on screenshots?**
- "I can't get good demo data" → Let me help you populate it
- "My dashboard looks empty" → Let me create dummy data script
- "I'm not good at design" → Just capture clean shots, I'll guide annotations
- "I don't have a demo GIF" → Screenshots alone work fine, GIF is bonus

**Want me to review?**
- Send me your screenshots and I'll give feedback before launch
- "Are these good enough?" → I'll tell you honestly
- "Which order should I use?" → I'll optimize the sequence

---

**You've got this! Take your time, make them clean, and tell a story.** 📸

**Next step:** Block 2 hours this week to capture all 5 screenshots. You'll be amazed at how good your product looks! 💪
