# ChurnShield ROI Calculator - Specification

## 🎯 Purpose

Create an interactive calculator on the landing page that shows prospects:
1. How much revenue they're losing to churn monthly/annually
2. How much ChurnShield can recover
3. The ROI vs subscription cost

**Why this works:**
- Makes the problem tangible (real dollar amounts)
- Personalizes the value prop (their specific numbers)
- Creates "aha moment" (didn't realize I'm losing this much!)
- Generates qualified leads (people who complete it are serious)

---

## User Experience Flow

### Step 1: Calculator Input Section
```
┌─────────────────────────────────────────────────────┐
│  💰 How much are you losing to churn?              │
│                                                      │
│  What's your Monthly Recurring Revenue?             │
│  [$________] /month                                 │
│                                                      │
│  What's your monthly churn rate?                    │
│  [_____%] (average SaaS: 5-7%)                      │
│                                                      │
│  [Calculate My Losses →]                            │
└─────────────────────────────────────────────────────┘
```

### Step 2: Results Display (appears after clicking Calculate)
```
┌─────────────────────────────────────────────────────┐
│  📊 Your Churn Analysis                             │
│                                                      │
│  You're losing: $X,XXX per month                    │
│                 $XX,XXX per year                     │
│                                                      │
│  With ChurnShield (30-40% recovery):                │
│  ✅ Recover: $X,XXX - $X,XXX per month             │
│  ✅ Annual savings: $XX,XXX - $XX,XXX              │
│                                                      │
│  ROI Calculation:                                    │
│  ChurnShield cost: $99/month ($1,188/year)          │
│  Your savings: $XX,XXX/year                         │
│  Net gain: $XX,XXX/year                             │
│  ROI: XXX%                                           │
│                                                      │
│  [Start Free Trial →] [Book Demo →]                 │
└─────────────────────────────────────────────────────┘
```

---

## Technical Implementation

### HTML Structure

```html
<!-- ROI Calculator Section -->
<section id="roi-calculator" class="py-20 bg-gradient-to-br from-primary/5 to-background">
  <div class="container max-w-4xl mx-auto px-4">
    <!-- Header -->
    <div class="text-center mb-12">
      <h2 class="text-4xl font-bold mb-4">
        💰 Calculate Your Churn Losses
      </h2>
      <p class="text-xl text-muted-foreground">
        See exactly how much revenue you're losing - and how much you can recover
      </p>
    </div>

    <!-- Calculator Card -->
    <div class="bg-card border rounded-xl shadow-lg p-8">
      <!-- Input Section -->
      <div id="calculator-input" class="space-y-6">
        <!-- MRR Input -->
        <div class="space-y-2">
          <label for="mrr-input" class="text-sm font-medium">
            What's your Monthly Recurring Revenue (MRR)?
          </label>
          <div class="relative">
            <span class="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">
              $
            </span>
            <input
              id="mrr-input"
              type="number"
              placeholder="10,000"
              min="0"
              step="1000"
              class="w-full pl-8 pr-4 py-3 border rounded-lg text-lg"
            />
          </div>
          <p class="text-sm text-muted-foreground">
            Total monthly subscription revenue
          </p>
        </div>

        <!-- Churn Rate Input -->
        <div class="space-y-2">
          <label for="churn-input" class="text-sm font-medium">
            What's your monthly churn rate?
          </label>
          <div class="relative">
            <input
              id="churn-input"
              type="number"
              placeholder="5"
              min="0"
              max="100"
              step="0.1"
              class="w-full pr-12 pl-4 py-3 border rounded-lg text-lg"
            />
            <span class="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground">
              %
            </span>
          </div>
          <p class="text-sm text-muted-foreground">
            Average SaaS: 5-7% · Not sure? <a href="#" class="text-primary hover:underline">Estimate it</a>
          </p>
        </div>

        <!-- Calculate Button -->
        <button
          id="calculate-btn"
          class="w-full bg-primary text-primary-foreground py-4 rounded-lg text-lg font-semibold hover:bg-primary/90 transition"
        >
          Calculate My Losses →
        </button>
      </div>

      <!-- Results Section (hidden initially) -->
      <div id="calculator-results" class="hidden mt-8 pt-8 border-t space-y-6">
        <!-- Current Losses -->
        <div class="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
          <h3 class="text-lg font-semibold mb-4 text-destructive">
            📉 Your Current Churn Losses
          </h3>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <p class="text-sm text-muted-foreground">Monthly</p>
              <p class="text-3xl font-bold text-destructive" id="loss-monthly">
                $0
              </p>
            </div>
            <div>
              <p class="text-sm text-muted-foreground">Annually</p>
              <p class="text-3xl font-bold text-destructive" id="loss-annual">
                $0
              </p>
            </div>
          </div>
        </div>

        <!-- ChurnShield Recovery -->
        <div class="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
          <h3 class="text-lg font-semibold mb-4 text-green-700 dark:text-green-400">
            ✅ With ChurnShield Recovery (30-40%)
          </h3>
          <div class="space-y-4">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <p class="text-sm text-muted-foreground">Monthly Recovery</p>
                <p class="text-2xl font-bold text-green-700 dark:text-green-400" id="recovery-monthly">
                  $0 - $0
                </p>
              </div>
              <div>
                <p class="text-sm text-muted-foreground">Annual Recovery</p>
                <p class="text-2xl font-bold text-green-700 dark:text-green-400" id="recovery-annual">
                  $0 - $0
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- ROI Calculation -->
        <div class="bg-primary/5 border border-primary/20 rounded-lg p-6">
          <h3 class="text-lg font-semibold mb-4">
            📊 Return on Investment
          </h3>
          <div class="space-y-3">
            <div class="flex justify-between">
              <span class="text-muted-foreground">ChurnShield Cost (annual)</span>
              <span class="font-semibold">$1,188</span>
            </div>
            <div class="flex justify-between">
              <span class="text-muted-foreground">Your Savings (annual)</span>
              <span class="font-semibold text-green-600" id="roi-savings">$0 - $0</span>
            </div>
            <div class="border-t pt-3 flex justify-between items-center">
              <span class="font-semibold">Net Gain (annual)</span>
              <span class="text-2xl font-bold text-primary" id="roi-net">$0 - $0</span>
            </div>
            <div class="flex justify-between items-center">
              <span class="font-semibold">ROI</span>
              <span class="text-2xl font-bold text-primary" id="roi-percentage">0%</span>
            </div>
          </div>
        </div>

        <!-- CTA Buttons -->
        <div class="flex flex-col sm:flex-row gap-4 pt-4">
          <a
            href="/signup"
            class="flex-1 bg-primary text-primary-foreground py-4 rounded-lg text-center font-semibold hover:bg-primary/90 transition"
          >
            Start Free Trial →
          </a>
          <a
            href="#book-demo"
            class="flex-1 border border-primary text-primary py-4 rounded-lg text-center font-semibold hover:bg-primary/5 transition"
          >
            Book a Demo
          </a>
        </div>

        <!-- Recalculate -->
        <button
          id="recalculate-btn"
          class="w-full text-center text-sm text-muted-foreground hover:text-foreground transition"
        >
          ← Recalculate with different numbers
        </button>
      </div>
    </div>

    <!-- Social Proof Under Calculator -->
    <div class="mt-12 text-center">
      <p class="text-sm text-muted-foreground mb-4">
        Trusted by SaaS companies recovering $50K+ monthly
      </p>
      <div class="flex justify-center gap-8 items-center opacity-60">
        <!-- Company logos here -->
      </div>
    </div>
  </div>
</section>
```

---

## JavaScript Logic

```typescript
// ROI Calculator Logic
interface CalculatorInputs {
  mrr: number;
  churnRate: number;
}

interface CalculatorResults {
  monthlyLoss: number;
  annualLoss: number;
  recoveryMonthlyLow: number;
  recoveryMonthlyHigh: number;
  recoveryAnnualLow: number;
  recoveryAnnualHigh: number;
  roiSavingsLow: number;
  roiSavingsHigh: number;
  roiNetLow: number;
  roiNetHigh: number;
  roiPercentage: number;
}

function calculateChurnROI(inputs: CalculatorInputs): CalculatorResults {
  const { mrr, churnRate } = inputs;

  // Constants
  const RECOVERY_RATE_LOW = 0.30;  // 30%
  const RECOVERY_RATE_HIGH = 0.40; // 40%
  const CHURNSHIELD_MONTHLY_COST = 99;
  const CHURNSHIELD_ANNUAL_COST = CHURNSHIELD_MONTHLY_COST * 12;

  // Calculate losses
  const monthlyLoss = mrr * (churnRate / 100);
  const annualLoss = monthlyLoss * 12;

  // Calculate recovery
  const recoveryMonthlyLow = monthlyLoss * RECOVERY_RATE_LOW;
  const recoveryMonthlyHigh = monthlyLoss * RECOVERY_RATE_HIGH;
  const recoveryAnnualLow = recoveryMonthlyLow * 12;
  const recoveryAnnualHigh = recoveryMonthlyHigh * 12;

  // Calculate ROI
  const roiSavingsLow = recoveryAnnualLow;
  const roiSavingsHigh = recoveryAnnualHigh;
  const roiNetLow = roiSavingsLow - CHURNSHIELD_ANNUAL_COST;
  const roiNetHigh = roiSavingsHigh - CHURNSHIELD_ANNUAL_COST;
  const roiPercentage = Math.round(((roiSavingsHigh - CHURNSHIELD_ANNUAL_COST) / CHURNSHIELD_ANNUAL_COST) * 100);

  return {
    monthlyLoss,
    annualLoss,
    recoveryMonthlyLow,
    recoveryMonthlyHigh,
    recoveryAnnualLow,
    recoveryAnnualHigh,
    roiSavingsLow,
    roiSavingsHigh,
    roiNetLow,
    roiNetHigh,
    roiPercentage
  };
}

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
}

function formatPercentage(percentage: number): string {
  return `${percentage.toLocaleString()}%`;
}

// DOM Event Handlers
document.addEventListener('DOMContentLoaded', () => {
  const mrrInput = document.getElementById('mrr-input') as HTMLInputElement;
  const churnInput = document.getElementById('churn-input') as HTMLInputElement;
  const calculateBtn = document.getElementById('calculate-btn') as HTMLButtonElement;
  const recalculateBtn = document.getElementById('recalculate-btn') as HTMLButtonElement;
  const inputSection = document.getElementById('calculator-input') as HTMLElement;
  const resultsSection = document.getElementById('calculator-results') as HTMLElement;

  // Calculate button click
  calculateBtn.addEventListener('click', () => {
    const mrr = parseFloat(mrrInput.value);
    const churnRate = parseFloat(churnInput.value);

    // Validation
    if (isNaN(mrr) || mrr <= 0) {
      alert('Please enter a valid MRR amount');
      mrrInput.focus();
      return;
    }

    if (isNaN(churnRate) || churnRate <= 0 || churnRate > 100) {
      alert('Please enter a valid churn rate (0-100%)');
      churnInput.focus();
      return;
    }

    // Calculate results
    const results = calculateChurnROI({ mrr, churnRate });

    // Update DOM
    document.getElementById('loss-monthly')!.textContent = formatCurrency(results.monthlyLoss);
    document.getElementById('loss-annual')!.textContent = formatCurrency(results.annualLoss);
    document.getElementById('recovery-monthly')!.textContent =
      `${formatCurrency(results.recoveryMonthlyLow)} - ${formatCurrency(results.recoveryMonthlyHigh)}`;
    document.getElementById('recovery-annual')!.textContent =
      `${formatCurrency(results.recoveryAnnualLow)} - ${formatCurrency(results.recoveryAnnualHigh)}`;
    document.getElementById('roi-savings')!.textContent =
      `${formatCurrency(results.roiSavingsLow)} - ${formatCurrency(results.roiSavingsHigh)}`;
    document.getElementById('roi-net')!.textContent =
      `${formatCurrency(results.roiNetLow)} - ${formatCurrency(results.roiNetHigh)}`;
    document.getElementById('roi-percentage')!.textContent = formatPercentage(results.roiPercentage);

    // Show results, hide inputs
    inputSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');

    // Smooth scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

    // Track analytics event
    trackEvent('roi_calculator_completed', {
      mrr: mrr,
      churn_rate: churnRate,
      monthly_loss: results.monthlyLoss,
      roi_percentage: results.roiPercentage
    });
  });

  // Recalculate button click
  recalculateBtn.addEventListener('click', () => {
    inputSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    mrrInput.focus();
  });

  // Enter key to calculate
  [mrrInput, churnInput].forEach(input => {
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        calculateBtn.click();
      }
    });
  });
});

// Analytics tracking (implement with your analytics tool)
function trackEvent(eventName: string, properties: Record<string, any>) {
  // Example: Google Analytics
  if (typeof gtag !== 'undefined') {
    gtag('event', eventName, properties);
  }

  // Example: Segment
  if (typeof analytics !== 'undefined') {
    analytics.track(eventName, properties);
  }

  // Example: Mixpanel
  if (typeof mixpanel !== 'undefined') {
    mixpanel.track(eventName, properties);
  }
}
```

---

## Implementation Steps

### Step 1: Create React Component (ChurnShield uses React)

**File:** `src/components/ROICalculator.tsx`

```tsx
import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface CalculatorResults {
  monthlyLoss: number;
  annualLoss: number;
  recoveryMonthlyLow: number;
  recoveryMonthlyHigh: number;
  recoveryAnnualLow: number;
  recoveryAnnualHigh: number;
  roiNetLow: number;
  roiNetHigh: number;
  roiPercentage: number;
}

const formatCurrency = (amount: number): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0
  }).format(amount);
};

export const ROICalculator = () => {
  const [mrr, setMrr] = useState<string>("");
  const [churnRate, setChurnRate] = useState<string>("");
  const [results, setResults] = useState<CalculatorResults | null>(null);
  const [showResults, setShowResults] = useState(false);

  const calculateROI = () => {
    const mrrNum = parseFloat(mrr);
    const churnNum = parseFloat(churnRate);

    if (isNaN(mrrNum) || mrrNum <= 0) {
      alert('Please enter a valid MRR amount');
      return;
    }

    if (isNaN(churnNum) || churnNum <= 0 || churnNum > 100) {
      alert('Please enter a valid churn rate (0-100%)');
      return;
    }

    const monthlyLoss = mrrNum * (churnNum / 100);
    const annualLoss = monthlyLoss * 12;
    const recoveryMonthlyLow = monthlyLoss * 0.30;
    const recoveryMonthlyHigh = monthlyLoss * 0.40;
    const recoveryAnnualLow = recoveryMonthlyLow * 12;
    const recoveryAnnualHigh = recoveryMonthlyHigh * 12;
    const churnshieldAnnualCost = 99 * 12;
    const roiNetLow = recoveryAnnualLow - churnshieldAnnualCost;
    const roiNetHigh = recoveryAnnualHigh - churnshieldAnnualCost;
    const roiPercentage = Math.round(((recoveryAnnualHigh - churnshieldAnnualCost) / churnshieldAnnualCost) * 100);

    setResults({
      monthlyLoss,
      annualLoss,
      recoveryMonthlyLow,
      recoveryMonthlyHigh,
      recoveryAnnualLow,
      recoveryAnnualHigh,
      roiNetLow,
      roiNetHigh,
      roiPercentage
    });

    setShowResults(true);

    // Track event (add your analytics here)
    console.log('ROI Calculated:', { mrr: mrrNum, churnRate: churnNum });
  };

  const recalculate = () => {
    setShowResults(false);
    setResults(null);
  };

  return (
    <section className="py-20 bg-gradient-to-br from-primary/5 to-background">
      <div className="container max-w-4xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="text-4xl font-bold mb-4">
            💰 Calculate Your Churn Losses
          </h2>
          <p className="text-xl text-muted-foreground">
            See exactly how much revenue you're losing - and how much you can recover
          </p>
        </div>

        <Card className="shadow-lg">
          <CardContent className="p-8">
            {!showResults ? (
              <div className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="mrr">What's your Monthly Recurring Revenue (MRR)?</Label>
                  <div className="relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-muted-foreground">
                      $
                    </span>
                    <Input
                      id="mrr"
                      type="number"
                      placeholder="10,000"
                      value={mrr}
                      onChange={(e) => setMrr(e.target.value)}
                      className="pl-8 text-lg"
                      onKeyPress={(e) => e.key === 'Enter' && calculateROI()}
                    />
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Total monthly subscription revenue
                  </p>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="churn">What's your monthly churn rate?</Label>
                  <div className="relative">
                    <Input
                      id="churn"
                      type="number"
                      placeholder="5"
                      value={churnRate}
                      onChange={(e) => setChurnRate(e.target.value)}
                      className="pr-12 text-lg"
                      onKeyPress={(e) => e.key === 'Enter' && calculateROI()}
                    />
                    <span className="absolute right-4 top-1/2 -translate-y-1/2 text-muted-foreground">
                      %
                    </span>
                  </div>
                  <p className="text-sm text-muted-foreground">
                    Average SaaS: 5-7% · Not sure? Try 5%
                  </p>
                </div>

                <Button
                  onClick={calculateROI}
                  className="w-full text-lg py-6"
                  size="lg"
                >
                  Calculate My Losses →
                </Button>
              </div>
            ) : results && (
              <div className="space-y-6">
                {/* Current Losses */}
                <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-destructive">
                    📉 Your Current Churn Losses
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Monthly</p>
                      <p className="text-3xl font-bold text-destructive">
                        {formatCurrency(results.monthlyLoss)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Annually</p>
                      <p className="text-3xl font-bold text-destructive">
                        {formatCurrency(results.annualLoss)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* Recovery */}
                <div className="bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4 text-green-700 dark:text-green-400">
                    ✅ With ChurnShield Recovery (30-40%)
                  </h3>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <p className="text-sm text-muted-foreground">Monthly Recovery</p>
                      <p className="text-2xl font-bold text-green-700 dark:text-green-400">
                        {formatCurrency(results.recoveryMonthlyLow)} - {formatCurrency(results.recoveryMonthlyHigh)}
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-muted-foreground">Annual Recovery</p>
                      <p className="text-2xl font-bold text-green-700 dark:text-green-400">
                        {formatCurrency(results.recoveryAnnualLow)} - {formatCurrency(results.recoveryAnnualHigh)}
                      </p>
                    </div>
                  </div>
                </div>

                {/* ROI */}
                <div className="bg-primary/5 border border-primary/20 rounded-lg p-6">
                  <h3 className="text-lg font-semibold mb-4">
                    📊 Return on Investment
                  </h3>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">ChurnShield Cost (annual)</span>
                      <span className="font-semibold">$1,188</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-muted-foreground">Your Savings (annual)</span>
                      <span className="font-semibold text-green-600">
                        {formatCurrency(results.recoveryAnnualLow)} - {formatCurrency(results.recoveryAnnualHigh)}
                      </span>
                    </div>
                    <div className="border-t pt-3 flex justify-between items-center">
                      <span className="font-semibold">Net Gain (annual)</span>
                      <span className="text-2xl font-bold text-primary">
                        {formatCurrency(results.roiNetLow)} - {formatCurrency(results.roiNetHigh)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="font-semibold">ROI</span>
                      <span className="text-2xl font-bold text-primary">
                        {results.roiPercentage}%
                      </span>
                    </div>
                  </div>
                </div>

                {/* CTAs */}
                <div className="flex flex-col sm:flex-row gap-4 pt-4">
                  <Button asChild className="flex-1 text-lg py-6" size="lg">
                    <a href="/signup">Start Free Trial →</a>
                  </Button>
                  <Button asChild variant="outline" className="flex-1 text-lg py-6" size="lg">
                    <a href="mailto:hello@churnshield.app">Book a Demo</a>
                  </Button>
                </div>

                <button
                  onClick={recalculate}
                  className="w-full text-center text-sm text-muted-foreground hover:text-foreground transition"
                >
                  ← Recalculate with different numbers
                </button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Social Proof */}
        <div className="mt-12 text-center">
          <p className="text-sm text-muted-foreground">
            Trusted by SaaS companies recovering $50K+ monthly
          </p>
        </div>
      </div>
    </section>
  );
};
```

### Step 2: Add to Landing Page

**File:** `src/pages/Index.tsx`

```tsx
import { ROICalculator } from "@/components/ROICalculator";

// ... other imports and components ...

export default function Index() {
  return (
    <div>
      {/* Hero Section */}
      <Hero />

      {/* Features Section */}
      <Features />

      {/* ROI Calculator - Add here! */}
      <ROICalculator />

      {/* Pricing Section */}
      <Pricing />

      {/* ... rest of page ... */}
    </div>
  );
}
```

---

## Analytics Tracking

Track these events:

1. **`roi_calculator_viewed`** - User scrolls to calculator
2. **`roi_calculator_interacted`** - User enters MRR or churn rate
3. **`roi_calculator_completed`** - User clicks "Calculate"
   - Properties: `mrr`, `churn_rate`, `monthly_loss`, `roi_percentage`
4. **`roi_calculator_cta_clicked`** - User clicks "Start Trial" or "Book Demo" from results
   - Properties: `cta_type` (trial or demo), `roi_percentage`

---

## A/B Test Ideas

### Test 1: Recovery Rate Claims
- **Variant A:** "30-40% recovery" (current)
- **Variant B:** "Average 35% recovery"
- **Variant C:** "Up to 40% recovery"

### Test 2: Calculator Placement
- **Variant A:** After features, before pricing (current)
- **Variant B:** Immediately after hero (above fold)
- **Variant C:** After pricing (end of page)

### Test 3: Input Defaults
- **Variant A:** Empty inputs (user enters everything)
- **Variant B:** Pre-filled with "$10,000" MRR and "5%" churn
- **Variant C:** Progressive disclosure (ask MRR first, then churn)

---

## Success Metrics

**Calculator Engagement:**
- 30%+ of page visitors interact with calculator (enter data)
- 60%+ of interactors complete calculation
- 20%+ of completers click CTA

**Lead Quality:**
- Leads from calculator convert 2-3x higher than average
- Higher MRR inputs correlate with faster sales cycles
- Higher ROI calculations correlate with higher close rates

---

## Next Steps

1. **Create the React component** (use code above)
2. **Add to Index.tsx** landing page
3. **Set up analytics tracking** (Google Analytics/Mixpanel)
4. **Test thoroughly** (various MRR/churn combinations)
5. **Monitor conversion rates** (calculator → trial signup)
6. **Iterate based on data** (A/B tests)

---

**This calculator will be your highest-converting element.** People love seeing their own numbers!

