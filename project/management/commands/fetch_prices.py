import os
from django.core.management.base import BaseCommand
from django.utils import timezone
from project.models import Stock, StockPrice
import yfinance as yf
import snowflake.connector


class Command(BaseCommand):
    help = 'Fetch live prices for all stocks, update the StockPrice cache, and append to Snowflake'

    def handle(self, *args, **options):
        stocks = list(Stock.objects.all())
        rows = []

        for stock in stocks:
            try:
                info = yf.Ticker(stock.ticker).fast_info
                price = round(info.last_price, 2)
                change = round(info.last_price - info.previous_close, 2)
                change_pct = round(change / info.previous_close * 100, 2)
                rows.append((stock, price, change, change_pct))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  skipped {stock.ticker}: {e}'))

        # Load → PostgreSQL
        for stock, price, change, change_pct in rows:
            StockPrice.objects.update_or_create(
                stock=stock,
                defaults={
                    'price': price,
                    'change': change,
                    'change_pct': change_pct,
                    'fetched_at': timezone.now(),
                }
            )
        self.stdout.write(f'Postgres: updated {len(rows)} rows')

        # Load → Snowflake
        sf_account = os.environ.get('SNOWFLAKE_ACCOUNT')
        if not sf_account:
            self.stdout.write(self.style.WARNING('SNOWFLAKE_ACCOUNT not set — skipping Snowflake load'))
            self.stdout.write(self.style.SUCCESS(f'Done — {len(rows)} stocks fetched'))
            return

        try:
            conn = snowflake.connector.connect(
                account=sf_account,
                user=os.environ['SNOWFLAKE_USER'],
                password=os.environ['SNOWFLAKE_PASSWORD'],
                database=os.environ.get('SNOWFLAKE_DATABASE', 'STOCK_TRACKER'),
                schema=os.environ.get('SNOWFLAKE_SCHEMA', 'PUBLIC'),
                warehouse=os.environ.get('SNOWFLAKE_WAREHOUSE', 'STOCK_TRACKER_WH'),
            )
            cur = conn.cursor()
            fetched_at = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            cur.executemany(
                "INSERT INTO PRICE_HISTORY (ticker, price, change, change_pct, fetched_at) VALUES (%s, %s, %s, %s, %s)",
                [(stock.ticker, price, change, change_pct, fetched_at) for stock, price, change, change_pct in rows]
            )
            conn.close()
            self.stdout.write(f'Snowflake: appended {len(rows)} rows')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Snowflake load failed: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Done — {len(rows)} stocks fetched'))
