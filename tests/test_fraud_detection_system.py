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

# -------------------------------------------------------------------------------------------------------------------
# Testes gerados utilizando a Complexidade Ciclomática e a Criação do Conjunto de Caminhos Básicos utilizando o CFG
# -------------------------------------------------------------------------------------------------------------------

def test_cenario_maximo_risco_aciona_todas_regras(fraud_system, now, blacklisted_locations):
    """
    Testa um cenário de risco máximo onde todas as condições de fraude são atendidas.
    1) Valor da transação > 10000
    2) Mais de 10 transações na última hora
    3) Mudança de localização em menos de 30 minutos
    4) Localização da transação está na lista de bloqueio (blacklist)

    Esse teste foi gerado considerando o seguinte fluxo no CFG: A B C D E G D F H I J L K M N.
    Verifique o CFG em cfg/fraud_detection_system.png para mais detalhes.
    """

    # Cria uma transação atual que atende às condições de valor alto e localização na blacklist
    current_transaction = Transaction(
        amount=15000, # Condição 1: Valor alto
        timestamp=now,
        location="Moscou"  # Condição 4: Localização na blacklist
    )

    # Cria a transação mais recente
    most_recent_transaction = Transaction(
        amount=50,
        timestamp=now - timedelta(minutes=15),  # Condição 3: Dentro de 30 minutos
        location="São Paulo"                   
    )

    # Crie as outras 10 transações para exceder o limite de contagem (> 10 transações na última hora).
    # O tempo delas não é tão crítico, desde que estejam na última hora (< 1 hora).
    additional_transactions = [
        Transaction(amount=20, timestamp=now - timedelta(minutes=25), location="São Paulo")
        for _ in range(10)
    ]
    
    # A transação mais recente deve ser a última da lista.
    previous_transactions = additional_transactions + [most_recent_transaction]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado
    expected_result = FraudCheckResult(
        is_fraudulent=True,
        is_blocked=True,
        verification_required=True,
        risk_score=100
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def test_localizacao_bloqueada_com_alta_frequencia_e_mudanca_de_localizacao(fraud_system, now, blacklisted_locations):
    """
    Testa uma transação de valor normal, mas que é bloqueada e marcada como fraude
    devido a uma combinação de outros fatores de risco.
    1) Valor da transação < 10000 (Normal)
    2) Mais de 10 transações na última hora (Dispara bloqueio)
    3) Mudança de localização em menos de 30 minutos (Dispara fraude)
    4) Localização da transação está na lista de bloqueio (Dispara bloqueio, score máximo)

    Esse teste foi gerado considerando o seguinte fluxo no CFG: A C D E G D F H I J L K M N.
    Verifique o CFG em cfg/fraud_detection_system.png para mais detalhes.
    """

    # Cria uma transação atual com valor normal, mas em local da blacklist
    current_transaction = Transaction(
        amount=500,  # Condição 1: Valor normal
        timestamp=now,
        location="Pyongyang"  # Condição 4: Localização na blacklist
    )

    # Cria a transação mais recente para satisfazer a regra de mudança rápida de local
    most_recent_transaction = Transaction(
        amount=50,
        timestamp=now - timedelta(minutes=20),  # Condição 3: Dentro de 30 minutos
        location="São Paulo"                    # Condição 3: Local diferente
    )

    # Cria 10 transações adicionais para exceder o limite de contagem (> 10 no total)
    additional_transactions = [
        Transaction(amount=20, timestamp=now - timedelta(minutes=40), location="São Paulo")
        for _ in range(10) # Condição 2: Total de 11 transações na última hora
    ]
    
    # A transação mais recente deve ser a última da lista
    previous_transactions = additional_transactions + [most_recent_transaction]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado
    expected_result = FraudCheckResult(
        is_fraudulent=True,
        is_blocked=True,
        verification_required=True,
        risk_score=100
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def testa_primeira_transacao_de_valor_alto_em_local_bloqueado(fraud_system, now, blacklisted_locations):
    """
    Testa uma transação que é a primeira de um cliente, mas já possui
    múltiplos sinais de alerta de alto risco.
    1) Valor da transação > 10000 (Alto risco)
    2) Nenhuma transação anterior (size = 0)
    3) Localização da transação está na lista de bloqueio (Alto risco)

    Esse teste foi gerado considerando o seguinte fluxo no CFG: A B C D F I K M N.
    Verifique o CFG em cfg/fraud_detection_system.png para mais detalhes.
    """

    # Cria uma transação atual que atende às condições de valor e localização
    current_transaction = Transaction(
        amount=25000,      # Condição 1: Valor alto
        timestamp=now,
        location="Moscou"  # Condição 3: Localização na blacklist
    )

    # Condição 2: Lista de transações anteriores está vazia
    previous_transactions = []

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado
    expected_result = FraudCheckResult(
        is_fraudulent=True,
        is_blocked=True,
        verification_required=True,
        risk_score=100
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def testa_valor_alto_em_local_bloqueado_com_historico_antigo(fraud_system, now, blacklisted_locations):
    """
    Testa uma transação de valor alto em local bloqueado, onde o histórico de
    transações é numeroso, mas antigo (mais de 1 hora), não devendo
    disparar o alerta de frequência.
    1) Valor da transação > 10000 (Alto risco)
    2) Mais de 10 transações, mas todas com mais de 60 minutos (Frequência OK)
    3) Localização da transação está na lista de bloqueio (Alto risco)

    Esse teste foi gerado considerando o seguinte fluxo no CFG: A B C D E D F H I J K M N.
    Verifique o CFG em cfg/fraud_detection_system.png para mais detalhes.
    """

    # Cria uma transação atual com valor alto e em local da blacklist
    current_transaction = Transaction(
        amount=20000,       # Condição 1: Valor alto
        timestamp=now,
        location="Pyongyang" # Condição 3: Localização na blacklist
    )

    # Cria uma lista de transações anteriores que são numerosas, mas antigas
    # Todas ocorreram há mais de 60 minutos.
    previous_transactions = [
        Transaction(
            amount=100,
            # Gera transações entre 70 e 180 minutos atrás
            timestamp=now - timedelta(minutes=70 + (i * 10)),
            location="São Paulo"
        )
        for i in range(11) # Condição 2: Cria 11 transações antigas
    ]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado
    expected_result = FraudCheckResult(
        is_fraudulent=True,
        is_blocked=True,
        verification_required=True,
        risk_score=100
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def testa_valor_alto_com_mudanca_local_em_area_bloqueada(fraud_system, now, blacklisted_locations):
    """
    Testa uma transação de valor alto que também apresenta mudança rápida de
    localização e ocorre em uma área da blacklist, mas com uma frequência
    de transações abaixo do limite de bloqueio.
    1) Valor da transação > 10000 (Fraude)
    2) 5 transações na última hora (Frequência OK)
    3) Mudança de localização em menos de 30 minutos (Fraude)
    4) Localização da transação está na lista de bloqueio (Bloqueio)

    Esse teste foi gerado considerando o seguinte fluxo no CFG: A B C D E G D F I J L K M N.
    Verifique o CFG em cfg/fraud_detection_system.png para mais detalhes.
    """

    # Cria uma transação atual com valor alto e em local da blacklist
    current_transaction = Transaction(
        amount=12000,       # Condição 1: Valor alto
        timestamp=now,
        location="Moscou"   # Condição 4: Localização na blacklist
    )

    # Cria a transação mais recente para a regra de mudança de local
    most_recent_transaction = Transaction(
        amount=50,
        timestamp=now - timedelta(minutes=10),  # Condição 3: Dentro de 30 minutos
        location="São Paulo"                    # Condição 3: Local diferente
    )

    # Cria 4 transações adicionais para totalizar 5 transações recentes
    additional_transactions = [
        Transaction(amount=20, timestamp=now - timedelta(minutes=20), location="São Paulo")
        for _ in range(4) # Condição 2: Total de 5 transações na última hora
    ]
    
    previous_transactions = additional_transactions + [most_recent_transaction]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado
    expected_result = FraudCheckResult(
        is_fraudulent=True,
        is_blocked=True,
        verification_required=True,
        risk_score=100
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def testa_valor_alto_com_alta_frequencia_sem_mudanca_local(fraud_system, now, blacklisted_locations):
    """
    Testa uma transação de valor alto e alta frequência em um local da blacklist,
    mas onde não houve mudança de localização recente.
    1) Valor da transação > 10000 (Fraude)
    2) Mais de 10 transações na última hora (Bloqueio)
    3) Última transação há mais de 30 minutos e no mesmo local (Mudança de local OK)
    4) Localização da transação está na lista de bloqueio (Bloqueio)

    Esse teste foi gerado considerando o seguinte fluxo no CFG: A B C D E G D F H I J K M N.
    Verifique o CFG em cfg/fraud_detection_system.png para mais detalhes.
    """

    # Cria uma transação atual com valor alto e em local da blacklist
    current_transaction = Transaction(
        amount=18000,       # Condição 1: Valor alto
        timestamp=now,
        location="Moscou"   # Condição 4: Localização na blacklist
    )

    # Cria uma lista de transações anteriores que são numerosas e recentes,
    # mas a mais nova tem mais de 30 minutos e está no mesmo local.
    previous_transactions = [
        Transaction(
            amount=100,
            # Gera 11 transações entre 40 e 50 minutos atrás
            timestamp=now - timedelta(minutes=40 + i),
            location="Moscou" # Condição 3: Mesmo local da transação atual
        )
        for i in range(11) # Condição 2: 11 transações recentes
    ]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado
    expected_result = FraudCheckResult(
        is_fraudulent=True,
        is_blocked=True,
        verification_required=True,
        risk_score=100
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def testa_multiplos_alertas_em_local_confiavel(fraud_system, now, blacklisted_locations):
    """
    Testa um cenário complexo onde todos os alertas de fraude são acionados
    (valor alto, alta frequência, mudança de local), exceto o de localização
    em blacklist.
    1) Valor da transação > 10000 (Fraude)
    2) Mais de 10 transações na última hora (Bloqueio)
    3) Mudança de localização em menos de 30 minutos (Fraude)
    4) Localização da transação NÃO está na lista de bloqueio (Local OK)

    Esse teste foi gerado considerando o seguinte fluxo no CFG: A B C D E G D F H I J L K N.
    Verifique o CFG em cfg/fraud_detection_system.png para mais detalhes.
    """

    # Cria uma transação atual com valor alto em um local confiável
    current_transaction = Transaction(
        amount=15000,           # Condição 1: Valor alto
        timestamp=now,
        location="Campinas"     # Condição 4: Local confiável
    )

    # Cria a transação mais recente para a regra de mudança de local
    most_recent_transaction = Transaction(
        amount=50,
        timestamp=now - timedelta(minutes=15),  # Condição 3: Dentro de 30 minutos
        location="São Paulo"                    # Condição 3: Local diferente
    )

    # Cria 10 transações adicionais para totalizar 11 transações recentes
    additional_transactions = [
        Transaction(amount=20, timestamp=now - timedelta(minutes=30), location="São Paulo")
        for _ in range(10) # Condição 2: Total de 11 transações na última hora
    ]
    
    previous_transactions = additional_transactions + [most_recent_transaction]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado
    expected_result = FraudCheckResult(
        is_fraudulent=True,
        is_blocked=True,
        verification_required=True,
        risk_score=100
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def testa_primeira_transacao_em_local_bloqueado(fraud_system, now, blacklisted_locations):
    """
    Testa uma transação de valor normal que é a primeira de um cliente
    mas que ocorre em uma localização da blacklist, devendo ser bloqueada.
    1) Valor da transação < 10000 (Valor OK)
    2) Nenhuma transação anterior (size = 0)
    3) Localização da transação está na lista de bloqueio (Bloqueio)

    Esse teste foi gerado considerando o seguinte fluxo no CFG: A C D F I K M N.
    Verifique o CFG em cfg/fraud_detection_system.png para mais detalhes.
    """

    # Cria uma transação atual com valor normal, mas em local da blacklist
    current_transaction = Transaction(
        amount=250,        # Condição 1: Valor normal
        timestamp=now,
        location="Moscou"  # Condição 3: Localização na blacklist
    )

    # Lista de transações anteriores está vazia
    previous_transactions = []

    # 2. Act: Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado
    expected_result = FraudCheckResult(
        is_fraudulent=False,
        is_blocked=True,
        verification_required=False,
        risk_score=100
    )

    assert result.is_fraudulent == expected_result.is_fraudulent
    assert result.is_blocked == expected_result.is_blocked
    assert result.verification_required == expected_result.verification_required
    assert result.risk_score == expected_result.risk_score

def testa_transacao_normal_sem_nenhum_risco(fraud_system, now, blacklisted_locations):
    """
    Testa o "caminho feliz": uma transação completamente normal que não
    deve acionar nenhuma regra de fraude.
    1) Valor da transação < 10000 (Valor OK)
    2) Baixa frequência de transações na última hora (Frequência OK)
    3) Sem mudança de localização recente (Localização OK)
    4) Localização da transação NÃO está na lista de bloqueio (Local OK)

    Diferentemente dos testes anteriores, esse teste foi gerado SEM 
    considerar a Complexidade Ciclomática e a Criação do Conjunto de Caminhos Básicos utilizando o CFG.
    O motivo disto é que após utilizar essas técnicas para gerar os testes anteriores, percebeu-se que 
    nenhum dos testes gerados cobria o "caminho feliz", que é um cenário crítico de acordo com os testadores.
    """
    
    # Cria uma transação atual de baixo valor em um local seguro
    current_transaction = Transaction(
        amount=500,        # Condição 1: Valor normal
        timestamp=now,
        location="Campinas"  # Condição 4: Local não está na blacklist
    )

    # Cria um histórico de poucas transações recentes e sem mudança de local
    previous_transactions = [
        Transaction(
            amount=150,
            # Última transação há 45 min (> 30 min) no mesmo local
            timestamp=now - timedelta(minutes=45),
            location="Campinas" # Condição 3: Mesmo local
        ),
        Transaction(
            amount=200,
            timestamp=now - timedelta(minutes=55),
            location="Campinas"
        )
        # Condição 2: Apenas 2 transações recentes, abaixo do limite de 10
    ]

    # Executa o método testado
    result = fraud_system.check_for_fraud(
        current_transaction,
        previous_transactions,
        blacklisted_locations
    )

    # Verifica se o resultado é o esperado (nenhum alerta)
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