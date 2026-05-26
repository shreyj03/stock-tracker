# project/views.py
# Shrey Jain, shreyj@bu.edu, 4/27/2026
# Views for the stock portfolio tracker application.

from django.shortcuts import render
from django.views.generic import ListView, DetailView, TemplateView
from .models import Profile, Stock, Watchlist, Transaction
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse_lazy
import yfinance as yf
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django import forms
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin
import pandas as pd
from datetime import date




class MainPageView(TemplateView):
    """Display the main landing page with market overview."""
    template_name = 'project/main.html'

    def get_context_data(self, **kwargs):
        """Add top stocks with live prices to the landing page."""
        context = super().get_context_data(**kwargs)
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'JPM']
        market_data = []
        for t in tickers:
            try:
                stock_obj = Stock.objects.get(ticker=t)
                ticker = yf.Ticker(t)
                info = ticker.fast_info
                live_price = round(info.last_price, 2)
                change = round(info.last_price - info.previous_close, 2)
                change_pct = round(change / info.previous_close * 100, 2)
                market_data.append({
                    'ticker': t,
                    'pk': stock_obj.pk,
                    'price': live_price,
                    'change': change,
                    'change_pct': change_pct,
                })
            except:
                pass
        context['market_data'] = market_data

        # portfolio summary for logged in user
        if self.request.user.is_authenticated:
            try:
                profile = self.request.user.project_profile
                transactions = profile.transactions.all()
                total_invested = 0
                total_current_value = 0
                for t in transactions:
                    try:
                        ticker = yf.Ticker(t.stock.ticker)
                        live_price = ticker.fast_info.last_price
                        cost = float(t.price_per_share) * t.quantity
                        current_value = live_price * t.quantity
                        if t.transaction_type == 'buy':
                            total_invested += cost
                            total_current_value += current_value
                    except:
                        pass
                context['total_invested'] = round(total_invested, 2)
                context['total_current_value'] = round(total_current_value, 2)
                context['total_pnl'] = round(total_current_value - total_invested, 2)
            except:
                pass
        return context


class StockListView(ListView):
    """Display a list of all stocks with search and sector filtering."""
    model = Stock
    template_name = 'project/stock_list.html'
    context_object_name = 'stocks'

    def get_queryset(self):
        """Filter stocks by search query and/or sector."""
        queryset = Stock.objects.all()
        query = self.request.GET.get('q')
        sector = self.request.GET.get('sector')
        if query:
            queryset = queryset.filter(
                models.Q(ticker__icontains=query) |
                models.Q(company_name__icontains=query)
            )
        if sector:
            queryset = queryset.filter(sector=sector)
        return queryset

    def get_context_data(self, **kwargs):
        """Add list of sectors and current filters to context."""
        context = super().get_context_data(**kwargs)
        context['sectors'] = Stock.objects.values_list('sector', flat=True).distinct().order_by('sector')
        context['current_q'] = self.request.GET.get('q', '')
        context['current_sector'] = self.request.GET.get('sector', '')
        return context


class StockDetailView(DetailView):
    """Display details for a single stock including live price data."""
    model = Stock
    template_name = 'project/stock_detail.html'
    context_object_name = 'stock'

    def get_context_data(self, **kwargs):
        """Add live price and historical chart data from yfinance to the context."""
        context = super().get_context_data(**kwargs)
        try:
            ticker = yf.Ticker(self.object.ticker)
            info = ticker.fast_info
            context['live_price'] = round(info.last_price, 2)
            context['price_change'] = round(info.last_price - info.previous_close, 2)
            context['price_change_pct'] = round((info.last_price - info.previous_close) / info.previous_close * 100, 2)

            # get 6 months of historical data
            hist = ticker.history(period='6mo')
            context['chart_dates'] = list(hist.index.strftime('%Y-%m-%d'))
            context['chart_prices'] = [round(p, 2) for p in hist['Close'].tolist()]
        except:
            context['live_price'] = None
            context['price_change'] = None
            context['price_change_pct'] = None
            context['chart_dates'] = []
            context['chart_prices'] = []
        return context


class ProfileDetailView(DetailView):
    """Display details for a single profile."""
    model = Profile
    template_name = 'project/profile_detail.html'
    context_object_name = 'profile'

    def get_context_data(self, **kwargs):
        """Add P&L data for each transaction using live prices from yfinance."""
        context = super().get_context_data(**kwargs)
        transactions = self.object.transactions.all()
        transaction_data = []
        total_invested = 0
        total_current_value = 0

        for t in transactions:
            # try:
            ticker = yf.Ticker(t.stock.ticker)
            live_price = round(ticker.fast_info.last_price, 2)
            cost = round(float(t.price_per_share) * t.quantity, 2)
            current_value = round(live_price * t.quantity, 2)
            pnl = round(current_value - cost, 2)
            if t.transaction_type == 'buy':
                total_invested += cost
                total_current_value += current_value
            # except:
            #     live_price = None
            #     pnl = None
            #     cost = None
            #     current_value = None
            transaction_data.append({
                'transaction': t,
                'live_price': live_price,
                'pnl': pnl,
            })

        watchlist_prices = {}
        for w in self.object.watchlist.all():
            try:
                ticker = yf.Ticker(w.stock.ticker)
                watchlist_prices[w.stock.ticker] = round(ticker.fast_info.last_price, 2)
            except:
                watchlist_prices[w.stock.ticker] = None

        # portfolio value over time chart
        try:
            transactions = self.object.transactions.filter(transaction_type='buy')
            if transactions.exists():
                earliest_date = transactions.order_by('date').first().date

                # get historical prices for each stock in portfolio
                holdings = {}
                for t in transactions:
                    if t.stock.ticker not in holdings:
                        holdings[t.stock.ticker] = []
                    holdings[t.stock.ticker].append({
                        'quantity': t.quantity,
                        'date': t.date,
                    })

                # build daily portfolio value from earliest transaction to today
                date_range = pd.date_range(start=earliest_date, end=date.today(), freq='B')  # business days
                portfolio_values = []
                chart_dates = []

                for ticker_str, buys in holdings.items():
                    hist = yf.Ticker(ticker_str).history(start=str(earliest_date), end=str(date.today()))
                    for d in date_range:
                        date_str = d.strftime('%Y-%m-%d')
                        total_shares = sum(b['quantity'] for b in buys if b['date'] <= d.date())
                        if total_shares > 0 and date_str in hist.index.strftime('%Y-%m-%d').tolist():
                            idx = hist.index.strftime('%Y-%m-%d').tolist().index(date_str)
                            price = hist['Close'].iloc[idx]
                            # accumulate value for this date
                            if date_str not in chart_dates:
                                chart_dates.append(date_str)
                                portfolio_values.append(float(round(total_shares * price, 2)))
                            else:
                                i = chart_dates.index(date_str)
                                portfolio_values[i] += float(round(total_shares * price, 2))

                context['portfolio_chart_dates'] = chart_dates
                context['portfolio_chart_values'] = portfolio_values
            else:
                context['portfolio_chart_dates'] = []
                context['portfolio_chart_values'] = []
        except:
            context['portfolio_chart_dates'] = []
            context['portfolio_chart_values'] = []

        context['watchlist_prices'] = watchlist_prices
        context['watchlist_prices'] = watchlist_prices
        context['transaction_data'] = transaction_data
        context['total_invested'] = round(total_invested, 2)
        context['total_current_value'] = round(total_current_value, 2)
        context['total_pnl'] = round(total_current_value - total_invested, 2)
        return context


class WatchlistDetailView(DetailView):
    """Display details for a single watchlist entry."""
    model = Watchlist
    template_name = 'project/watchlist_detail.html'
    context_object_name = 'watchlist'


class TransactionDetailView(DetailView):
    """Display details for a single transaction."""
    model = Transaction
    template_name = 'project/transaction_detail.html'
    context_object_name = 'transaction'

class RegisterView(FormView):
    """Handle user registration."""
    template_name = 'project/register.html'
    form_class = UserCreationForm
    success_url = reverse_lazy('main')

    def form_valid(self, form):
        """Save the new user, create their profile, and log them in."""
        user = form.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        messages.success(self.request, 'Account created successfully. Welcome!')
        return super().form_valid(form)

class TransactionForm(forms.ModelForm):
    """Form for logging a buy or sell transaction."""
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Transaction
        fields = ['stock', 'transaction_type', 'quantity', 'price_per_share', 'date']

class AddTransactionView(LoginRequiredMixin, CreateView):
    """Allow a logged-in user to log a new transaction."""
    model = Transaction
    form_class = TransactionForm
    template_name = 'project/add_transaction.html'

    def form_valid(self, form):
        """Attach the current user's profile to the transaction before saving."""
        form.instance.profile = self.request.user.project_profile
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect to the user's profile after logging a transaction."""
        return reverse_lazy('profile-detail', kwargs={'pk': self.request.user.project_profile.pk})

class DeleteTransactionView(LoginRequiredMixin, DeleteView):
    """Allow a user to delete a transaction."""
    model = Transaction
    template_name = 'project/delete_transaction.html'

    def get_success_url(self):
        """Redirect to profile after deleting a transaction."""
        return reverse_lazy('profile-detail', kwargs={'pk': self.request.user.project_profile.pk})


class EditProfileView(LoginRequiredMixin, UpdateView):
    """Allow a user to edit their profile."""
    model = Profile
    template_name = 'project/edit_profile.html'
    fields = ['bio', 'profile_image_url']

    def get_success_url(self):
        """Redirect to profile after editing."""
        return reverse_lazy('profile-detail', kwargs={'pk': self.object.pk})

class AddToWatchlistView(LoginRequiredMixin, CreateView):
    """Allow a logged-in user to add a stock to their watchlist."""
    model = Watchlist
    fields = []
    template_name = 'project/add_watchlist.html'

    def form_valid(self, form):
        """Attach the current user's profile and stock to the watchlist entry."""
        form.instance.profile = self.request.user.project_profile
        form.instance.stock = Stock.objects.get(pk=self.kwargs['stock_pk'])
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Add the stock to the template context."""
        context = super().get_context_data(**kwargs)
        context['stock'] = Stock.objects.get(pk=self.kwargs['stock_pk'])
        return context

    def get_success_url(self):
        """Redirect to profile after adding to watchlist."""
        return reverse_lazy('profile-detail', kwargs={'pk': self.request.user.project_profile.pk})

class DeleteWatchlistView(LoginRequiredMixin, DeleteView):
    """Allow a user to remove a stock from their watchlist."""
    model = Watchlist
    template_name = 'project/delete_watchlist.html'

    def get_success_url(self):
        """Redirect to profile after removing from watchlist."""
        return reverse_lazy('profile-detail', kwargs={'pk': self.request.user.project_profile.pk})
