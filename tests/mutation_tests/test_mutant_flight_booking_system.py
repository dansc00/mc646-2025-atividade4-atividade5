import pytest
from datetime import datetime
from src.flight.FlightBookingSystem import FlightBookingSystem
from src.flight.BookingResult import BookingResult

@pytest.fixture
def flight_system():
    """Configura uma instância do FlightBookingSystem para os testes."""
    return FlightBookingSystem()

def test_mutant75_insufficient_seats_and_confirmation_None(flight_system):
    """
    Teste com passageiros (10) excedendo assentos disponíveis (2).
    Deve retornar confirmação False com preços zerados.
    Mata mutante 75, que define confirmation = None
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
    
    assert not result.confirmation and result.confirmation is not None
    assert result.total_price == 0.0
    assert result.refund_amount == 0.0
    assert not result.points_used

def test_mutant77_insufficient_seats_and_points_used_None(flight_system):
    """
    Teste com passageiros (10) excedendo assentos disponíveis (2).
    Deve retornar confirmação False, pontos usados False, com preços zerados.
    Mata mutante 77, que define points_used = None
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
    assert not result.points_used and result.points_used is not None

def test_mutant77_reward_points_used_0_points_used_None(flight_system):
    """
    Teste com pontos de recompensa 0.
    Deve retornar pontos usados False.
    Mata mutante 77, que define points_used = None
    """
    result = flight_system.book_flight(
        passengers=1,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 19, 12, 0, 0),
        reward_points_available=0
    )
    
    assert result.confirmation
    assert result.total_price > 0.0
    assert result.refund_amount == 0.0
    assert not result.points_used and result.points_used is not None

def test_mutant78_equal_passengers_and_seats(flight_system):
    """
    Teste com passageiros igual aos assentos disponíveis (5 == 5).
    Deve retornar confirmação True com preço calculado.
    Mata mutante 78, que altera a condição para passengers >= availavle_seats
    """
    result = flight_system.book_flight(
        passengers=5,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=5,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 19, 12, 0, 0),
        reward_points_available=0
    )
    
    assert result.confirmation
    assert result.total_price > 0.0

def test_mutant90_mutant92_mutant93_exactly_24_hours_departure(flight_system):
    """
    Teste com exatamente 24 horas de antecedência.
    Mata mutante 90 e 92, que alteram o cálculo de hours_to_departure
    Mata mutante 92, que altera a condição para hours_to_departure <= 24
    Mata mutante 93, que altera a condição para hours_to_departure < 25
    """
    result = flight_system.book_flight(
        passengers=1,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 17, 12, 0, 0),  
        reward_points_available=0
    )
    
    # Cálculos esperados (código original):
    # price_factor = (100 / 100.0) * 0.8 = 0.8
    # base_price = 100.0 * 0.8 * 1 = 80.0
    # hours_to_departure = 24.0, então 24.0 < 24 é False
    # SEM taxa de última hora
    # final_price = 80.0
    
    assert result.confirmation
    assert result.total_price == 80.0  
    assert result.refund_amount == 0.0
    assert not result.points_used

def test_mutant97_exactly_4_passengers(flight_system):
    """
    Teste com exatamente 4 passageiros.
    Mata mutante 97, que altera a condição para passengers >= 4
    """
    result = flight_system.book_flight(
        passengers=4,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 19, 12, 0, 0),
        reward_points_available=0
    )
    
    # Cálculos esperados (código original):
    # price_factor = (100 / 100.0) * 0.8 = 0.8
    # final_price = 100.0 * 0.8 * 4 = 320.0
    # passengers > 4 é False, então SEM desconto de 5%
    # final_price = 320.0
    
    assert result.confirmation
    assert result.total_price == 320.0  

def test_mutant103_points_used_1(flight_system):
    """
    Teste com pontos de recompensa exatamente igual a 1.
    Mata mutante 103, que altera a condição para reward_points_available > 1
    """
    result = flight_system.book_flight(
        passengers=1,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 19, 12, 0, 0),
        reward_points_available=1
    )
    
    assert result.confirmation
    assert result.points_used

def test_mutant111_final_price_0_point_5(flight_system):
    """
    Teste onde o preço final calculado é exatamente 0.5.
    Mata mutante 111, que altera a condição para final_price < 1
    """
    result = flight_system.book_flight(
        passengers=1,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=0.625,
        previous_sales=100,
        is_cancellation=False,
        departure_time=datetime(2025, 10, 19, 12, 0, 0),
        reward_points_available=0
    )
    
    assert result.confirmation
    assert result.total_price == 0.5

def test_mutant114_mutant115_exactly_48_hours_departure_and_is_cancellation_true(flight_system):
    """
    Teste com exatamente 48 horas de antecedência para cancelamento.
    Mata mutante 114, que altera a condição para hours_to_departure > 48
    Mata mutante 115, que altera a condição para hours_to_departure >= 49
    """
    result = flight_system.book_flight(
        passengers=1,
        booking_time=datetime(2025, 10, 16, 12, 0, 0),
        available_seats=10,
        current_price=100.0,
        previous_sales=100,
        is_cancellation=True,
        departure_time=datetime(2025, 10, 18, 12, 0, 0),  
        reward_points_available=0
    )
    
    # Cálculos esperados (código original):
    # price_factor = (100 / 100.0) * 0.8 = 0.8
    # final_price = 100.0 * 0.8 * 1 = 80.0
    # hours_to_departure = 48.0, então 48.0 >= 48 é True
    # refund_amount = final_price = 80.0
    
    assert not result.confirmation
    assert result.total_price == 0.0  
    assert result.refund_amount == 80.0  
    assert not result.points_used
