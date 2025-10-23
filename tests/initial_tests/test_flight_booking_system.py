import pytest
from datetime import datetime
from src.flight.FlightBookingSystem import FlightBookingSystem
from src.flight.BookingResult import BookingResult

@pytest.fixture
def flight_system():
    """Configura uma instância do FlightBookingSystem para os testes."""
    return FlightBookingSystem()


def test_case_c1_insufficient_seats(flight_system):
    """
    C1: Teste com passageiros (10) excedendo assentos disponíveis (2).
    Deve retornar confirmação False com preços zerados.
    """
    result = flight_system.book_flight(
        passengers=10,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=2,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 19, 12, 0, 0),
        reward_points_available=0
    )
    
    assert not result.confirmation
    assert result.total_price == 0.0
    assert result.refund_amount == 0.0
    assert not result.points_used


def test_case_c2_with_reward_points_and_last_minute(flight_system):
    """
    C2: Reserva com pontos de recompensa (20000) e taxa de última hora.
    Departure em 8 horas (taxa aplicada), com desconto de pontos.
    """
    result = flight_system.book_flight(
        passengers=5,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=50,
        current_price=1.0,
        previous_sales=1,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 16, 20, 0, 0),
        reward_points_available=20000
    )
    
    # Cálculos esperados:
    # price_factor = (1 / 100.0) * 0.8 = 0.008
    # base_price = 1.0 * 0.008 * 5 = 0.04
    # + taxa última hora (< 24h) = 0.04 + 100 = 100.04
    # - desconto pontos = 100.04 - (20000 * 0.01) = 100.04 - 200 = -99.96 → 0 (não negativo)
    
    assert result.confirmation
    assert result.total_price == 0.0
    assert result.refund_amount == 0.0
    assert result.points_used


def test_case_c3_cancellation_with_full_refund(flight_system):
    """
    C3: Cancelamento com mais de 48 horas de antecedência (reembolso total).
    Departure em 72 horas.
    """
    result = flight_system.book_flight(
        passengers=5,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=50,
        current_price=10.0,
        previous_sales=10,
        is_cancellation=True,
        departure_time=datetime(2025, 10, 19, 12, 0, 0),
        reward_points_available=500
    )
    
    # Cálculos do preço original:
    # price_factor = (10 / 100.0) * 0.8 = 0.08
    # base_price = 10.0 * 0.08 * 5 = 4.0
    # Sem taxa última hora (> 24h)
    # - desconto pontos = 4.0 - (500 * 0.01) = 4.0 - 5 = -1 → 0
    # Cancelamento com >= 48h: reembolso total = 0
    
    assert not result.confirmation
    assert result.total_price == 0.0
    assert result.refund_amount == 0.0
    assert not result.points_used


def test_case_c4_last_minute_with_points(flight_system):
    """
    C4: Reserva de última hora (6 horas) com pontos de recompensa.
    """
    result = flight_system.book_flight(
        passengers=1,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=10.0,
        previous_sales=10,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 16, 18, 0, 0),
        reward_points_available=20000
    )
    
    # Cálculos esperados:
    # price_factor = (10 / 100.0) * 0.8 = 0.08
    # base_price = 10.0 * 0.08 * 1 = 0.8
    # + taxa última hora (< 24h) = 0.8 + 100 = 100.8
    # - desconto pontos = 100.8 - (20000 * 0.01) = 100.8 - 200 = -99.2 → 0
    
    assert result.confirmation
    assert result.total_price == 0.0
    assert result.refund_amount == 0.0
    assert result.points_used


def test_case_c5_group_discount_last_minute(flight_system):
    """
    C5: Reserva em grupo (5 pessoas) com desconto de 5% e taxa de última hora.
    """
    result = flight_system.book_flight(
        passengers=5,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 16, 18, 0, 0),
        reward_points_available=0
    )
    
    # Cálculos esperados:
    # price_factor = (100 / 100.0) * 0.8 = 0.8
    # base_price = 100.0 * 0.8 * 5 = 400.0
    # + taxa última hora (< 24h) = 400.0 + 100 = 500.0
    # desconto grupo (> 4 passageiros) = 500.0 * 0.95 = 475.0
    
    assert result.confirmation
    assert result.total_price == 475.0
    assert result.refund_amount == 0.0
    assert not result.points_used


def test_case_c6_cancellation_partial_refund(flight_system):
    """
    C6: Cancelamento com menos de 48 horas (reembolso parcial de 50%).
    """
    result = flight_system.book_flight(
        passengers=5,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=True,
        departure_time=datetime(2025, 10, 16, 18, 0, 0),
        reward_points_available=1000
    )
    
    # Cálculos do preço original:
    # price_factor = (100 / 100.0) * 0.8 = 0.8
    # base_price = 100.0 * 0.8 * 5 = 400.0
    # + taxa última hora (< 24h) = 400.0 + 100 = 500.0
    # desconto grupo (> 4 passageiros) = 500.0 * 0.95 = 475.0
    # - desconto pontos = 475.0 - (1000 * 0.01) = 475.0 - 10 = 465.0
    # Cancelamento com < 48h: reembolso 50% = 465.0 * 0.5 = 232.5
    
    assert not result.confirmation
    assert result.total_price == 0.0
    assert result.refund_amount == 232.5
    assert not result.points_used