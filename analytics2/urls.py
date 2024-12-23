from django.urls import path
from . import views


app_name = "analytics2"
urlpatterns = [
    path('', views.index, name='index'),
    path('stock-analysis/', views.stock_analysis, name='stock_analysis'),
    path('update-investment-style/', views.update_investment_style, name='update_investment_style'),
    path('update-auto-investment/', views.update_auto_investment, name='update_auto_investment'),
    path('update-portfolio-settings/', views.update_portfolio_settings, name='update_portfolio_settings'),
]
