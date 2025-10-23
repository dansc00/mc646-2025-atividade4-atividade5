import pytest
from datetime import datetime, timedelta
from src.fraud.Transaction import Transaction
from src.fraud.FraudCheckResult import FraudCheckResult
from src.fraud.FraudDetectionSystem import FraudDetectionSystem

@pytest.fixture
def fraud_system():
    return FraudDetectionSystem()

@pytest.fixture
def blacklisted_locations():
    return ["Moscou", "Pyongyang"]

@pytest.fixture
def now():
    return datetime.now()

# ------------------------------------------------------
# Testes gerados utilizando a Análise de Mutantes Vivos
# ------------------------------------------------------

def test_mutante_133_valor_exato_limite_10000_nao_deve_ser_fraude(fraud_system, now, blacklisted_locations):
    """
    Testa o valor limite exato de 10000.
    Este teste é projetado para matar o mutante 133 (que muda > para >=).

    No código original (> 10000), 10000 NÃO é fraude.
    No código mutado (>= 10000), 10000 É fraude (score 50).

    O teste espera o comportamento original (não-fraude) e falhará
    no mutante.
    """

    # Cria uma transação atual com o valor exato do limite
    current_transaction = Transaction(
        amount=10000,       # Condição de limite
        timestamp=now,
        location="Campinas"   # Local OK (não está na blacklist)
    )

    # Histórico de transações normais (sem outros alertas)
    previous_transactions = [
        Transaction(
            amount=150,
            timestamp=now - timedelta(minutes=45), # Frequência OK
            location="Campinas"                    # Mudança de local OK
        )
    ]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica o resultado esperado (comportamento original)
    # O valor 10000 não deve disparar a regra
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=False,
        verification_required=False,
        risk_score=0
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_mutante_134_valor_exato_limite_10001_deve_ser_fraude(fraud_system, now, blacklisted_locations):
    """
    Testa o valor limite exato de 10001.
    Este teste é projetado para matar o mutante 134 (que muda > 10000 para > 10001).

    No código original (> 10000), 10001 É fraude (score 50).
    No código mutado (> 10001), 10001 NÃO é fraude (score 0).

    O teste espera o comportamento original (fraude) e falhará no mutante.
    """

    # Cria uma transação atual com o valor exato do limite + 1
    current_transaction = Transaction(
        amount=10001,       # Condição de limite
        timestamp=now,
        location="Campinas"   # Local OK (não está na blacklist)
    )

    # Histórico de transações normais (sem outros alertas)
    previous_transactions = [
        Transaction(
            amount=150,
            timestamp=now - timedelta(minutes=45), # Frequência OK
            location="Campinas"                    # Mudança de local OK
        )
    ]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica o resultado esperado (comportamento original)
    # O valor 10001 deve disparar a regra
    expected_result = FraudCheckResult(
        is_fraudulent=True,
        is_blocked=False,
        verification_required=True,
        risk_score=50
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_mutante_142_exatamente_10_transacoes_recentes(fraud_system, now, blacklisted_locations):
    """
    Testa o limite exato de 10 transações recentes.
    Este teste é projetado para matar o mutante 142 (recent_transaction_count = 1).

    Cenário: Valor normal, local OK, sem mudança de local, 10 transações recentes.

    No código original (count=0), o count final é 10. (10 > 10) é Falso.
    result.is_blocked = False, score = 0.

    No código mutado (count=1), o count final é 11. (11 > 10) é Verdadeiro.
    result.is_blocked = True, score = 30.

    O teste espera o comportamento original (não-bloqueado).
    """
    current_transaction = Transaction(
        amount=500, # Valor OK
        timestamp=now,
        location="Campinas" # Local OK
    )

    # Cria exatamente 10 transações recentes (dentro de 60 min)
    # A mais recente tem 40 min, então a regra de "mudança de local" (L36) não dispara
    previous_transactions = [
        Transaction(
            amount=20, 
            timestamp=now - timedelta(minutes=40 + i), # entre 40 e 49 min atrás
            location="Campinas" # Mesmo local
        )
        for i in range(10) # Exatamente 10 transações
    ]

    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Espera o comportamento original (não bloqueado)
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=False,
        verification_required=False,
        risk_score=0
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_mutante_147_transacao_pouco_mais_de_60_minutos(fraud_system, now, blacklisted_locations):
    """
    Testa o cálculo da janela de 60 minutos (divisão por 60 vs 61).
    Este teste é projetado para matar o mutante 147.

    Cenário: 10 transações (< 60 min) e 1 transação a 60.5 min (3630s).

    No código original (/ 60), 3630s = 60.5 min. (60.5 <= 60) é Falso.
    O count final é 10. (10 > 10) é Falso. Não bloqueia.

    No código mutado (/ 61), 3630s = 59.5 min. (59.5 <= 60) é Verdadeiro.
    O count final é 11. (11 > 10) é Verdadeiro. Bloqueia.

    O teste espera o comportamento original (não-bloqueado).
    """
    current_transaction = Transaction(
        amount=500, timestamp=now, location="Campinas"
    )

    # 10 transações recentes (OK)
    recent_transactions = [
        Transaction(amount=20, timestamp=now - timedelta(minutes=40 + i), location="Campinas")
        for i in range(10)
    ]
    
    # 1 transação no limite (60.5 minutos = 3630 segundos)
    borderline_transaction = [
        Transaction(amount=50, timestamp=now - timedelta(seconds=3630), location="Campinas")
    ]
    
    previous_transactions = recent_transactions + borderline_transaction

    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Espera o comportamento original (não bloqueado)
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=False,
        verification_required=False,
        risk_score=0
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_mutante_149_transacao_exatamente_60_minutos(fraud_system, now, blacklisted_locations):
    """
    Testa o limite exato da janela de 60 minutos (<= vs <).
    Este teste é projetado para matar o mutante 149 (<= 60 para < 60).

    Cenário: 10 transações (< 60 min) e 1 transação a exatos 60 min (3600s).

    No código original (<= 60), 3600s = 60.0 min. (60.0 <= 60) é Verdadeiro.
    O count final é 11. (11 > 10) é Verdadeiro. Bloqueia (score 30).

    No código mutado (< 60), 3600s = 60.0 min. (60.0 < 60) é Falso.
    O count final é 10. (10 > 10) é Falso. Não bloqueia (score 0).

    O teste espera o comportamento original (bloqueado).
    """
    current_transaction = Transaction(
        amount=500, timestamp=now, location="Campinas"
    )

    # 10 transações recentes (< 60 min)
    recent_transactions = [
        Transaction(amount=20, timestamp=now - timedelta(minutes=40 + i), location="Campinas")
        for i in range(10)
    ]
    
    # 1 transação exatamente no limite (60 minutos = 3600 segundos)
    borderline_transaction = [
        Transaction(amount=50, timestamp=now - timedelta(seconds=3600), location="Campinas")
    ]
    
    previous_transactions = recent_transactions + borderline_transaction

    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Espera o comportamento original (bloqueado)
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=True,
        verification_required=False,
        risk_score=30
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_mutante_153_exatamente_6_transacoes_recentes(fraud_system, now, blacklisted_locations):
    """
    Testa a contagem de transações (+= 1 vs += 2).
    Este teste é projetado para matar o mutante 153 (+= 2).

    Cenário: 6 transações recentes. (Valor/Local/Mudança OK).

    No código original (+= 1), o count final é 6. (6 > 10) é Falso.
    Não bloqueia (score 0).

    No código mutado (+= 2), o count final é 12. (12 > 10) é Verdadeiro.
    Bloqueia (score 30).

    O teste espera o comportamento original (não-bloqueado).
    """
    current_transaction = Transaction(
        amount=500, timestamp=now, location="Campinas"
    )

    # Exatamente 6 transações recentes
    previous_transactions = [
        Transaction(
            amount=20, 
            timestamp=now - timedelta(minutes=40 + i), # > 30 min (sem mudança local)
            location="Campinas" # Mesmo local
        )
        for i in range(6) # Exatamente 6 transações
    ]

    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Espera o comportamento original (não bloqueado)
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=False,
        verification_required=False,
        risk_score=0
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_mutante_167_transacao_pouco_mais_de_30_minutos(fraud_system, now, blacklisted_locations):
    """
    Testa o cálculo da janela de 30 minutos (mudança de local).
    Este teste é projetado para matar o mutante 167 (divisão por 61).

    Cenário: Transação anterior 30.1 minutos (1806 segundos) atrás,
    em local diferente. (Valor, Frequência, Local OK).

    No código original (/ 60), 1806s = 30.1 min. (30.1 < 30) é Falso.
    Não é fraude (score 0).

    No código mutado (/ 61), 1806s = 29.6... min. (29.6 < 30) é Verdadeiro.
    É fraude (score 20).

    O teste espera o comportamento original (não-fraude).
    """
    current_transaction = Transaction(
        amount=500, timestamp=now, location="Campinas" # Local atual
    )

    # 1 transação no limite (30.1 minutos = 1806 segundos)
    previous_transactions = [
        Transaction(
            amount=50,
            timestamp=now - timedelta(seconds=1806),
            location="São Paulo" # Local diferente
        )
    ]
    
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Espera o comportamento original (não-fraude)
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=False,
        verification_required=False,
        risk_score=0
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_mutante_169_transacao_exatamente_30_minutos(fraud_system, now, blacklisted_locations):
    """
    Testa o limite exato da janela de 30 minutos (< 30 vs <= 30).
    Este teste é projetado para matar o mutante 169 (<= 30).

    Cenário: Transação anterior exatamente 30 minutos (1800 segundos) atrás,
    em local diferente. (Valor, Frequência, Local OK).

    No código original (< 30), 1800s = 30.0 min. (30.0 < 30) é Falso.
    Não é fraude (score 0).

    No código mutado (<= 30), 1800s = 30.0 min. (30.0 <= 30) é Verdadeiro.
    É fraude (score 20).

    O teste espera o comportamento original (não-fraude).
    """
    current_transaction = Transaction(
        amount=500, timestamp=now, location="Campinas" # Local atual
    )

    # 1 transação exatamente no limite (30 minutos = 1800 segundos)
    previous_transactions = [
        Transaction(
            amount=50,
            timestamp=now - timedelta(seconds=1800),
            location="São Paulo" # Local diferente
        )
    ]
    
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Espera o comportamento original (não-fraude)
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=False,
        verification_required=False,
        risk_score=0
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_mutante_172_transacao_recente_mesmo_local(fraud_system, now, blacklisted_locations):
    """
    Testa o operador lógico (AND vs OR) na regra de mudança de local.
    Este teste é projetado para matar o mutante 172 (AND para OR).

    Cenário: Transação anterior 15 minutos atrás (< 30 min = True),
    mas no MESMO local (location != location = False).
    (Valor, Frequência, Local OK).

    No código original (AND), (True AND False) é Falso.
    Não é fraude (score 0).

    No código mutado (OR), (True OR False) é Verdadeiro.
    É fraude (score 20).

    O teste espera o comportamento original (não-fraude).
    """
    current_transaction = Transaction(
        amount=500, timestamp=now, location="Campinas" # Local atual
    )

    # 1 transação recente, mas no mesmo local
    previous_transactions = [
        Transaction(
            amount=50,
            timestamp=now - timedelta(minutes=15), # Recente (True)
            location="Campinas" # Mesmo local (False)
        )
    ]
    
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Espera o comportamento original (não-fraude)
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=False,
        verification_required=False,
        risk_score=0
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score