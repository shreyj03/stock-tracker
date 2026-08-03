# project/models.py
# Shrey Jain, shreyj@bu.edu 4/19/2026
# Data models for the stock portfolio tracker application.

from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    """Represents a user profile linked to Django's User model"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='project_profile')
    bio = models.TextField(blank=True)
    profile_image_url = models.URLField(blank=True)

    def __str__(self):
        """Return string representation of the Profile"""
        return self.user.username


class Stock(models.Model):
    """Represents a stock"""

    ticker = models.CharField(max_length=10)
    company_name = models.TextField()
    sector = models.TextField(blank=True)
    exchange = models.TextField(blank=True)

    def __str__(self):
        """Return string representation of the Stock"""
        return f'{self.ticker} - {self.company_name}'


class Watchlist(models.Model):
    """Represents a stock on a user's watchlist."""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='watchlist')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='watched_by')
    date_added = models.DateField(auto_now_add=True)

    def __str__(self):
        """Return string representation of the Watchlist entry"""
        return f'{self.profile.user.username} watching {self.stock.ticker}'


class StockPrice(models.Model):
    """Cached live price for a stock, updated by the fetch_prices ETL command."""
    stock = models.OneToOneField(Stock, on_delete=models.CASCADE, related_name='cached_price')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    change = models.DecimalField(max_digits=10, decimal_places=2)
    change_pct = models.DecimalField(max_digits=6, decimal_places=2)
    fetched_at = models.DateTimeField()

    def __str__(self):
        return f'{self.stock.ticker} @ {self.price}'


class Transaction(models.Model):
    """Represents a buy or sell transaction by a user for a stock."""
    BUY = 'buy'
    SELL = 'sell'
    TRANSACTION_TYPES = [
        (BUY, 'Buy'),
        (SELL, 'Sell'),
    ]
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='transactions')
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.PositiveIntegerField()
    price_per_share = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()

    def __str__(self):
        """Return string representation of the Transaction"""
        return f'{self.profile.user.username} {self.transaction_type} {self.quantity} x {self.stock.ticker}'