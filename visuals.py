import streamlit.components.v1 as components
from qiskit.quantum_info import Statevector
import numpy as np

def get_bloch_coordinates(qc):
    """
    Calculate [x, y, z] coordinates for the Bloch sphere from a quantum circuit.
    """
    sv = Statevector.from_instruction(qc)
    # Expectation values of Pauli operators
    x = sv.expectation_value([[0, 1], [1, 0]]).real
    y = sv.expectation_value([[0, -1j], [1j, 0]]).real
    z = sv.expectation_value([[1, 0], [0, -1]]).real
    return [float(x), float(y), float(z)]

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
            // (Simplifying for now, can add text sprites later)

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

def photon_transmission(n_photons=10, height=300):
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
                background: radial-gradient(circle, #fff 0%, #00d2ff 100%);
                box-shadow: 0 0 10px #00d2ff;
                top: 50%;
                transform: translateY(-50%);
            }}
            .alice, .bob {{
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
            }}
            .alice {{ left: 20px; }}
            .bob {{ right: 20px; }}

            @keyframes travel {{
                0% {{ left: 80px; opacity: 0; }}
                10% {{ opacity: 1; }}
                90% {{ opacity: 1; }}
                100% {{ left: calc(100% - 100px); opacity: 0; }}
            }}
        </style>
    </head>
    <body>
        <div class="alice">Alice</div>
        <div class="bob">Bob</div>
        <div id="photons-container"></div>
        <script>
            const container = document.getElementById('photons-container');
            const n = {n_photons};
            for (let i = 0; i < n; i++) {{
                const photon = document.createElement('div');
                photon.className = 'photon';
                photon.style.animation = `travel 3s linear ${{i * 0.5}}s infinite`;
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
