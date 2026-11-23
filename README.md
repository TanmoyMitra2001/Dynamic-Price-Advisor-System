# Explainable Dynamic Price Advisor

A rule-based pricing assistant that suggests price changes for retail items and **explains every suggestion in plain language**. It combines price sensitivity (elasticity), demand trend and stock status.

> End Term Project, Department of Computer Science and Engineering, Tezpur University
> Supervisor: Dr. Dhruba K Bhattacharyya

## Team

| Name | Roll No. |
|---|---|
| Agraj Milind | CSM25002 |
| Riteeka Dutta | CSM25025 |
| Tanmoy Mitra | CSM25061 |

## Problem

Retail pricing is often manual and static. Existing tools give recommendations without reasons, so managers find them hard to trust. This project suggests price changes from data and states why each change was made.

## Features

- Price elasticity estimated per product from sales data
- Demand trend and stock status computed per item
- Rule engine that suggests a price change, scaled by a damping factor
- A plain-language explanation for every suggestion
- Time-based evaluation of the elasticity estimates
- Streamlit app with filters, item lookup, charts and CSV download

## Datasets

| Dataset | Used for | Notes |
|---|---|---|
| Online Retail II | Price and quantity, so elasticity | No stock or views |
| Retail Rocket (4 files) | Views, add-to-carts, purchases and stock availability | No price |

The two datasets cannot be joined by ID (`StockCode` vs `itemid`), so they meet only through one store-wide damping factor.

## How it works

```
Online Retail II --> clean --> daily table --> elasticity --> damping factor --+
                                                                              |
Retail Rocket ----> clean --> demand trend + stock status ---------------------+--> rule engine --> explanation --> advisor_data.csv --> Streamlit app
```

1. **Elasticity** = % change in quantity / % change in price, per product, using the previous record of the same product. Rows with no price change are removed, and values are clipped to [-20, 20].
2. **Demand trend** = events in the recent half / events in the older half of the timeline.
3. **Stock status** = latest `available` value (1 = in stock, 0 = out of stock; no record is treated as in stock).
4. **Damping factor** = `min(1, 3 / |average elasticity|)`.
5. **Rule engine** picks a base change, then multiplies it by the damping factor.

| Demand | In stock | Out of stock |
|---|---|---|
| Rising (trend > 1) | +4% | +10% |
| Falling (trend < 1) | -8% | -2% |
| Stable (trend = 1) | 0% | 0% |

The base steps and the constant 3 in the damping factor are design assumptions and can be tuned.

## Results

| Item | Value |
|---|---|
| Online Retail II rows after cleaning | 504,730 (from 525,461) |
| Products analysed | 4,251 |
| Average elasticity | about -3.25 (elastic demand) |
| Sign accuracy (time-based test) | 0.61 |
| MAE (model) vs baseline (predict 0) | 4.70 vs 3.95 |

The elasticity estimates predict the **direction** of demand change above chance (0.5) but not its **size**, so the advisor uses direction-based rules with a damped scale.

## Sample output

```
Raise price by 9.2% because demand is rising (2.0x recent vs earlier activity)
and item is out of stock. Change is scaled by 0.92 due to price sensitivity
(elasticity -3.25).
```

## Project structure

```
Dynamic-Price-Advisor-System/
|-- app.py                                      # Streamlit app
|-- advisor_data.csv                            # Output of the notebook, read by the app
|-- requirements.txt                            # Python packages
|-- Dynamic Price Advisor System.ipynb          # Data cleaning, elasticity, rules, evaluation
`-- README.md
```

The raw datasets (`online_retail_II.xlsx` and the `Retail Rocket/` folder) are not included because of their size.

## Run locally

```bash
git clone https://github.com/TanmoyMitra2001/Dynamic-Price-Advisor-System.git
cd Dynamic-Price-Advisor-System
pip install -r requirements.txt
streamlit run app.py
```

## Streamlit app

- **Sidebar filters:** demand, stock status, minimum events
- **Item lookup:** pick a group, then an item ID, to see the suggested change, trend, stock and explanation
- **Overview:** summary cards, demand and suggested-change charts, top suggestions table
- **Export:** download the filtered results as CSV

Live app: _add your Streamlit Community Cloud link here_

## Limitations

- The two datasets cannot be joined, so one store-wide elasticity is applied to all items.
- Base price steps, the damping constant and the cap of 2.0 for new items are assumptions.
- The trend counts all event types equally (a view counts the same as a purchase).
- The demand trend itself has not been backtested.

## Future work

- Weight event types (view < add-to-cart < purchase)
- Backtest the demand trend on a held-out future period
- Sensitivity analysis of the assumed parameters
- Per-item elasticity from a dataset that has both price and demand

## Tech stack

Python, pandas, NumPy, matplotlib, Streamlit
