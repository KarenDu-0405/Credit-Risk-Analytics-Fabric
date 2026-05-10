# Tier-1 Credit Risk Analytics (Direct Lake & PySpark)

### The Mission
Simulating credit contagion and geopolitical shocks ("Greenland Risk") using a Python scriptted 10k-row synthetic CDS (Credit Default Swap) dataset.

### The Tech Stack
* **Platform:** Microsoft Fabric
* **Engine:** PySpark (Direct Lake) for high-performance ETL
* **Modeling:** Power BI Semantic Modeling & DAX
* **Storage:** Delta Lake (Parquet)

---

## Technical Deep-Dive

### 1. Credit Contagion & Risk Spillover
In quantitative risk management, monitoring static counterparty exposure is insufficient. During macroeconomic stress, an initial shock in one sector (e.g., Financial deregulation or bank capital constraints) can cause systemic contagion, dragging down the credit quality of non-financial sectors. To monitor this, I engineered a cross-sector sensitivity framework:
* **Drift Analysis:** Using the DAX Query View, I developed measures to calculate the "Contagion Beta" of non-financial sectors against a Financial benchmark.
* **The Findings:** The data highlights a distinct sectoral drift where Telecoms and Consumer sectors exhibit correlated repricing within Investment Grade debt during liquidity freezes. This allows for proactive hedging before the contagion matures.

### 2. Greenland Risk Stress Test
Earlier this year, global markets experienced severe volatility driven by escalating geopolitical tensions in Greenland. This module simulates a stochastic credit event—specifically, a sovereign default scenario triggering a parallel shift in global credit spreads.
* **The Logic:** Built a dynamic `Capital_Shortfall` measure using DAX to isolate the financial delta between current valuations and stressed scenarios.
* **The Quant Insight:** By implementing a 90bps shock, the model identified a **£4.7bn systemic liquidity gap**, with Financials exhibiting the highest sensitivity to the primary shock.

### 3. Regulatory Compliance: PRIN 12 / Consumer Duty
Under the FCA PRIN & COND sourcebook, retail customers require the highest level of regulatory protection to ensure market stability. I designed a dedicated monitoring tab for FCA PRIN 12 compliance to ensure "Retail" end-user protection.
* **Architecture:** Pushed compliance flagging logic upstream into the PySpark layer to maintain Direct Lake processing speeds while ensuring categorical accuracy.
* **Monitoring:** Automated the identification of High-Yield exposure within retail-scope holdings to actively prevent regulatory breaches.

---

## Dashboard Highlights
*(See attached video and screenshots for the full interactive demo).*

* **Overview & Limit Monitoring:** Tracks Total Notional Exposure (£ Millions) across the portfolio. Uses conditional formatting and DAX-driven threshold lines to instantly highlight counterparties breaching the 0.9% firm-wide concentration limit.
* **Contagion Scatter Model:** Maps non-financial sector spreads against a Financial Risk Benchmark. A dynamic trendline visualizes the "Contagion Beta," proving that a shock to the financial sector directly increases borrowing costs in Consumer, Energy, and Telecoms.
* **Interactive Slicing:** Executives can stress-test the model by cross-filtering between "Investment Grade" and "High Yield" corporate bonds to observe which rating buckets are most vulnerable to systemic shock.

---

## How to Navigate this Repository

* `Python_CDS_Data_Generator.ipynb`: The PySpark notebook containing the data generator for raw data, the market drift model.
* `Star_Schema.ipynb`: The PySpark notebook containing pipeline construction, data cleaning, and unpivot logic.
* `CDS Final Cloud Report.pbix`: The Fabric workspace Power BI file containing the semantic modeling logic and visual layer.
* `DAX_measures.txt`: A repository of the core quantitative DAX formulas used in the semantic model.
* `Screenshot_model_view.png`: A snapshot of the Star Schema modeling logic within the Fabric workspace.
* `CDS Final Cloud Report.pdf`: A static export of the final presentation layer.
* `CDS_final_cloud_report_video.mp4`: A 50-second voiceless video demonstrating the interactive stress-testing and contagion filtering capabilities.

