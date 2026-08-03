from django.core.management.base import BaseCommand
from django.utils import timezone
from project.models import Stock, StockPrice
import yfinance as yf


class Command(BaseCommand):
    help = 'Fetch live prices for all stocks and update the StockPrice cache'

    def handle(self, *args, **options):
        stocks = list(Stock.objects.all())
        updated = 0
        failed = 0

        for stock in stocks:
            try:
                info = yf.Ticker(stock.ticker).fast_info
                price = round(info.last_price, 2)
                change = round(info.last_price - info.previous_close, 2)
                change_pct = round(change / info.previous_close * 100, 2)

                StockPrice.objects.update_or_create(
                    stock=stock,
                    defaults={
                        'price': price,
                        'change': change,
                        'change_pct': change_pct,
                        'fetched_at': timezone.now(),
                    }
                )
                updated += 1
            except Exception as e:
                failed += 1
                self.stdout.write(self.style.WARNING(f'  skipped {stock.ticker}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Done — {updated} updated, {failed} failed'))
