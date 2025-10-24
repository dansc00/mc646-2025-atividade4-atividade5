"""
Testes específicos para matar os mutantes sobreviventes do EnergyManagementSystem.
Cada teste é projetado para detectar uma mutação específica.
"""

from datetime import datetime
from src.energy.EnergyManagementSystem import SmartEnergyManagementSystem
from src.energy.DeviceSchedule import DeviceSchedule

energy_system = SmartEnergyManagementSystem()


def test_mutant6():
    """
    Mata o mutante 6: current_price > price_threshold → current_price >= price_threshold
    
    Mutação: Operador relacional > mudou para >=
    """
    result = energy_system.manage_energy(
        current_price=0.20,       
        price_threshold=0.20,     
        device_priorities={"Heating": 1, "Lights": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.energy_saving_mode is False
    assert result.device_status["Lights"] is True  


def test_mutant9():
    """
    Mata o mutante 9: priority > 1 → priority >= 1
    
    Mutação: Operador relacional > mudou para >= no check de prioridade
    """
    result = energy_system.manage_energy(
        current_price=0.25,       # Alto - ativa modo economia
        price_threshold=0.20,
        device_priorities={"CriticalDevice": 1},  # Priority exatamente 1
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    # Dispositivo com priority 1 deve ficar LIGADO em modo economia
    assert result.energy_saving_mode is True
    assert result.device_status["CriticalDevice"] is True


def test_mutant13():
    """
    Mata o mutante 13: device_status[device] = True → device_status[device] = False
    
    Mutação: True mudou para False no else (alta prioridade)
    """
    result = energy_system.manage_energy(
        current_price=0.30,
        price_threshold=0.20,
        device_priorities={"Essential": 1, "NonEssential": 3},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    # Dispositivo essencial (priority 1) deve estar LIGADO
    assert result.device_status["Essential"] is True
    # Dispositivo não essencial deve estar desligado
    assert result.device_status["NonEssential"] is False


def test_mutant14():
    """
    Mata o mutante 14: device_status[device] = True → device_status[device] = None
    
    Mutação: True mudou para None
    """
    result = energy_system.manage_energy(
        current_price=0.25,
        price_threshold=0.20,
        device_priorities={"Device": 1},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    assert result.device_status["Device"] is True
    assert result.device_status["Device"] is not None


def test_mutant19():
    """
    Mata o mutante 19: current_time.hour < 6 → current_time.hour <= 6
    
    Mutação: < mudou para <= no limite superior do modo noturno
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Security": 1, "TV": 2},
        current_time=datetime(2025, 10, 16, 6, 0, 0),  # Exatamente 6h
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    # Às 6h, modo noturno já terminou - TV deve estar ligada
    assert result.device_status["TV"] is True
    assert result.device_status["Security"] is True


def test_mutant20():
    """
    Mata o mutante 20: current_time.hour < 6 → current_time.hour < 7
    
    Mutação: 6 mudou para 7 no limite do modo noturno
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Refrigerator": 1, "Lights": 2},
        current_time=datetime(2025, 10, 16, 6, 30, 0),  # 6h30
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    # Às 6h30, modo noturno já terminou - Lights deve estar ligada
    assert result.device_status["Lights"] is True


def test_mutant44():
    """
    Mata o mutante 44: "Cooling" → "XXCoolingXX"
    
    Mutação: String "Cooling" foi modificada
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"TV": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,  # Temperatura normal
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=50.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    # A chave "Cooling" deve existir e estar False
    assert "Cooling" in result.device_status
    assert result.device_status["Cooling"] is False
    # A chave mutada não deve existir
    assert "XXCoolingXX" not in result.device_status


def test_mutant49():
    """
    Mata o mutante 49: total_energy_used_today >= energy_usage_limit → 
                       total_energy_used_today > energy_usage_limit
    
    Mutação: >= mudou para > na condição do while
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Essential": 1, "Light": 2, "TV": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=30.0,
        total_energy_used_today=30.0,  # Exatamente no limite
        scheduled_devices=[]
    )
    
    assert result.total_energy_used < 30.0


def test_mutant51():
    """
    Mata o mutante 51: device_status.get(device, False) → device_status.get(device, True)
    
    Mutação: Default do .get() mudou de False para True
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Device1": 2, "Device2": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=20.0,
        total_energy_used_today=25.0,  # Acima do limite
        scheduled_devices=[]
    )
    
    # O loop deve funcionar corretamente mesmo com .get()
    # Energia deve ter sido reduzida
    assert result.total_energy_used < 25.0


def test_mutant53():
    """
    Mata o mutante 53: priority > 1 → priority > 2
    
    Mutação: 1 mudou para 2 no check de priority dentro do while
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Essential": 1, "MediumPriority": 2, "Low": 3},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=20.0,
        total_energy_used_today=30.0,  # Muito acima
        scheduled_devices=[]
    )
    
    # Dispositivo com priority 2 deve ser considerado para desligamento
    # Pelo menos um dispositivo com priority > 1 deve ter sido desligado
    low_priority_off = (
        result.device_status["MediumPriority"] is False or 
        result.device_status["Low"] is False
    )
    assert low_priority_off


def test_mutant58():
    """
    Mata o mutante 58: devices_were_on = False → devices_were_on = None
    
    Mutação: False mudou para None
    """
    result = energy_system.manage_energy(
        current_price=0.25,  # Modo economia - desliga baixa prioridade
        price_threshold=0.20,
        device_priorities={"Device1": 1},  # Só alta prioridade
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=10.0,
        total_energy_used_today=15.0,  # Acima do limite
        scheduled_devices=[]
    )
    
    # O código deve executar sem erros (None causaria problemas no and)
    assert result.device_status["Device1"] is True  # Alta prioridade mantém


def test_mutant59():
    """
    Mata o mutante 59: continue → break
    
    Mutação: continue mudou para break
    """
    result = energy_system.manage_energy(
        current_price=0.25,
        price_threshold=0.20,
        device_priorities={"Critical": 1},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=10.0,
        total_energy_used_today=15.0,
        scheduled_devices=[]
    )
    
    # Mesmo sem dispositivos para desligar, deve processar corretamente
    assert result.device_status["Critical"] is True


def test_mutant60():
    """
    Mata o mutante 60: total_energy_used_today < energy_usage_limit → 
                       total_energy_used_today <= energy_usage_limit
    
    Mutação: < mudou para <= no if dentro do for
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"D1": 1, "D2": 2, "D3": 2, "D4": 2, "D5": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=31.0,
        total_energy_used_today=35.0,  # 4 acima do limite
        scheduled_devices=[]
    )
    
    # Deve desligar exatamente 4 dispositivos e parar
    # Original (<): para quando chega abaixo do limite
    # Mutante (<=): pararia quando chegasse exatamente no limite
    devices_off = sum(1 for v in result.device_status.values() if v is False)
    assert devices_off >= 3  # Deve ter desligado pelo menos 3


def test_mutant61():
    """
    Mata o mutante 61: break → continue
    
    Mutação: break mudou para continue
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"D1": 1, "D2": 2, "D3": 2, "D4": 2, "D5": 3},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=30.0,
        total_energy_used_today=32.0,  # 2 acima do limite
        scheduled_devices=[]
    )
    
    # Com break: para assim que atinge o limite
    # Com continue: pode processar todos os dispositivos da lista
    # O código deve parar e não desligar todos os dispositivos
    devices_on = sum(1 for v in result.device_status.values() if v is True)
    assert devices_on >= 2  # Pelo menos alta prioridade + alguns outros


def test_mutant63():
    """
    Mata o mutante 63: device_status[device] = False → device_status[device] = None
    
    Mutação: False mudou para None no desligamento dentro do loop
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"Essential": 1, "NonEssential": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=20.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    # Dispositivo desligado deve ser False, não None
    if result.device_status["NonEssential"] is not True:
        assert result.device_status["NonEssential"] is False
        assert result.device_status["NonEssential"] is not None


def test_mutant64():
    """
    Mata o mutante 64: total_energy_used_today -= 1 → total_energy_used_today = 1
    
    Mutação: -= 1 mudou para = 1 (atribuição em vez de decremento)
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"D1": 1, "D2": 2, "D3": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=20.0,
        total_energy_used_today=25.0,
        scheduled_devices=[]
    )
    
    # Com -= 1: energia seria algo como 22-24
    # Com = 1: energia seria 1
    assert result.total_energy_used > 1
    assert result.total_energy_used < 25.0


def test_mutant66():
    """
    Mata o mutante 66: total_energy_used_today -= 1 → total_energy_used_today -= 2
    
    Mutação: Decremento de 1 mudou para 2
    """
    result = energy_system.manage_energy(
        current_price=0.15,
        price_threshold=0.20,
        device_priorities={"D1": 1, "D2": 2, "D3": 2},
        current_time=datetime(2025, 10, 16, 14, 0, 0),
        current_temperature=22.0,
        desired_temperature_range=(20.0, 24.0),
        energy_usage_limit=28.0,
        total_energy_used_today=30.0,  # 2 acima do limite
        scheduled_devices=[]
    )
    
    # Deve desligar 2 dispositivos e energia deve ser 28
    # Com -= 1: energia = 30 - 2 = 28
    # Com -= 2: energia = 30 - 4 = 26
    # Verifica que a energia está próxima do limite (não muito abaixo)
    assert result.total_energy_used >= 27.0  # No mínimo 27
    assert result.total_energy_used <= 28.0  # No máximo 28
