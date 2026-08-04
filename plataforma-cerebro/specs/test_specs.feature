Feature: Orquestracao Cognitiva e Seguranca do Cerebro de Condominio

  Scenario: Executar pagamento autorizado (Happy Path)
    Given o usuario possui cargo 'condo_financial_analyst'
    And o condominio e 'C01'
    And o valor do pagamento e R$ 5000.00
    When o usuario solicita 'Executar pagamento do condominio C01'
    Then o motor deve retornar status 'executado'

  Scenario: Bloquear pagamento sem autorizacao (Adversarial ABAC)
    Given o usuario possui cargo 'condo_manager'
    And o condominio e 'C01'
    And o valor do pagamento e R$ 1000.00
    When o usuario solicita 'Executar pagamento sem autorizacao'
    Then o motor deve retornar status 'bloqueado'

  Scenario: Bloquear pagamento acima do limite maximo (Limit Exceeded)
    Given o usuario possui cargo 'condo_financial_analyst'
    And o condominio e 'C01'
    And o valor do pagamento e R$ 60000.00
    When o usuario solicita 'Executar pagamento acima do limite maximo'
    Then o motor deve retornar status 'bloqueado'
