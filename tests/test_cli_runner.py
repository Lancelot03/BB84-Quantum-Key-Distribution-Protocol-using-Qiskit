import pytest
import sys
from unittest.mock import patch, MagicMock
from qkd_cli_runner import run_simulation, main

def test_run_simulation_bb84_no_eve():
    viz_data = run_simulation(
        protocol_name="BB84",
        qubits=20,
        eve_present=False,
        attack_name="Intercept-Resend",
        noise_level=0.1
    )
    assert viz_data['protocol_name'] == "BB84"
    assert len(viz_data['alice_bits']) == 20
    assert viz_data['qber'] == 0.0
    assert viz_data['is_secure'] is True

def test_run_simulation_b92_with_noisy_channel():
    viz_data = run_simulation(
        protocol_name="B92",
        qubits=30,
        eve_present=True,
        attack_name="Noisy Channel",
        noise_level=0.2
    )
    assert viz_data['protocol_name'] == "B92"
    assert len(viz_data['alice_bits']) == 30

def test_run_simulation_bb84_with_pns():
    viz_data = run_simulation(
        protocol_name="BB84",
        qubits=40,
        eve_present=True,
        attack_name="Photon Number Splitting",
        noise_level=0.0
    )
    assert viz_data['protocol_name'] == "BB84"
    assert len(viz_data['alice_bits']) == 40
    # PNS should have fixed eve info gain
    assert viz_data['eve_info_gain'] == 0.25

def test_run_simulation_invalid_protocol():
    with pytest.raises(SystemExit) as excinfo:
        run_simulation(
            protocol_name="INVALID_PROTOCOL",
            qubits=10,
            eve_present=False,
            attack_name="Intercept-Resend",
            noise_level=0.1
        )
    assert excinfo.value.code == 1

def test_run_simulation_invalid_attack():
    with pytest.raises(SystemExit) as excinfo:
        run_simulation(
            protocol_name="BB84",
            qubits=10,
            eve_present=True,
            attack_name="INVALID_ATTACK",
            noise_level=0.1
        )
    assert excinfo.value.code == 1

def test_main_cli_args():
    test_args = ["qkd_cli_runner.py", "-p", "B92", "-n", "15", "-e", "-a", "Noisy Channel", "-s", "0.05"]
    with patch.object(sys, 'argv', test_args):
        # We can intercept run_simulation to verify main parses args correctly
        with patch('qkd_cli_runner.run_simulation') as mock_run:
            main()
            mock_run.assert_called_once_with("B92", 15, True, "Noisy Channel", 0.05)

def test_main_cli_interactive():
    test_args = ["qkd_cli_runner.py", "-i"]
    with patch.object(sys, 'argv', test_args):
        with patch('qkd_cli_runner.interactive_mode') as mock_interactive:
            main()
            mock_interactive.assert_called_once()
