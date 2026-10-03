# Unit 2 — System Development Life Cycle (SDLC) Deep Dive & Project Inception
## Lesson 2 — Multi-Dimensional Feasibility Engineering: The TELOS & Economic ROI Frameworks

### 1. The Architecture of Feasibility Analysis & Decision Gates

In software engineering management, a catastrophic error is confusing a technical project proposal with a viable business undertaking. A software system may be technically brilliant, written in state-of-the-art languages and hosted on cutting-edge cloud infrastructure; however, if it violates data privacy laws, incites user rebellion, or produces negative financial returns, the project is a catastrophic organizational failure.

A **Feasibility Study** is a formal, objective investigation conducted during the project inception phase to determine whether a proposed software system **should be constructed**.

```
+-----------------------------------------------------------------------------------------+
|                        THE FEASIBILITY STUDY DECISION FUNNEL                            |
|                                                                                         |
|       +-------------------------------------------------------------------------+       |
|       | 1. UNDERSTAND THE REAL BUSINESS PROBLEM / OPPORTUNITY:                  |       |
|       | • What operational friction or market loss is occurring?               |       |
|       | • Differentiate root causes from superficial symptoms!                  |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|                                           v                                             |
|       +-------------------------------------------------------------------------+       |
|       | 2. SYNTHESIZE MULTIPLE COMPETING ARCHITECTURAL ALTERNATIVES:            |       |
|       | • Alternative 0: Do Nothing (Baseline Status Quo).                      |       |
|       | • Alternative 1: Purchase Commercial Off-the-Shelf (COTS) SaaS.        |       |
|       | • Alternative 2: Custom In-House Cloud-Native Microservices Build.      |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|                                           v                                             |
|       +-------------------------------------------------------------------------+       |
|       | 3. MULTI-DIMENSIONAL SCREENING (THE TELOS FRAMEWORK):                   |       |
|       | • Filter each alternative across Technical, Economic, Legal,           |       |
|       |   Operational, Schedule, and Political feasibility.                     |       |
|       +-------------------------------------------------------------------------+       |
|                                           |                                             |
|                                           v                                             |
|       +-------------------------------------------------------------------------+       |
|       | 4. EXECUTIVE MILESTONE DECISION GATE:                                   |       |
|       | • Formal Feasibility Study Report (FSR) presented to C-Suite.           |       |
|       | • Formal Decision: GO, NO-GO (Terminate), or REDESIGN SCOPE.           |       |
|       +-------------------------------------------------------------------------+       |
+-----------------------------------------------------------------------------------------+
```

#### Core Objectives of the Feasibility Study
1. **Analyze Strategic Fit:** Verify that the system fulfills measurable corporate business objectives.
2. **Quantify Technical Realizability:** Confirm that required hardware, cloud capacity, networking bandwidth, and software development skills exist or can be acquired.
3. **Establish Economic Justification:** Demonstrate that the discounted financial benefits outweigh the total cost of ownership (TCO) across the system lifecycle.
4. **Identify Critical Fatal Flaws Early:** Discover compliance violations, labor union disputes, or fatal scheduling bottlenecks before committing millions of dollars in capital expenditure!

{{ media:sam-feasibility-telos-diagram }}

---

### 2. The TELOS (+P) Multi-Dimensional Feasibility Framework

To ensure that no dimension of risk is overlooked, software analysts evaluate projects against the **TELOS Framework** (augmented by modern political/cultural feasibility):

```
+-----------------------------------------------------------------------------------------+
|                                 THE TELOS (+P) FRAMEWORK                                |
|                                                                                         |
|       +-------------------+       +-------------------+       +-------------------+     |
|       |    T: TECHNICAL   |       |    E: ECONOMIC    |       |     L: LEGAL      |     |
|       | • Architecture    |       | • Cost-Benefit    |       | • GDPR, HIPAA     |     |
|       | • Hardware/Cloud  |       | • Cash Flows / NPV|       | • Copyright/IP    |     |
|       | • Team Expertise  |       | • Payback Period  |       | • Vendor Liability|     |
|       +-------------------+       +-------------------+       +-------------------+     |
|                 ^                           ^                           ^               |
|                 |                           |                           |               |
|       =============================================================================     |
|       |                       PROJECT FEASIBILITY VERDICT                         |     |
|       =============================================================================     |
|                 v                           v                           v               |
|                 |                           |                           |               |
|       +-------------------+       +-------------------+       +-------------------+     |
|       |   O: OPERATIONAL  |       |    S: SCHEDULE    |       |    P: POLITICAL   |     |
|       | • User Resistance |       | • Mandatory Dates |       | • Stakeholder Buy |     |
|       | • Workflow Impact |       | • Critical Path   |       | • Power Shifts    |     |
|       | • Retraining Load |       | • Resource Contend|       | • Org Culture     |     |
|       +-------------------+       +-------------------+       +-------------------+     |
+-----------------------------------------------------------------------------------------+
```

#### Detailed Breakdown of Dimensions

##### 1. Technical Feasibility (Can it be engineered?)
- **Hardware & Network Infrastructure:** Does the target environment have the compute, storage, and low-latency network bandwidth required to sustain projected peak transaction volumes?
- **Engineering Skill Availability:** Does the in-house development team possess expertise in the chosen technology stack (e.g., Rust, Kubernetes, distributed consensus)? If not, can external consultants be hired within budget?
- **Technological Maturity:** Is the proposed software architecture based on stable, proven standards, or does it depend on unproven, experimental libraries prone to breaking changes?
- **Architectural Scalability:** Can the system gracefully scale from 1,000 concurrent users to 1,000,000 users without fundamental redesign?

##### 2. Economic Feasibility (Is it financially viable?)
- Assesses whether the tangible and intangible financial benefits generated by the software exceed the development, deployment, and operational costs. (Analyzed in deep mathematical detail in Section 3).

##### 3. Legal and Contractual Feasibility (Is it legally permissible?)
- **Regulatory Compliance:** Does the software comply with national and international statutory mandates? (e.g., European Union GDPR privacy rights, United States HIPAA healthcare record privacy, PCI-DSS payment card data security standards).
- **Intellectual Property & Licensing:** Does the project utilize open-source components with restrictive copyleft licenses (e.g., GNU GPLv3) that would legally force the enterprise to open-source its proprietary intellectual property?
- **Contractual & Service Level Liabilities:** Does the software expose the enterprise to crippling financial breach-of-contract penalties if cloud availability dips below 99.99%?

##### 4. Operational / Behavioral Feasibility (Will humans embrace it?)
- **User Resistance to Change:** Software projects frequently collapse not because of software bugs, but because operational staff actively sabotage or refuse to use the new system.
- **Workflow Congruence:** Does the software align with natural human operational habits, or does it impose rigid, unnatural clerical burdens?
- **Ergonomics & Training:** What is the cognitive load imposed on operators? How many weeks of training are required before employees reach baseline productivity?
- **Labor Union Agreements:** Does automating a process violate collective bargaining agreements regarding employee displacement or job classifications?

##### 5. Schedule Feasibility (Can it be delivered in time?)
- **Mandatory External Deadlines:** Is the delivery date constrained by immovable external events? (e.g., a tax compliance software update that MUST be active by January 1st; a retail system that MUST be operational prior to Black Friday).
- **Critical Path Analysis:** Does the project schedule contain sufficient slack, or does a single 2-week delay in API development trigger a project-wide milestone failure?

##### 6. Political and Cultural Feasibility (How will organizational power shift?)
- **Stakeholder Power Dynamics:** In every enterprise, "information is power." A software system that centralizes reporting often strips departmental managers of their autonomy, creating covert political resistance.
- **Executive Sponsorship:** Does the project have a powerful C-suite champion capable of resolving inter-departmental turf wars?
- **Corporate Culture Alignment:** Does a rigid, process-heavy software framework clash with an open, entrepreneurial corporate culture?

---

### 3. Quantitative Cost-Benefit Analysis (CBA): Tangible vs. Intangible, NPV & Payback

Economic feasibility is the definitive quantitative pillar of the Feasibility Study. Systems analysts must construct a rigorous financial model evaluating the **Total Cost of Ownership (TCO)** against projected business returns.

#### 1. Categorization of Costs and Benefits

```
+-----------------------------------------------------------------------------------------+
|                           THE ECONOMIC COST-BENEFIT SPECTRUM                            |
|                                                                                         |
|       [ COSTS ]                                     [ BENEFITS ]                        |
|                                                                                         |
|       TANGIBLE DEVELOPMENT COSTS (CapEx):           TANGIBLE FINANCIAL SAVINGS:         |
|       • Server hardware & cloud infrastructure      • Direct elimination of manual labor|
|       • Software developer & analyst salaries       • Reduced inventory carrying costs  |
|       • Commercial database / software licenses     • Elimination of physical paper/post|
|       • Physical networking & site preparation      • Reduced fraud & shrinkage losses  |
|                                                                                         |
|       TANGIBLE OPERATIONAL COSTS (OpEx):            TANGIBLE REVENUE GENERATION:        |
|       • Monthly cloud hosting bills (AWS/Azure)     • Increased transaction throughput  |
|       • Software maintenance & support contracts    • Unlocking new digital channels    |
|       • Ongoing employee training & helpdesk        • Reduced customer churn rate       |
|                                                                                         |
|       INTANGIBLE COSTS:                             INTANGIBLE BENEFITS:                |
|       • Temporary drop in worker productivity       • Enhanced corporate brand prestige |
|       • Employee morale dips during transition      • Improved customer satisfaction    |
|       • Disruption of existing client routines      • Faster executive decision-making  |
+-----------------------------------------------------------------------------------------+
```

#### 2. The Time Value of Money & Cash Flow Discounting
A dollar earned five years in the future is worth significantly less than a dollar held today, due to inflation and the opportunity cost of capital (interest rates).
To evaluate multi-year projects objectively, analysts apply **Discounted Cash Flow (DCF)** modeling.

##### The Present Value ($PV$) Formula:
$$PV = \frac{CF_t}{(1 + r)^t}$$
Where:
- $CF_t$ = Net Cash Flow in year $t$ ($\text{Cash Flow} = \text{Benefits}_t - \text{Costs}_t$).
- $r$ = Discount Rate (the company's Cost of Capital or Required Hurdle Rate, typically $8\%\text{ to }14\%$).
- $t$ = Year index ($t \in \{1, 2, 3, \dots, n\}$).

#### 3. Core Financial Decision Metrics

##### A. Net Present Value ($NPV$)
The sum of all discounted future cash flows across the system's operational lifespan minus the initial capital investment ($C_0$):

$$NPV = \sum_{t=1}^n \frac{CF_t}{(1 + r)^t} - C_0$$

- **The NPV Decision Rule:**
  - If $NPV > 0 \implies$ **Accept the Project!** The system generates wealth exceeding the cost of capital.
  - If $NPV = 0 \implies$ Indifferent (breaks even with cost of capital).
  - If $NPV < 0 \implies$ **Reject the Project!** The company loses money compared to keeping capital in a risk-free bond.

##### B. Return on Investment ($ROI$)
The percentage ratio of total net lifetime benefits to total lifetime costs:

$$ROI = \frac{\text{Total Cumulative Discounted Benefits} - \text{Total Cumulative Discounted Costs}}{\text{Total Cumulative Discounted Costs}} \times 100\%$$

##### C. Break-Even Payback Period
The precise calendar duration required for cumulative discounted financial benefits to equal the cumulative investment costs.
- The shorter the payback period, the lower the project's financial liquidity risk.

---

### 4. The Formal Feasibility Study Report (FSR) Structure

The culmination of the feasibility investigation is the formal publication and presentation of the **Feasibility Study Report (FSR)**. The FSR is an executive document that follows a standardized engineering structure:

```
+-----------------------------------------------------------------------------------------+
|                   STRUCTURE OF THE FEASIBILITY STUDY REPORT (FSR)                       |
|                                                                                         |
|       1. EXECUTIVE SUMMARY:                                                             |
|          • Concise 1-page synthesis for C-suite decision-makers.                        |
|          • High-level statement of problem, evaluated alternatives & recommended path.  |
|                                                                                         |
|       2. BUSINESS PROBLEM & OBJECTIVES:                                                 |
|          • Current operational friction, quantified revenue losses, root causes.        |
|                                                                                         |
|       3. EVALUATION OF COMPETING ALTERNATIVES:                                          |
|          • Alternative 0 (Status Quo), Alternative 1 (COTS), Alternative 2 (Custom).    |
|                                                                                         |
|       4. MULTI-DIMENSIONAL FEASIBILITY ASSESSMENT:                                      |
|          • Detailed Technical, Legal, Operational, Schedule, and Political analyses.    |
|                                                                                         |
|       5. FINANCIAL COST-BENEFIT ANALYSIS (CBA):                                         |
|          • 5-Year Cash Flow Discounting Table, NPV, ROI, and Payback curves.            |
|                                                                                         |
|       6. RISK MATRIX & MITIGATION STRATEGY:                                             |
|          • Top 10 identified project risks, severity, probability & contingencies.      |
|                                                                                         |
|       7. FINAL RECOMMENDATIONS & NEXT STEPS:                                            |
|          • Explicit Go/No-Go proposal and initial Project Charter baseline.             |
+-----------------------------------------------------------------------------------------+
```

---

### 5. Progressive Multi-Tier Practice Suite

#### Level 1 — Architectural Walkthrough: Quantitative 5-Year Economic Feasibility Analysis

##### Problem Statement
A regional retail bank evaluates an investment to replace its legacy in-branch loan origination system with a Cloud-Native Automated Loan Origination Engine.
The bank's financial analysts establish the following baseline parameters:
- **Discount Rate ($r$):** $10.0\%$ ($0.10$).
- **Year 0 (Initial Capital Outlay / Development):** $C_0 = \$600,000$.
- **Year 1:** Operating Costs = $\$60,000$ | Financial Benefits = $\$200,000$ (Net $CF_1 = +\$140,000$).
- **Year 2:** Operating Costs = $\$70,000$ | Financial Benefits = $\$320,000$ (Net $CF_2 = +\$250,000$).
- **Year 3:** Operating Costs = $\$80,000$ | Financial Benefits = $\$400,000$ (Net $CF_3 = +\$320,000$).
- **Year 4:** Operating Costs = $\$90,000$ | Financial Benefits = $\$420,000$ (Net $CF_4 = +\$330,000$).
- **Year 5:** Operating Costs = $\$100,000$ | Financial Benefits = $\$380,000$ (Net $CF_5 = +\$280,000$).

Calculate:
1. The Discount Factor ($DF_t = \frac{1}{(1.10)^t}$) for each year (to 3 decimal places).
2. The Present Value ($PV$) of net cash flows for Years 1 through 5.
3. The overall **Net Present Value ($NPV$)**.
4. The exact **Break-Even Payback Period**.

##### Analytical Calculations & Discounting Table

| Year ($t$) | Net Cash Flow ($CF_t$) | Discount Factor ($1 / 1.10^t$) | Present Value ($PV = CF \times DF$) | Cumulative Discounted Cash Flow |
| :---: | :---: | :---: | :---: | :---: |
| **Year 0** | $-\$600,000$ | $1.000$ | $-\$600,000.00$ | $-\$600,000.00$ |
| **Year 1** | $+\$140,000$ | $0.909$ | $+\$127,260.00$ | $-\$472,740.00$ |
| **Year 2** | $+\$250,000$ | $0.826$ | $+\$206,500.00$ | $-\$266,240.00$ |
| **Year 3** | $+\$320,000$ | $0.751$ | $+\$240,320.00$ | $-\$25,920.00$ |
| **Year 4** | $+\$330,000$ | $0.683$ | $+\$225,390.00$ | **$+\$199,470.00$** |
| **Year 5** | $+\$280,000$ | $0.621$ | $+\$173,880.00$ | $+\$373,350.00$ |

##### 1. Total Cumulative Discounted Present Value of Future Inflows:
$$\sum_{t=1}^5 PV_t = 127,260 + 206,500 + 240,320 + 225,390 + 173,880 = \mathbf{\$973,350.00}$$

##### 2. Net Present Value ($NPV$):
$$NPV = \sum_{t=1}^5 PV_t - C_0 = \$973,350.00 - \$600,000.00 = \mathbf{+\$373,350.00}$$
**Economic Verdict:** Because $NPV = +\$373,350 > 0$, the project is **highly profitable** and easily clears the bank's $10\%$ cost of capital.

##### 3. Payback Period Calculation:
At the end of Year 3, the cumulative deficit is $-\$25,920.00$.
During Year 4, the system generates $+\$225,390.00$ in discounted present value.
$$\text{Fraction of Year 4 to Break Even} = \frac{\$25,920}{\$225,390} \approx 0.115\text{ years}$$
$$\text{Payback Period} = 3.0 + 0.115 \approx \mathbf{3.12\text{ Years } (\sim 3\text{ Years and } 1.5\text{ Months})}$$

---

#### Level 2 — Scaffolded Bug-Fix: The "Omission of Intangible & Operational Costs" Fallacy

##### Defect Scenario
A multinational consulting firm submitted a feasibility study for an enterprise ERP migration. The financial model projected an incredible $NPV$ of **$+\$4,500,000$** with a payback period of only 14 months:

```python
# DEFECTIVE FEASIBILITY COST MODEL: FATAL OMISSIONS
def calculate_defective_tco():
    # Only direct software licenses and server hosting were included!
    software_licenses = 500000.0
    aws_cloud_hosting = 120000.0
    implementation_vendor_fee = 600000.0
    
    # FATAL DEFECT: Completely ignored human operational costs!
    total_cost = software_licenses + aws_cloud_hosting + implementation_vendor_fee
    print(f"Reported Project Cost: ${total_cost:,.2f}") # Reports $1,220,000
```

When deployed in production, the project triggered a financial disaster:
- 2,000 employees suffered a **$35\%$ productivity collapse** for 4 months because training was inadequate, causing $\$1.8\text{M}$ in missed customer order deadlines.
- The company was forced to maintain the legacy mainframe system in parallel for an extra year due to data migration corruption ($\$650\text{k}$ unplanned expense).
- Actual Total Cost of Ownership surged from $\$1.22\text{M}$ to **$\$4.1\text{M}$**, turning a supposedly profitable project into a massive net financial loss!

##### Systems Analysis Diagnosis
The feasibility study committed the classical **Total Cost of Ownership (TCO) Underestimation Fallacy**. In enterprise software, direct software licenses and hardware typically represent **less than $30\%$ of true lifetime costs**! The remaining $70\%$ is dominated by indirect human factors: data cleansing, user retraining, organizational productivity dips, legacy dual-running, and ongoing maintenance.

<details>
<summary><b>View Architectural Solution & Comprehensive TCO Financial Modeling Framework</b></summary>

```python
# ============================================================================
# COMPREHENSIVE FINANCIAL MODEL: TOTAL COST OF OWNERSHIP (TCO) ENGINE
# ============================================================================
class EnterpriseTCOCalculator:
    def __init__(self, num_employees, avg_hourly_wage):
        self.num_employees = num_employees
        self.avg_hourly_wage = avg_hourly_wage

    def compute_rigorous_tco(self, license_cost, cloud_annual, vendor_fee):
        costs = {}
        
        # 1. Direct Capital Expenditures (CapEx)
        costs["Direct Software Licenses"] = license_cost
        costs["System Integrator Vendor Fees"] = vendor_fee
        
        # 2. Direct Operational Expenditures (OpEx - 3 Years)
        costs["Cloud Infrastructure (3 Yrs)"] = cloud_annual * 3.0
        costs["Third-Party Support & Maintenance (20% license/yr)"] = license_cost * 0.20 * 3.0

        # 3. Human Factors & Operational Change Costs (MANDATORY INCLUSION)
        # Training: 40 hours per employee
        training_hours = 40
        costs["Employee Training Labor"] = self.num_employees * training_hours * self.avg_hourly_wage
        
        # Productivity Dip: 25% efficiency drop during first 60 days (480 hours)
        dip_hours = 480
        efficiency_loss_pct = 0.25
        costs["Productivity Dip Transition Penalty"] = (
            self.num_employees * dip_hours * self.avg_hourly_wage * efficiency_loss_pct
        )

        # Legacy Mainframe Dual-Running & Data Cleansing Bridge
        costs["Data Scrubbing & Dual-Run Mainframe Overhead"] = 450000.0

        # 4. Total Cost of Ownership Aggregation
        total_tco = sum(costs.values())
        return costs, total_tco

# Execution
calc = EnterpriseTCOCalculator(num_employees=2000, avg_hourly_wage=45.0) # $45/hr average salary
cost_breakdown, true_tco = calc.compute_rigorous_tco(
    license_cost=500000.0, cloud_annual=120000.0, vendor_fee=600000.0
)

print("======================================================================")
print("             RIGOROUS ENTERPRISE TCO FEASIBILITY AUDIT                ")
print("======================================================================")
for category, amount in cost_breakdown.items():
    print(f"{category:45} : ${amount:12,.2f}")
print("----------------------------------------------------------------------")
print(f"TRUE TOTAL COST OF OWNERSHIP (TCO)           : ${true_tco:12,.2f}")
print("======================================================================")
# Reveals true TCO is $12.16M, completely reversing naive feasibility assumptions!
```

</details>

---

#### Level 3 — High-Scale System Design: Financial Feasibility & Sensitivity Tornado Simulator in C++

Design a complete, production-grade C++17 simulation modeling:
1. **Multi-Alternative Feasibility Evaluator:** Evaluates three competing architectural solutions (COTS SaaS vs. Custom Cloud Microservices vs. Outsourced Legacy Refactoring).
2. **Dynamic Cash Flow Discounting:** Calculates Net Present Value ($NPV$), Internal Rate of Return ($IRR$), and Discounted Payback Period.
3. **Sensitivity Tornado Analysis:** Perturbs discount rates ($\pm 3\%$), development costs ($\pm 20\%$), and annual benefit streams ($\pm 25\%$) to identify which variable introduces the greatest financial volatility.

<details>
<summary><b>View Complete C++ Feasibility & Sensitivity Simulator Implementation</b></summary>

```cpp
// ============================================================================
// SYSTEM ARCHITECTURE: FINANCIAL FEASIBILITY & SENSITIVITY TORNADO ENGINE
// Compile: g++ -std=c++17 -O3 feasibility_engine.cpp -o feasibility_engine
// ============================================================================

#include <iostream>
#include <vector>
#include <string>
#include <cmath>
#include <iomanip>
#include <cstdint>

struct ArchitecturalAlternative {
    std::string name;
    double initial_investment_usd;
    std::vector<double> annual_net_cash_flows; // Years 1 through 5
};

class FeasibilityEconomicEngine {
public:
    static double calculate_npv(double initial_cost, const std::vector<double>& cash_flows, double discount_rate) {
        double npv = -initial_cost;
        for (size_t t = 0; t < cash_flows.size(); t++) {
            double pv = cash_flows[t] / std::pow(1.0 + discount_rate, static_cast<double>(t + 1));
            npv += pv;
        }
        return npv;
    }

    static double calculate_payback_years(double initial_cost, const std::vector<double>& cash_flows, double discount_rate) {
        double cumulative_pv = -initial_cost;
        for (size_t t = 0; t < cash_flows.size(); t++) {
            double pv = cash_flows[t] / std::pow(1.0 + discount_rate, static_cast<double>(t + 1));
            double prev_cumulative = cumulative_pv;
            cumulative_pv += pv;

            if (cumulative_pv >= 0.0) {
                // Linear interpolation within year t
                double fraction = (-prev_cumulative) / pv;
                return static_cast<double>(t) + fraction;
            }
        }
        return -1.0; // Does not pay back within evaluation window
    }

    static void run_sensitivity_tornado(const ArchitecturalAlternative& alt, double base_discount_rate) {
        std::cout << "\n======================================================================\n";
        std::cout << "  SENSITIVITY TORNADO ANALYSIS: " << alt.name << "\n";
        std::cout << "======================================================================\n";

        double baseline_npv = calculate_npv(alt.initial_investment_usd, alt.annual_net_cash_flows, base_discount_rate);
        std::cout << "Baseline NPV (Rate=" << (base_discount_rate * 100.0) << "%): $" 
                  << std::fixed << std::setprecision(2) << baseline_npv << "\n\n";

        // Variable 1: Discount Rate Shock (Rate - 3% vs Rate + 3%)
        double npv_rate_low  = calculate_npv(alt.initial_investment_usd, alt.annual_net_cash_flows, base_discount_rate - 0.03);
        double npv_rate_high = calculate_npv(alt.initial_investment_usd, alt.annual_net_cash_flows, base_discount_rate + 0.03);
        std::cout << "1. Discount Rate (7% to 13%)   : Low: $" << npv_rate_low 
                  << " | High: $" << npv_rate_high << " (Spread: $" << (npv_rate_low - npv_rate_high) << ")\n";

        // Variable 2: Development Cost Overrun (-10% vs +25%)
        double npv_cost_low  = calculate_npv(alt.initial_investment_usd * 0.90, alt.annual_net_cash_flows, base_discount_rate);
        double npv_cost_high = calculate_npv(alt.initial_investment_usd * 1.25, alt.annual_net_cash_flows, base_discount_rate);
        std::cout << "2. Development Cost (-10%/+25%): Low: $" << npv_cost_low 
                  << " | High: $" << npv_cost_high << " (Spread: $" << (npv_cost_low - npv_cost_high) << ")\n";

        // Variable 3: Benefit Volatility (-20% vs +20%)
        std::vector<double> flows_low = alt.annual_net_cash_flows;
        std::vector<double> flows_high = alt.annual_net_cash_flows;
        for (auto& f : flows_low) f *= 0.80;
        for (auto& f : flows_high) f *= 1.20;
        double npv_ben_low  = calculate_npv(alt.initial_investment_usd, flows_low, base_discount_rate);
        double npv_ben_high = calculate_npv(alt.initial_investment_usd, flows_high, base_discount_rate);
        std::cout << "3. Benefit Realization (±20%)  : Low: $" << npv_ben_low 
                  << " | High: $" << npv_ben_high << " (Spread: $" << (npv_ben_high - npv_ben_low) << ")\n";
        std::cout << "----------------------------------------------------------------------\n";
    }
};

int main() {
    std::cout << "======================================================================\n";
    std::cout << "       ENTERPRISE FEASIBILITY EVALUATION & SELECTION ENGINE           \n";
    std::cout << "======================================================================\n";

    std::vector<ArchitecturalAlternative> options = {
        {"Option A: Custom Cloud Microservices", 1200000.0, {300000.0, 500000.0, 700000.0, 800000.0, 850000.0}},
        {"Option B: Commercial SaaS Implementation", 400000.0, {150000.0, 220000.0, 250000.0, 250000.0, 250000.0}},
        {"Option C: Legacy Modernization Wrap", 600000.0, {180000.0, 220000.0, 240000.0, 240000.0, 240000.0}}
    };

    const double base_discount_rate = 0.10; // 10% Hurdle Rate

    for (const auto& opt : options) {
        double npv = FeasibilityEconomicEngine::calculate_npv(opt.initial_investment_usd, opt.annual_net_cash_flows, base_discount_rate);
        double payback = FeasibilityEconomicEngine::calculate_payback_years(opt.initial_investment_usd, opt.annual_net_cash_flows, base_discount_rate);

        std::cout << "\nALTERNATIVE: " << opt.name << "\n"
                  << "  • Initial Capex : $" << std::fixed << std::setprecision(2) << opt.initial_investment_usd << "\n"
                  << "  • 5-Year NPV    : $" << npv << (npv > 0 ? " (ACCEPTABLE)" : " (REJECT)") << "\n"
                  << "  • Payback Period: " << (payback > 0 ? (std::to_string(payback) + " Years") : "NEVER") << "\n";
    }

    // Run sensitivity analysis on highest NPV candidate (Option A)
    FeasibilityEconomicEngine::run_sensitivity_tornado(options[0], base_discount_rate);

    return 0;
}
```

</details>

---

### 6. Reference Video Lecture

{{ media:systems-theory-video }}

In this video by Crash Course Computer Science, the systematic lifecycle of complex computing systems is explored, illustrating why multi-dimensional feasibility, resource constraints, and operational governance are essential prerequisites before committing to full-scale software construction.
