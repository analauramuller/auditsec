from app.services.compliance_service import ComplianceService


def test_calculate_percent_basic():
    service = ComplianceService()
    assert service.calculate_percent(conforme=8, nao_aplica=2, total=10) == 100.0


def test_calculate_percent_partial():
    service = ComplianceService()
    assert service.calculate_percent(conforme=5, nao_aplica=0, total=10) == 50.0


def test_calculate_percent_all_na():
    service = ComplianceService()
    assert service.calculate_percent(conforme=0, nao_aplica=10, total=10) == 0.0
