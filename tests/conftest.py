# Pytest configuration and fixtures for EBMS

import pytest
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

@pytest.fixture(scope='session')
def app_config():
    """Application configuration for testing"""
    from config.config import TestingConfig
    return TestingConfig


@pytest.fixture(scope='session')
def app(app_config):
    """Create application for testing"""
    # This will be populated when Flask app is created
    pass


@pytest.fixture
def db():
    """Database session for tests"""
    # This will be set up with SQLAlchemy
    pass


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Flask CLI runner for testing CLI commands"""
    return app.test_cli_runner()


@pytest.fixture
def auth_headers(client):
    """Get authorization headers with valid JWT token"""
    # This will generate a test JWT token
    pass


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        'email': 'test@example.com',
        'password': 'TestPassword123!',
        'name': 'Test User',
        'account_type': 'residential'
    }


@pytest.fixture
def sample_bill_data():
    """Sample bill data for testing"""
    return {
        'usage_kwh': 5000,
        'billing_period': '2024-01',
        'status': 'pending',
        'amount': 1500.50
    }


@pytest.fixture
def sample_payment_data():
    """Sample payment data for testing"""
    return {
        'amount': 1500.50,
        'method': 'credit_card',
        'reference': 'TXN_123456'
    }


# Markers for pytest
def pytest_configure(config):
    """Register custom markers"""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database"
    )
    config.addinivalue_line(
        "markers", "api: mark test as API endpoint test"
    )
