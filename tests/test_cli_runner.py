import pytest
from unittest.mock import patch
from qkd_cli_runner import run_simulation

def test_run_simulation_bb84_no_attack():
    with patch('builtins.print') as mock_print:
        exit_code = run_simulation("BB84", 20, None, 0.1)
        assert exit_code == 0
        # Check that prints occurred
        assert mock_print.called

def test_run_simulation_b92_no_attack():
    with patch('builtins.print') as mock_print:
        exit_code = run_simulation("B92", 40, None, 0.1)
        assert exit_code == 0
        assert mock_print.called

def test_run_simulation_bb84_intercept_resend():
    with patch('builtins.print') as mock_print:
        exit_code = run_simulation("BB84", 50, "Intercept-Resend", 0.2)
        assert exit_code == 0
        assert mock_print.called

def test_run_simulation_bb84_noisy_channel():
    with patch('builtins.print') as mock_print:
        exit_code = run_simulation("BB84", 50, "Noisy-Channel", 0.15)
        assert exit_code == 0
        assert mock_print.called

def test_run_simulation_bb84_pns():
    with patch('builtins.print') as mock_print:
        exit_code = run_simulation("BB84", 50, "PNS", 0.1)
        assert exit_code == 0
        assert mock_print.called

def test_run_simulation_invalid_protocol():
    exit_code = run_simulation("INVALID_PROTOCOL", 10, None, 0.1)
    assert exit_code == 1

def test_run_simulation_invalid_attack():
    exit_code = run_simulation("BB84", 10, "INVALID_ATTACK", 0.1)
    assert exit_code == 1
