from django.urls import path
from .views import DashboardView, QuickActionsView

urlpatterns = [
    path('', DashboardView.as_view(), name='dashboard'),
    path('quick-actions/', QuickActionsView.as_view(), name='quick_actions'),
]