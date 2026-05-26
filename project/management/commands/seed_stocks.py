# project/management/commands/seed_stocks.py
# Shrey Jain, shreyj@bu.edu
# Seeds the Stock table with a curated list of popular stocks.
# Safe to run multiple times — uses get_or_create on the ticker symbol.
#
# Usage:
#   python manage.py seed_stocks               # seed all stocks (default)
#   python manage.py seed_stocks --clear       # wipe existing rows first

from django.core.management.base import BaseCommand
from project.models import Stock

# ---------------------------------------------------------------------------
# Stock data: (ticker, company_name, sector, exchange)
# ---------------------------------------------------------------------------
STOCKS = [
    # Technology
    ("AAPL",  "Apple Inc.",                      "Technology",          "NASDAQ"),
    ("MSFT",  "Microsoft Corporation",            "Technology",          "NASDAQ"),
    ("GOOGL", "Alphabet Inc.",                    "Technology",          "NASDAQ"),
    ("META",  "Meta Platforms Inc.",              "Technology",          "NASDAQ"),
    ("NVDA",  "NVIDIA Corporation",              "Technology",          "NASDAQ"),
    ("AMD",   "Advanced Micro Devices Inc.",      "Technology",          "NASDAQ"),
    ("INTC",  "Intel Corporation",               "Technology",          "NASDAQ"),
    ("ORCL",  "Oracle Corporation",              "Technology",          "NYSE"),
    ("CRM",   "Salesforce Inc.",                 "Technology",          "NYSE"),
    ("ADBE",  "Adobe Inc.",                      "Technology",          "NASDAQ"),
    ("QCOM",  "Qualcomm Incorporated",           "Technology",          "NASDAQ"),
    ("TXN",   "Texas Instruments Incorporated",  "Technology",          "NASDAQ"),

    # Consumer Discretionary / E-commerce
    ("AMZN",  "Amazon.com Inc.",                 "Consumer Discretionary", "NASDAQ"),
    ("TSLA",  "Tesla Inc.",                      "Consumer Discretionary", "NASDAQ"),
    ("NKE",   "Nike Inc.",                       "Consumer Discretionary", "NYSE"),
    ("MCD",   "McDonald's Corporation",          "Consumer Discretionary", "NYSE"),
    ("SBUX",  "Starbucks Corporation",           "Consumer Discretionary", "NASDAQ"),
    ("HD",    "The Home Depot Inc.",             "Consumer Discretionary", "NYSE"),

    # Financials
    ("JPM",   "JPMorgan Chase & Co.",            "Financials",          "NYSE"),
    ("BAC",   "Bank of America Corporation",     "Financials",          "NYSE"),
    ("GS",    "The Goldman Sachs Group Inc.",    "Financials",          "NYSE"),
    ("MS",    "Morgan Stanley",                  "Financials",          "NYSE"),
    ("V",     "Visa Inc.",                       "Financials",          "NYSE"),
    ("MA",    "Mastercard Incorporated",         "Financials",          "NYSE"),
    ("BRK-B", "Berkshire Hathaway Inc.",         "Financials",          "NYSE"),
    ("WFC",   "Wells Fargo & Company",           "Financials",          "NYSE"),

    # Healthcare
    ("JNJ",   "Johnson & Johnson",              "Healthcare",           "NYSE"),
    ("UNH",   "UnitedHealth Group Incorporated","Healthcare",           "NYSE"),
    ("PFE",   "Pfizer Inc.",                    "Healthcare",           "NYSE"),
    ("ABBV",  "AbbVie Inc.",                    "Healthcare",           "NYSE"),
    ("MRK",   "Merck & Co. Inc.",               "Healthcare",           "NYSE"),
    ("LLY",   "Eli Lilly and Company",          "Healthcare",           "NYSE"),
    ("TMO",   "Thermo Fisher Scientific Inc.",  "Healthcare",           "NYSE"),

    # Energy
    ("XOM",   "Exxon Mobil Corporation",        "Energy",               "NYSE"),
    ("CVX",   "Chevron Corporation",            "Energy",               "NYSE"),
    ("COP",   "ConocoPhillips",                 "Energy",               "NYSE"),

    # Communication Services
    ("NFLX",  "Netflix Inc.",                   "Communication Services", "NASDAQ"),
    ("DIS",   "The Walt Disney Company",        "Communication Services", "NYSE"),
    ("T",     "AT&T Inc.",                      "Communication Services", "NYSE"),
    ("VZ",    "Verizon Communications Inc.",    "Communication Services", "NYSE"),
    ("CMCSA", "Comcast Corporation",            "Communication Services", "NASDAQ"),

    # Consumer Staples
    ("PG",    "Procter & Gamble Co.",           "Consumer Staples",     "NYSE"),
    ("KO",    "The Coca-Cola Company",          "Consumer Staples",     "NYSE"),
    ("PEP",   "PepsiCo Inc.",                   "Consumer Staples",     "NASDAQ"),
    ("WMT",   "Walmart Inc.",                   "Consumer Staples",     "NYSE"),
    ("COST",  "Costco Wholesale Corporation",   "Consumer Staples",     "NASDAQ"),

    # Industrials
    ("BA",    "The Boeing Company",             "Industrials",          "NYSE"),
    ("CAT",   "Caterpillar Inc.",               "Industrials",          "NYSE"),
    ("GE",    "GE Aerospace",                   "Industrials",          "NYSE"),
    ("HON",   "Honeywell International Inc.",   "Industrials",          "NASDAQ"),
    ("UPS",   "United Parcel Service Inc.",     "Industrials",          "NYSE"),

    # Real Estate / Other
    ("SPG",   "Simon Property Group Inc.",      "Real Estate",          "NYSE"),
    ("AMT",   "American Tower Corporation",     "Real Estate",          "NYSE"),
]


class Command(BaseCommand):
    help = (
        "Seed the Stock table with a curated list of popular stocks. "
        "Safe to re-run — existing rows are skipped."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete all existing Stock rows before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            deleted, _ = Stock.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Cleared {deleted} existing stock(s)."))

        created_count = 0
        skipped_count = 0

        for ticker, company_name, sector, exchange in STOCKS:
            _, created = Stock.objects.get_or_create(
                ticker=ticker,
                defaults={
                    'company_name': company_name,
                    'sector': sector,
                    'exchange': exchange,
                },
            )
            if created:
                created_count += 1
                self.stdout.write(f"  + {ticker:8s} {company_name}")
            else:
                skipped_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_count} stock(s), skipped {skipped_count} existing."
            )
        )
