import subprocess
import sys
from qkd_cli_runner import parse_args

def test_cli_parse_args():
    # Test default parsing
    args = parse_args([])
    assert args.protocol == "BB84"
    assert args.qubits == 100
    assert not args.eve
    assert args.attack == "Intercept-Resend"
    assert args.noise == 0.1

    # Test custom parsing
    args = parse_args(["-p", "B92", "-n", "50", "-e", "-a", "Noisy Channel", "-s", "0.25"])
    assert args.protocol == "B92"
    assert args.qubits == 50
    assert args.eve
    assert args.attack == "Noisy Channel"
    assert args.noise == 0.25

def test_cli_help_execution():
    result = subprocess.run(
        [sys.executable, "qkd_cli_runner.py", "--help"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "QKD (Quantum Key Distribution) CLI Simulator" in result.stdout
    assert "--protocol" in result.stdout
    assert "--qubits" in result.stdout

def test_cli_bb84_default_execution():
    result = subprocess.run(
        [sys.executable, "qkd_cli_runner.py", "-n", "20"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Starting Quantum Key Distribution Simulation" in result.stdout
    assert "Protocol:   BB84" in result.stdout
    assert "Sifted Key Length:" in result.stdout
    assert "QBER:" in result.stdout
    assert "Security Status:" in result.stdout

def test_cli_b92_with_eve_execution():
    result = subprocess.run(
        [sys.executable, "qkd_cli_runner.py", "-p", "B92", "-n", "40", "-e", "-a", "Intercept-Resend", "-s", "0.3"],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0
    assert "Protocol:   B92" in result.stdout
    assert "Eavesdropper: Yes (Intercept-Resend" in result.stdout
    assert "QBER:" in result.stdout
    assert "Basis Match Efficiency:" in result.stdout
