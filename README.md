# Customer Loyalty & Promotion Analysis

Retail customer segmentation and promotion-effectiveness analysis using the **dunnhumby Complete Journey** dataset.

## Business question

**Which customer groups respond most to promotions, and do the observed gains justify the discount cost?**

This project turns transaction-level grocery data into a customer-insight and commercial decision workflow: clean the data, segment households, compare promoted and non-promoted product-weeks, estimate commercial return, and communicate a recommendation.

## Dataset

The analysis uses dunnhumby's **The Complete Journey**, a public retail dataset containing household-level transactions from 2,500 frequent-shopper households over two years.

The raw dataset is **not committed to this repository**. Download `transaction_data.csv` from the source and place it in:

```text
data/transaction_data.csv
```

Dataset licensing is separate from this repository's code licence. The source identifies the database/content licensing under Open Data Commons. Please follow the source licence and attribution requirements when using the data.

## Reproduced results

The analysis was rerun against the source transaction file before publication.

| Metric | Result |
|---|---:|
| Clean transaction lines | 2,576,815 |
| Households | 2,500 |
| Shopping baskets | 275,539+ |
| Customer segments | 4 |
| Products eligible for promotion comparison | 13,249 |
| Overall observed uplift | 58.34% |
| Loyal High-Value share of spend | 68.44% |
| Low-Value observed uplift | 63.63% |
| Incremental sales estimate | ~£1.021m |
| Discount cost | ~£958.6k |
| Estimated net return at 25% gross margin | ~-£703.4k |

### Customer segments

| Segment | Households | Avg. recency | Avg. baskets | Avg. spend | Share of spend |
|---|---:|---:|---:|---:|---:|
| Low-Value | 400 | 97.64 days | 18.76 | £408.49 | 2.03% |
| Occasional | 521 | 3.19 days | 56.18 | £1,369.34 | 8.85% |
| Regular | 695 | 30.23 days | 77.00 | £2,397.47 | 20.68% |
| Loyal High-Value | 884 | 2.50 days | 209.56 | £6,237.99 | 68.44% |

## Commercial interpretation

Promoted product-weeks showed materially higher unit sales than non-promoted weeks. The highest measured percentage uplift was among **Low-Value** customers, but this group represented only about **2% of total spend**. The **Loyal High-Value** group represented about **68% of spend** and still showed substantial measured uplift.

However, higher sales do not automatically mean profitable promotions. Under the project's **25% gross-margin scenario**, estimated incremental gross profit did not cover the observed store-discount cost.

A sensible business response would therefore be to **test more targeted discounting rather than scale broad discounting automatically**, and validate the strategy with a controlled experiment.

## Method

1. Remove returns/zero-value transaction lines.
2. Build household RFM measures: recency, basket frequency and monetary spend.
3. Standardise log-transformed RFM features.
4. Create four customer groups with K-means (`random_state=42`).
5. Define a product-week as promoted when at least 50% of units sold had a store discount.
6. Retain products with at least five promoted and five non-promoted weeks.
7. Compare average weekly units in promoted vs non-promoted weeks.
8. Estimate incremental sales, discount cost and net return under a 25% gross-margin assumption.
9. Repeat the promotion analysis by customer segment.

## Important limitations

This is an **observational analysis**, not a randomised experiment. The uplift should therefore be described as an **association**, not proof that promotions caused the increase.

Key limitations:
- promotions were not randomly assigned;
- seasonality is not controlled;
- displays, mailers and other campaign activity may affect demand;
- the 25% gross margin is a scenario assumption, not an audited retailer margin;
- customer segment labels are ordered by average monetary spend; they are descriptive labels rather than known retailer segments.

A stronger next step would use matched stores/products or a randomised/control design and measure incremental profit rather than sales alone.

## Repository structure

```text
.
├── README.md
├── src/
│   └── loyalty_promo_analysis.py
├── outputs/
│   ├── segment_profile.csv
│   └── promotion_results.csv
├── requirements.txt
├── .gitignore
└── LICENSE
```

## Run locally

```bash
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install -r requirements.txt
python src/loyalty_promo_analysis.py
```

## Skills demonstrated

**Customer insights · RFM segmentation · K-means · promotion analysis · commercial interpretation · Python · pandas · scikit-learn · reproducible analytics · stakeholder communication**

## Author

**Tejasvi Ponugoti**

This is a self-directed portfolio project for learning and demonstration purposes.
