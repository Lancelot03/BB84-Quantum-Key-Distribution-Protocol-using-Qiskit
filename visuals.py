import streamlit.components.v1 as components
from qiskit.quantum_info import Statevector
import numpy as np
import matplotlib.pyplot as plt

def plot_bit_differences(key_a, key_b):
    diffs = [int(a != b) for a, b in zip(key_a, key_b)]
    fig, ax = plt.subplots(figsize=(10, 2))
    ax.plot(diffs, marker='o', color='red', label='Mismatch')
    ax.set_title('Bit Differences (1 = Error)')
    ax.set_xlabel('Bit Index')
    ax.set_ylabel('Difference')
    ax.grid(True)
    return fig

def plot_qber_bar(qber):
    fig, ax = plt.subplots()
    correct = 100 * (1 - qber)
    incorrect = 100 * qber
    ax.bar(['Correct', 'Incorrect'], [correct, incorrect], color=['green', 'red'])
    ax.set_title(f'QBER: {qber * 100:.2f}%')
    ax.set_ylim(0, 100)
    return fig

def get_bloch_coordinates(qc):
    """
    Calculate [x, y, z] Bloch coordinates from a QuantumCircuit.
    Defaults to |0> state if calculation fails.
    """
    try:
        sv = Statevector.from_instruction(qc)
        # Expectation values for Pauli-X, Y, Z operators
        # X = <sv|X|sv>, Y = <sv|Y|sv>, Z = <sv|Z|sv>
        x = sv.expectation_value([[0, 1], [1, 0]]).real
        y = sv.expectation_value([[0, -1j], [1j, 0]]).real
        z = sv.expectation_value([[1, 0], [0, -1]]).real
        return [float(x), float(y), float(z)]
    except Exception:
        return [0.0, 0.0, 1.0] # Default to |0>

def bloch_sphere(state_vector=[1, 0, 0], height=500):
    """
    state_vector: [x, y, z] coordinates on the Bloch sphere
    """
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; background-color: #0e1117; }}
            canvas {{ display: block; }}
            #info {{
                position: absolute;
                top: 10px;
                left: 10px;
                color: white;
                font-family: sans-serif;
                font-size: 14px;
                pointer-events: none;
            }}
        </style>
    </head>
    <body>
        <div id="info">Bloch Sphere Visualization</div>
        <div id="container"></div>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
        <script>
            const scene = new THREE.Scene();
            const camera = new THREE.PerspectiveCamera(45, window.innerWidth / {height}, 0.1, 1000);
            const renderer = new THREE.WebGLRenderer({{ antialias: true, alpha: true }});
            renderer.setSize(window.innerWidth, {height});
            document.getElementById('container').appendChild(renderer.domElement);

            const controls = new THREE.OrbitControls(camera, renderer.domElement);

            // Sphere
            const geometry = new THREE.SphereGeometry(2, 32, 32);
            const material = new THREE.MeshPhongMaterial({{
                color: 0x444444,
                wireframe: true,
                transparent: true,
                opacity: 0.3
            }});
            const sphere = new THREE.Mesh(geometry, material);
            scene.add(sphere);

            // Axes
            const axesHelper = new THREE.AxesHelper(3);
            scene.add(axesHelper);

            // Labels for axes
            function makeTextSprite(message, color) {{
                const canvas = document.createElement('canvas');
                canvas.width = 64;
                canvas.height = 64;
                const ctx = canvas.getContext('2d');
                ctx.fillStyle = color;
                ctx.font = 'Bold 40px Arial';
                ctx.textAlign = 'center';
                ctx.textBaseline = 'middle';
                ctx.fillText(message, 32, 32);

                const texture = new THREE.CanvasTexture(canvas);
                const spriteMaterial = new THREE.SpriteMaterial({{ map: texture }});
                const sprite = new THREE.Sprite(spriteMaterial);
                sprite.scale.set(0.6, 0.6, 1);
                return sprite;
            }}

            const labelX = makeTextSprite('X', '#ff4444');
            labelX.position.set(2.5, 0, 0);
            scene.add(labelX);

            const labelY = makeTextSprite('Y', '#4444ff');
            labelY.position.set(0, 0, 2.5);
            scene.add(labelY);

            const labelZ = makeTextSprite('Z', '#44ff44');
            labelZ.position.set(0, 2.5, 0);
            scene.add(labelZ);

            // State Vector
            const dir = new THREE.Vector3({state_vector[0]}, {state_vector[2]}, {state_vector[1]}); // Three.js uses Y as up, Bloch uses Z as up
            dir.normalize();
            const origin = new THREE.Vector3(0, 0, 0);
            const length = 2;
            const hex = 0xffff00;
            const arrowHelper = new THREE.ArrowHelper(dir, origin, length, hex, 0.2, 0.1);
            scene.add(arrowHelper);

            // Lighting
            const light = new THREE.PointLight(0xffffff, 1, 100);
            light.position.set(10, 10, 10);
            scene.add(light);
            const ambientLight = new THREE.AmbientLight(0x404040);
            scene.add(ambientLight);

            camera.position.set(5, 5, 5);
            controls.update();

            function animate() {{
                requestAnimationFrame(animate);
                controls.update();
                renderer.render(scene, camera);
            }}
            animate();

            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / {height};
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, {height});
            }});
        </script>
    </body>
    </html>
    """
    return components.html(html_code, height=height)

def draw_circuit_visual(qc):
    """
    Returns a matplotlib figure of the quantum circuit.
    """
    return qc.draw(output='mpl')

def photon_transmission(n_photons=10, height=300, eve_present=False):
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; overflow: hidden; background-color: #0e1117; }}
            .photon {{
                position: absolute;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                top: 50%;
                transform: translateY(-50%);
            }}
            .photon.normal {{
                background: radial-gradient(circle, #fff 0%, #00d2ff 100%);
                box-shadow: 0 0 10px #00d2ff;
                animation: travel 3s linear infinite;
            }}
            .photon.intercepted {{
                background: radial-gradient(circle, #fff 0%, #00d2ff 100%);
                box-shadow: 0 0 10px #00d2ff;
                animation: travel-intercepted 3s linear infinite;
            }}
            .alice, .bob, .eve {{
                position: absolute;
                top: 50%;
                transform: translateY(-50%);
                color: white;
                font-family: sans-serif;
                font-weight: bold;
                padding: 10px;
                border: 2px solid #555;
                border-radius: 5px;
                background: #222;
                z-index: 10;
            }}
            .alice {{ left: 20px; }}
            .bob {{ right: 20px; }}
            .eve {{
                left: 50%;
                transform: translate(-50%, -50%);
                color: #ff4444;
                border: 2px dashed #ff4444;
                box-shadow: 0 0 10px rgba(255, 68, 68, 0.5);
            }}

            @keyframes travel {{
                0% {{ left: 80px; opacity: 0; }}
                10% {{ opacity: 1; }}
                90% {{ opacity: 1; }}
                100% {{ left: calc(100% - 100px); opacity: 0; }}
            }}

            @keyframes travel-intercepted {{
                0% {{ left: 80px; opacity: 0; background: radial-gradient(circle, #fff 0%, #00d2ff 100%); box-shadow: 0 0 10px #00d2ff; }}
                10% {{ opacity: 1; }}
                45% {{ background: radial-gradient(circle, #fff 0%, #00d2ff 100%); box-shadow: 0 0 10px #00d2ff; }}
                50% {{ left: 50%; background: radial-gradient(circle, #ff0000 0%, #ff4444 100%); box-shadow: 0 0 15px #ff0000; transform: translateY(-50%) scale(1.3); }}
                55% {{ background: radial-gradient(circle, #ffaa00 0%, #ffaa00 100%); box-shadow: 0 0 10px #ffaa00; transform: translateY(-50%) scale(1.0); }}
                90% {{ opacity: 1; }}
                100% {{ left: calc(100% - 100px); opacity: 0; background: radial-gradient(circle, #ffaa00 0%, #ffaa00 100%); box-shadow: 0 0 10px #ffaa00; }}
            }}
        </style>
    </head>
    <body>
        <div class="alice">Alice</div>
        {"<div class='eve'>Eve</div>" if eve_present else ""}
        <div class="bob">Bob</div>
        <div id="photons-container"></div>
        <script>
            const container = document.getElementById('photons-container');
            const n = {n_photons};
            const isIntercepted = { "true" if eve_present else "false" };
            for (let i = 0; i < n; i++) {{
                const photon = document.createElement('div');
                photon.className = isIntercepted ? 'photon intercepted' : 'photon normal';
                photon.style.animationDelay = `${{i * 0.5}}s`;
                container.appendChild(photon);
            }}
        </script>
    </body>
    </html>
    """
    return components.html(html_code, height=height)

def basis_matching_visual(alice_bases, bob_bases, height=200):
    matches = "".join(["✅" if a == b else "❌" for a, b in zip(alice_bases, bob_bases)])
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                margin: 0;
                background-color: #0e1117;
                color: white;
                font-family: monospace;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: {height}px;
                overflow-x: auto;
                white-space: nowrap;
                padding: 10px;
            }}
            .row {{ display: flex; margin: 2px 0; }}
            .cell {{
                width: 30px;
                height: 30px;
                display: flex;
                align-items: center;
                justify-content: center;
                border: 1px solid #444;
                margin: 1px;
                font-size: 12px;
            }}
            .match {{ background-color: rgba(0, 255, 0, 0.2); }}
            .mismatch {{ background-color: rgba(255, 0, 0, 0.2); }}
            .label {{ width: 80px; text-align: right; margin-right: 10px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="row">
            <div class="label">Alice Basis:</div>
            {"".join([f'<div class="cell">{b}</div>' for b in alice_bases])}
        </div>
        <div class="row">
            <div class="label">Bob Basis:</div>
            {"".join([f'<div class="cell">{b}</div>' for b in bob_bases])}
        </div>
        <div class="row">
            <div class="label">Match:</div>
            {"".join([f'<div class="cell {"match" if a==b else "mismatch"}">{ "✔" if a==b else "✘"}</div>' for a, b in zip(alice_bases, bob_bases)])}
        </div>
    </body>
    </html>
    """
    return components.html(html_code, height=height)
