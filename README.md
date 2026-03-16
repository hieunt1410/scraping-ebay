# Scraping eBay

Scrapes eBay product listings and seller profiles using [Scrapy](https://scrapy.org/) + [scrapy-playwright](https://github.com/scrapy-plugins/scrapy-playwright) (headless Chromium) to bypass eBay's JS challenge pages.

Output is split into two files:
- **`data/products.json`** — one entry per product listing
- **`data/sellers.json`** — one entry per unique seller

## Setup

Requires Python 3.12+.

```bash
pip install -r requirements.txt
playwright install chromium
```

## Usage

### Step 1 — Crawl products

```bash
scrapy crawl ebay
```

Output: `data/products.json`

To search for a different keyword (default is *nintendo switch console*):

```bash
scrapy crawl ebay -a search="xbox one x"
```

### Step 2 — Crawl sellers

Reads the seller names from `data/products.json` and visits each seller's eBay profile page.

```bash
scrapy crawl sellers
```

Output: `data/sellers.json`

## Product fields

| Field | Description |
|---|---|
| `ID` | eBay item ID extracted from the URL |
| `Name` | Product title |
| `Status` | Condition (e.g. Pre-Owned) |
| `Price` | Listed price |
| `URL` | Product page URL |
| `UPC` | UPC / GTIN-13 if available |
| `Item_Specifics` | Key-value pairs from the Item Specifics section |
| `Seller_Name` | Seller username |
| `Store_Categories` | Categories listed in the seller's store |
| `Feedback_This_Item` | Number of feedback entries for this specific listing |
| `Feedback_All_Items` | Total seller feedback count |
| `Feedback_Topics_This_Item` | AI-summarised feedback topics for this listing |
| `Feedback_Topics_All_Items` | AI-summarised feedback topics for all seller items |

## Seller fields

| Field | Description |
|---|---|
| `Seller_Name` | Seller username |
| `Seller_Feedback_Score` | Total feedback score |
| `Seller_Positive_Feedback` | Positive feedback percentage |
| `Seller_Items_Sold` | Number of items sold |
| `Seller_Detailed_Ratings` | DSR ratings (description, shipping cost, speed, communication) |
| `Feedback_Total` | Total feedback count shown on seller card |

## Optional: CaptchaAI integration

If eBay serves a reCAPTCHA page, set your [CaptchaAI](https://captchaai.com) API key to enable automatic solving:

```bash
export CAPTCHAAI_API_KEY=your_key_here
scrapy crawl ebay
```
