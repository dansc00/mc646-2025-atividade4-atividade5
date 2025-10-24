from datetime import datetime
from src.energy.EnergyManagementSystem import SmartEnergyManagementSystem
from src.energy.DeviceSchedule import DeviceSchedule
from src.energy.EnergyManagementResult import EnergyManagementResult

energy_system = SmartEnergyManagementSystem()

# ==============================================================================
# TESTES DE MODO DE ECONOMIA DE ENERGIA (Regra 1)
# ==============================================================================

def test_tc1_energy_saving_mode_activated_high_price():
    """
    TC1: Verifica se o modo de economia é ativado e dispositivos de baixa 
    prioridade são desligados quando o preço está alto.
    Caminho: current_price > price_threshold → energy_saving_mode = True
    """
    result = energy_system.manage_energy(
        current_price=0.25,
        price_threshold=0.20,
        device_priorities={"Heating": 1, "Lights": 2, "TV": 3},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.energy_saving_mode is True
    assert result.device_status["Lights"] is False   # priority > 1 → OFF
    assert result.device_status["TV"] is False       # priority > 1 → OFF


def test_tc2_energy_saving_mode_not_activated_low_price():
    """
    TC2: Verifica se o modo de economia NÃO é ativado quando o preço está baixo.
    Caminho: current_price <= price_threshold → todos dispositivos ON
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Heating": 1, "Lights": 2, "TV": 3},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.energy_saving_mode is False
    assert result.device_status["Lights"] is True
    assert result.device_status["TV"] is True


# ==============================================================================
# TESTES DE MODO NOTURNO (Regra 2)
# ==============================================================================

def test_tc3_night_mode_active_turns_off_non_essential():
    """
    TC3: Verifica se o modo noturno desliga dispositivos não essenciais (23h-6h).
    Caminho: current_time.hour >= 23 → desliga todos exceto Security/Refrigerator
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Security": 1, "Refrigerator": 1, "Lights": 2, "TV": 3},
        current_time=datetime(2025, 10, 17, 2, 0, 0),  # 2h da manhã
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.device_status["Security"] is True
    assert result.device_status["Refrigerator"] is True
    assert result.device_status["Lights"] is False
    assert result.device_status["TV"] is False


def test_tc4_night_mode_boundary_23h():
    """
    TC4: Testa o limite exato de 23h (início do modo noturno).
    Caminho: current_time.hour == 23 → modo noturno ativo
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Security": 1, "Lights": 2},
        current_time=datetime(2025, 10, 16, 23, 0, 0),  # Exatamente 23h
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.device_status["Security"] is True
    assert result.device_status["Lights"] is False


def test_tc5_night_mode_inactive_daytime():
    """
    TC5: Verifica que o modo noturno NÃO está ativo durante o dia.
    Caminho: current_time.hour between 6-22 → modo noturno inativo
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Security": 1, "Lights": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),  # 14h
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    # Modo noturno inativo, todos dispositivos ligados (preço baixo)
    assert result.device_status["Security"] is True
    assert result.device_status["Lights"] is True


def test_tc6_night_mode_boundary_before_6h():
    """
    TC6: Testa o limite de 5h59 (ainda dentro do modo noturno).
    Caminho: current_time.hour < 6 → modo noturno ativo
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Refrigerator": 1, "TV": 2},
        current_time=datetime(2025, 10, 17, 5, 59, 0),  # 5h59
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.device_status["Refrigerator"] is True
    assert result.device_status["TV"] is False


# ==============================================================================
# TESTES DE REGULAÇÃO DE TEMPERATURA (Regra 3)
# ==============================================================================

def test_tc7_temperature_below_range_activates_heating():
    """
    TC7: Temperatura abaixo do range → ativa aquecimento.
    Caminho: current_temperature < desired_temperature_range[0]
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"TV": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=18.0,  # Abaixo de 20.0
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.temperature_regulation_active is True
    assert result.device_status["Heating"] is True
    assert result.device_status.get("Cooling", False) is False


def test_tc8_temperature_above_range_activates_cooling():
    """
    TC8: Temperatura acima do range → ativa resfriamento.
    Caminho: current_temperature > desired_temperature_range[1]
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"TV": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=26.0,  # Acima de 24.0
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.temperature_regulation_active is True
    assert result.device_status["Cooling"] is True
    assert result.device_status.get("Heating", False) is False


def test_tc9_temperature_within_range_no_regulation():
    """
    TC9: Temperatura dentro do range → não regula.
    Caminho: desired_temperature_range[0] <= temp <= desired_temperature_range[1]
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"TV": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,  # Dentro do range [20.0, 24.0]
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.temperature_regulation_active is False
    assert result.device_status.get("Heating", False) is False
    assert result.device_status.get("Cooling", False) is False


def test_tc10_temperature_at_lower_boundary():
    """
    TC10: Temperatura exatamente no limite inferior → não regula.
    Caminho: current_temperature == desired_temperature_range[0]
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"TV": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=20.0,  # Exatamente no limite inferior
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.temperature_regulation_active is False


def test_tc11_temperature_at_upper_boundary():
    """
    TC11: Temperatura exatamente no limite superior → não regula.
    Caminho: current_temperature == desired_temperature_range[1]
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"TV": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=24.0,  # Exatamente no limite superior
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.temperature_regulation_active is False


# ==============================================================================
# TESTES DE LIMITE DE ENERGIA (Regra 4)
# ==============================================================================

def test_tc12_energy_limit_exceeded_turns_off_low_priority():
    """
    TC12: Limite de energia excedido → desliga dispositivos progressivamente.
    Caminho: total_energy_used_today >= energy_usage_limit → while loop executa
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Heating": 1, "Lights": 2, "TV": 3, "Washer": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=30.0,
        total_energy_used_today=35.0,  # Excedeu o limite
        scheduled_devices=[]
    )
    
    # Pelo menos um dispositivo com priority > 1 foi desligado
    low_priority_count = sum(
        1 for device, status in result.device_status.items()
        if device in ["Lights", "TV", "Washer"] and not status
    )
    assert low_priority_count > 0
    assert result.total_energy_used < 35.0  # Energia diminuiu


def test_tc13_energy_limit_not_exceeded():
    """
    TC13: Limite de energia NÃO excedido → loop não executa.
    Caminho: total_energy_used_today < energy_usage_limit → while não entra
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Heating": 1, "Lights": 2, "TV": 3},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,  # Abaixo do limite
        scheduled_devices=[]
    )
    
    assert result.device_status["Heating"] is False
    assert result.device_status["Lights"] is True
    assert result.device_status["TV"] is True
    assert result.total_energy_used == 25.0  # Não mudou


def test_tc14_energy_limit_no_devices_to_turn_off():
    """
    TC14: Limite excedido mas não há dispositivos de baixa prioridade ligados.
    Caminho: while entra → devices_to_turn_off vazio → devices_were_on = False
    """
    result = energy_system.manage_energy(
        current_price=0.25,  # Preço alto para desligar baixa prioridade
        price_threshold=0.20,
        device_priorities={"Heating": 1, "Cooling": 1},  # Só alta prioridade
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=19.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=10.0,
        total_energy_used_today=15.0,  # Excedeu
        scheduled_devices=[]
    )
    
    # Mesmo com limite excedido, não pode desligar dispositivos de alta prioridade
    assert result.device_status["Heating"] is True


# ==============================================================================
# TESTES DE DISPOSITIVOS AGENDADOS (Regra 5)
# ==============================================================================

def test_tc15_scheduled_device_activated_at_exact_time():
    """
    TC15: Dispositivo agendado é ligado no horário exato.
    Caminho: schedule.scheduled_time == current_time → liga dispositivo
    """
    scheduled_time = datetime(2025, 10, 16, 18, 0, 0)
    
    result = energy_system.manage_energy(
        current_price=0.25,  # Preço alto
        price_threshold=0.20,
        device_priorities={"Oven": 3},  # Baixa prioridade
        current_time=scheduled_time,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[DeviceSchedule("Oven", scheduled_time)]
    )
    
    # Mesmo com preço alto (desligaria por economia), agendamento sobrepõe
    assert result.device_status["Oven"] is True


def test_tc16_scheduled_device_not_activated_wrong_time():
    """
    TC16: Dispositivo agendado NÃO é ligado fora do horário.
    Caminho: schedule.scheduled_time != current_time → não liga
    """
    result = energy_system.manage_energy(
        current_price=0.25,
        price_threshold=0.20,
        device_priorities={"Oven": 3},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[DeviceSchedule("Oven", datetime(2025, 10, 16, 18, 0, 0))]
    )
    
    # Preço alto desliga dispositivo de baixa prioridade
    assert result.device_status["Oven"] is False


def test_tc17_multiple_scheduled_devices():
    """
    TC17: Múltiplos dispositivos agendados, apenas os no horário correto ligam.
    """
    current = datetime(2025, 10, 16, 18, 0, 0)
    
    result = energy_system.manage_energy(
        current_price=0.25,
        price_threshold=0.20,
        device_priorities={"Oven": 3, "Washer": 3, "Dryer": 3},
        current_time=current,
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[
            DeviceSchedule("Oven", current),
            DeviceSchedule("Washer", datetime(2025, 10, 16, 19, 0, 0)),
            DeviceSchedule("Dryer", current)
        ]
    )
    
    assert result.device_status["Oven"] is True    # Horário correto
    assert result.device_status["Washer"] is False # Horário diferente
    assert result.device_status["Dryer"] is True   # Horário correto
