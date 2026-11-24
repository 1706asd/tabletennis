<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>리얼 3D 탁구 시뮬레이터 (3D Table Tennis)</title>
    <!-- Tailwind CSS for UI controls -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Three.js 3D Library -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <!-- FontAwesome icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800;900&display=swap');
        
        body {
            font-family: 'Pretendard', sans-serif;
            background-color: #090d16;
            color: #f8fafc;
            user-select: none;
            -webkit-user-select: none;
            touch-action: none;
            overflow: hidden;
        }

        #canvas-container {
            width: 100vw;
            height: 100vh;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 1;
        }

        .glass-panel {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.12);
        }

        @keyframes pulse-glow {
            0%, 100% { transform: scale(1); opacity: 1; }
            50% { transform: scale(1.05); opacity: 0.85; }
        }
        .animate-pulse-glow {
            animation: pulse-glow 0.8s infinite ease-in-out;
        }
    </style>
</head>
<body class="w-screen h-screen flex flex-col justify-between p-3 md:p-6 select-none">

    <!-- 3D Canvas Container -->
    <div id="canvas-container"></div>

    <!-- Top UI Header (Score & Rally Stats) -->
    <header class="relative z-10 w-full max-w-5xl mx-auto glass-panel rounded-2xl p-3 md:p-4 flex items-center justify-between shadow-2xl">
        <!-- Player Info (Blue) -->
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 md:w-12 md:h-12 rounded-full bg-blue-600 flex items-center justify-center font-black text-xl border-2 border-blue-300 shadow-lg">
                <i class="fa-solid fa-user"></i>
            </div>
            <div>
                <div class="flex items-center space-x-2">
                    <span class="text-xs text-blue-300 font-bold uppercase tracking-wider">YOU (플레이어)</span>
                    <span id="player-serve-badge" class="hidden px-1.5 py-0.5 rounded text-[10px] bg-amber-500 text-slate-950 font-black">서브</span>
                </div>
                <div class="text-2xl md:text-4xl font-black text-blue-400" id="player-score">0</div>
            </div>
        </div>

        <!-- Rally & Game Status Center -->
        <div class="text-center">
            <div class="text-xs text-slate-400 font-semibold mb-0.5">최고 랠리: <span id="max-rally" class="text-amber-400 font-bold">0</span>회</div>
            <div class="text-xl md:text-3xl font-black text-white tracking-widest">
                랠리 <span id="current-rally" class="text-emerald-400">0</span>
            </div>
            <div id="game-status-badge" class="mt-1 inline-block px-3 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                11점 선승 (2점 차 승부)
            </div>
        </div>

        <!-- AI Info (Red) -->
        <div class="flex items-center space-x-3 text-right">
            <div>
                <div class="flex items-center justify-end space-x-2">
                    <span id="ai-serve-badge" class="hidden px-1.5 py-0.5 rounded text-[10px] bg-amber-500 text-slate-950 font-black">서브</span>
                    <span class="text-xs text-red-300 font-bold uppercase tracking-wider" id="ai-label">AI (보통)</span>
                </div>
                <div class="text-2xl md:text-4xl font-black text-red-400" id="ai-score">0</div>
            </div>
            <div class="w-10 h-10 md:w-12 md:h-12 rounded-full bg-red-600 flex items-center justify-center font-black text-xl border-2 border-red-300 shadow-lg">
                <i class="fa-solid fa-robot"></i>
            </div>
        </div>
    </header>

    <!-- Serve Notice Overlay -->
    <div id="serve-prompt" class="hidden absolute top-28 left-1/2 -translate-x-1/2 z-10 glass-panel px-6 py-2.5 rounded-full text-amber-300 font-bold text-sm md:text-base border border-amber-400/40 animate-pulse-glow shadow-xl">
        <i class="fa-solid fa-table-tennis-paddle-ball mr-2"></i><span id="serve-prompt-text">당신의 서브 순서입니다! (클릭/터치 시 서브)</span>
    </div>

    <!-- Bottom Controls & Camera Toggle -->
    <footer class="relative z-10 w-full max-w-5xl mx-auto glass-panel rounded-2xl p-3 flex flex-wrap items-center justify-between text-xs text-slate-300 gap-2 shadow-2xl">
        <div class="flex items-center space-x-3">
            <span class="font-bold text-slate-400"><i class="fa-solid fa-video mr-1 text-blue-400"></i> 시점 변경:</span>
            <button onclick="setCameraView('player')" id="cam-player" class="cam-btn px-2.5 py-1 bg-blue-600 rounded-lg text-white font-bold transition">1인칭 (플레이어)</button>
            <button onclick="setCameraView('quarter')" id="cam-quarter" class="cam-btn px-2.5 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 font-semibold transition">쿼터뷰</button>
            <button onclick="setCameraView('side')" id="cam-side" class="cam-btn px-2.5 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 font-semibold transition">사이드뷰</button>
        </div>

        <div class="flex items-center space-x-3">
            <button onclick="toggleMute()" id="btn-sound" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 text-slate-200 font-bold transition flex items-center space-x-1.5">
                <i class="fa-solid fa-volume-high" id="icon-sound"></i>
                <span id="text-sound">효과음 ON</span>
            </button>
        </div>
    </footer>

    <!-- Overlay: Start / Difficulty Select Modal -->
    <div id="modal-start" class="absolute inset-0 glass-panel rounded-3xl flex flex-col items-center justify-center p-6 text-center z-20 m-4 md:m-12 max-w-xl mx-auto my-auto h-fit shadow-2xl">
        <div class="w-20 h-20 bg-emerald-500/20 border-2 border-emerald-400 rounded-full flex items-center justify-center mb-4 text-emerald-400 text-4xl shadow-xl animate-pulse-glow">
            <i class="fa-solid fa-table-tennis-paddle-ball"></i>
        </div>
        <h1 class="text-3xl md:text-5xl font-black text-white mb-2 tracking-tight">3D 리얼 탁구 게임</h1>
        <p class="text-slate-300 text-sm md:text-base max-w-md mb-6 leading-relaxed">
            마우스 / 터치를 움직여 3D 라켓을 조작하세요.<br>
            빠르게 앞/위로 스윙하면 강력한 <strong>탑스핀 스매시</strong>가 발동합니다!
        </p>

        <div class="w-full max-w-xs space-y-3 mb-6">
            <label class="block text-xs font-bold text-slate-400 uppercase tracking-wider text-left">AI 난이도 선택</label>
            <div class="grid grid-cols-3 gap-2">
                <button type="button" onclick="selectDifficulty('easy')" id="btn-easy" class="diff-btn py-2.5 rounded-xl font-bold text-sm bg-slate-800 border border-slate-600 text-slate-300 hover:bg-slate-700 transition">쉬움</button>
                <button type="button" onclick="selectDifficulty('medium')" id="btn-medium" class="diff-btn py-2.5 rounded-xl font-bold text-sm bg-blue-600 border border-blue-400 text-white shadow-lg transition">보통</button>
                <button type="button" onclick="selectDifficulty('hard')" id="btn-hard" class="diff-btn py-2.5 rounded-xl font-bold text-sm bg-slate-800 border border-slate-600 text-slate-300 hover:bg-slate-700 transition">어려움</button>
            </div>
        </div>

        <button onclick="startGame()" class="w-full max-w-xs py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-lg rounded-xl shadow-xl transition transform hover:scale-105 active:scale-95 flex items-center justify-center space-x-2">
            <i class="fa-solid fa-play"></i>
            <span>경기 시작하기</span>
        </button>
    </div>

    <!-- Overlay: Match Over Modal -->
    <div id="modal-over" class="hidden absolute inset-0 glass-panel rounded-3xl flex flex-col items-center justify-center p-6 text-center z-20 m-4 md:m-12 max-w-xl mx-auto my-auto h-fit shadow-2xl">
        <div id="winner-icon" class="w-20 h-20 rounded-full flex items-center justify-center mb-4 text-4xl shadow-xl"></div>
        <h2 id="winner-title" class="text-3xl md:text-4xl font-black text-white mb-2"></h2>
        <p id="winner-desc" class="text-slate-300 text-sm md:text-base mb-6"></p>

        <div class="bg-slate-900/80 rounded-2xl p-4 w-full max-w-xs mb-6 border border-slate-700 text-left space-y-2 text-sm">
            <div class="flex justify-between">
                <span class="text-slate-400">최종 스코어:</span>
                <span id="final-score" class="font-bold text-white">11 - 9</span>
            </div>
            <div class="flex justify-between">
                <span class="text-slate-400">최장 랠리:</span>
                <span id="final-rally" class="font-bold text-emerald-400">0 회</span>
            </div>
            <div class="flex justify-between">
                <span class="text-slate-400">스매시 성공:</span>
                <span id="final-smashes" class="font-bold text-amber-400">0 회</span>
            </div>
        </div>

        <button onclick="restartGame()" class="w-full max-w-xs py-3.5 bg-blue-600 hover:bg-blue-500 text-white font-black text-lg rounded-xl shadow-xl transition transform hover:scale-105 active:scale-95 flex items-center justify-center space-x-2">
            <i class="fa-solid fa-rotate-right"></i>
            <span>다시 경기하기</span>
        </button>
    </div>

    <!-- Game Logic Script -->
    <script>
        // ==========================================
        // 1. Web Audio API Sound Synth Engine
        // ==========================================
        class SoundEngine {
            constructor() {
                this.ctx = null;
                this.muted = false;
            }

            init() {
                if (!this.ctx) {
                    const AudioCtx = window.AudioContext || window.webkitAudioContext;
                    if (AudioCtx) this.ctx = new AudioCtx();
                }
                if (this.ctx && this.ctx.state === 'suspended') {
                    this.ctx.resume();
                }
            }

            playPaddleHit(isSmash = false) {
                if (this.muted || !this.ctx) return;
                try {
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.type = isSmash ? 'sawtooth' : 'sine';
                    const freq = isSmash ? 720 : 450;
                    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(120, this.ctx.currentTime + (isSmash ? 0.14 : 0.08));

                    gain.gain.setValueAtTime(isSmash ? 0.45 : 0.25, this.ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + (isSmash ? 0.14 : 0.08));

                    osc.connect(gain);
                    gain.connect(this.ctx.destination);
                    osc.start();
                    osc.stop(this.ctx.currentTime + (isSmash ? 0.14 : 0.08));
                } catch(e){}
            }

            playTableBounce() {
                if (this.muted || !this.ctx) return;
                try {
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.type = 'triangle';
                    osc.frequency.setValueAtTime(320, this.ctx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(90, this.ctx.currentTime + 0.06);

                    gain.gain.setValueAtTime(0.22, this.ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + 0.06);

                    osc.connect(gain);
                    gain.connect(this.ctx.destination);
                    osc.start();
                    osc.stop(this.ctx.currentTime + 0.06);
                } catch(e){}
            }

            playScore(isPlayerWinner) {
                if (this.muted || !this.ctx) return;
                try {
                    const now = this.ctx.currentTime;
                    const freqs = isPlayerWinner ? [523.25, 659.25, 783.99] : [392.00, 349.23, 329.63];
                    freqs.forEach((freq, idx) => {
                        const osc = this.ctx.createOscillator();
                        const gain = this.ctx.createGain();
                        osc.type = 'sine';
                        osc.frequency.setValueAtTime(freq, now + idx * 0.1);
                        gain.gain.setValueAtTime(0.2, now + idx * 0.1);
                        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.1 + 0.22);
                        osc.connect(gain);
                        gain.connect(this.ctx.destination);
                        osc.start(now + idx * 0.1);
                        osc.stop(now + idx * 0.1 + 0.22);
                    });
                } catch(e){}
            }
        }

        const audio = new SoundEngine();

        // ==========================================
        // 2. Constants & Table Physics Dimensions
        // ==========================================
        // Official Table proportional dimensions in 3D units (meters scale)
        const TABLE = {
            width: 1.525,     // X axis width
            length: 2.74,     // Z axis length
            height: 0.76,     // Y axis surface height from floor
            netHeight: 0.1525
        };

        const BALL_RADIUS = 0.038;
        const PADDLE_RADIUS = 0.11;

        // Game State Variables
        let gameState = 'START'; // 'START', 'SERVE', 'PLAYING', 'SCORED', 'OVER'
        let difficulty = 'medium';
        let currentCameraView = 'player'; // 'player', 'quarter', 'side'

        let playerScore = 0;
        let aiScore = 0;
        let rallyCount = 0;
        let maxRallyCount = 0;
        let smashCount = 0;
        let server = 'player'; // 'player' or 'ai'
        let totalServesCount = 0;

        let lastBounceSide = null; // 'player' or 'ai' or null
        let bounceCountThisTurn = 0;

        // Pointer / Input tracking
        const mouse2D = new THREE.Vector2();
        let targetPaddlePos = new THREE.Vector3(0, TABLE.height + 0.15, TABLE.length / 2 + 0.35);
        let lastPaddlePos = new THREE.Vector3();
        let paddleVelocity = new THREE.Vector3();

        // ==========================================
        // 3. Three.js Scene & Object Construction
        // ==========================================
        const container = document.getElementById('canvas-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0a0f1d);
        scene.fog = new THREE.FogExp2(0x0a0f1d, 0.08);

        const camera = new THREE.PerspectiveCamera(50, window.innerWidth / window.innerHeight, 0.1, 50);
        
        const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        // Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        scene.add(ambientLight);

        const spotLight = new THREE.SpotLight(0xffffff, 1.2);
        spotLight.position.set(0, 4.5, 0);
        spotLight.angle = Math.PI / 3;
        spotLight.penumbra = 0.4;
        spotLight.castShadow = true;
        spotLight.shadow.mapSize.width = 2048;
        spotLight.shadow.mapSize.height = 2048;
        spotLight.shadow.bias = -0.0005;
        scene.add(spotLight);

        // Floor / Gymnasium arena background
        const floorGeo = new THREE.PlaneGeometry(24, 24);
        const floorMat = new THREE.MeshStandardMaterial({ color: 0x111827, roughness: 0.8 });
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.receiveShadow = true;
        scene.add(floor);

        // Table Mesh Group
        const tableGroup = new THREE.Group();
        scene.add(tableGroup);

        // Table Top Surface
        const tableGeo = new THREE.BoxGeometry(TABLE.width, 0.05, TABLE.length);
        const tableMat = new THREE.MeshStandardMaterial({ color: 0x1e3a8a, roughness: 0.3, metalness: 0.1 });
        const tableMesh = new THREE.Mesh(tableGeo, tableMat);
        tableMesh.position.y = TABLE.height - 0.025;
        tableMesh.receiveShadow = true;
        tableMesh.castShadow = true;
        tableGroup.add(tableMesh);

        // White Lines on Table
        const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        
        // Border lines
        const borderGeo = new THREE.BoxGeometry(TABLE.width + 0.01, 0.052, TABLE.length + 0.01);
        const borderMesh = new THREE.Mesh(borderGeo, new THREE.MeshBasicMaterial({ color: 0xffffff }));
        borderMesh.position.y = TABLE.height - 0.025;
        tableGroup.add(borderMesh);
        // Inner blue overlay to leave white border lines
        const innerBlue = new THREE.Mesh(
            new THREE.BoxGeometry(TABLE.width - 0.03, 0.054, TABLE.length - 0.03),
            tableMat
        );
        innerBlue.position.y = TABLE.height - 0.024;
        tableGroup.add(innerBlue);

        // Center White Line
        const centerLineGeo = new THREE.BoxGeometry(0.008, 0.055, TABLE.length - 0.03);
        const centerLine = new THREE.Mesh(centerLineGeo, lineMat);
        centerLine.position.y = TABLE.height - 0.023;
        tableGroup.add(centerLine);

        // Net Mesh & Posts
        const netGroup = new THREE.Group();
        const netGeo = new THREE.BoxGeometry(TABLE.width + 0.1, TABLE.netHeight, 0.005);
        const netMat = new THREE.MeshStandardMaterial({ color: 0xffffff, transparent: true, opacity: 0.7, wireframe: true });
        const netMesh = new THREE.Mesh(netGeo, netMat);
        netMesh.position.y = TABLE.height + TABLE.netHeight / 2;
        netGroup.add(netMesh);

        // Net Posts
        const postGeo = new THREE.CylinderGeometry(0.012, 0.012, TABLE.netHeight + 0.02, 12);
        const postMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.8 });
        const post1 = new THREE.Mesh(postGeo, postMat);
        post1.position.set(TABLE.width / 2 + 0.05, TABLE.height + TABLE.netHeight / 2, 0);
        const post2 = post1.clone();
        post2.position.x = -TABLE.width / 2 - 0.05;
        netGroup.add(post1);
        netGroup.add(post2);
        tableGroup.add(netGroup);

        // Table Legs
        const legGeo = new THREE.CylinderGeometry(0.025, 0.025, TABLE.height - 0.05, 16);
        const legMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, metalness: 0.5 });
        const legPositions = [
            [-TABLE.width / 2 + 0.1, (TABLE.height - 0.05)/2, -TABLE.length / 2 + 0.15],
            [ TABLE.width / 2 - 0.1, (TABLE.height - 0.05)/2, -TABLE.length / 2 + 0.15],
            [-TABLE.width / 2 + 0.1, (TABLE.height - 0.05)/2,  TABLE.length / 2 - 0.15],
            [ TABLE.width / 2 - 0.1, (TABLE.height - 0.05)/2,  TABLE.length / 2 - 0.15]
        ];
        legPositions.forEach(pos => {
            const leg = new THREE.Mesh(legGeo, legMat);
            leg.position.set(...pos);
            leg.castShadow = true;
            tableGroup.add(leg);
        });

        // --- Paddle Construction Helper ---
        function createPaddle(rubberColor) {
            const group = new THREE.Group();
            
            // Blade / Rubber Face
            const bladeGeo = new THREE.CylinderGeometry(PADDLE_RADIUS, PADDLE_RADIUS, 0.018, 32);
            const rubberMat = new THREE.MeshStandardMaterial({ color: rubberColor, roughness: 0.4 });
            const blade = new THREE.Mesh(bladeGeo, rubberMat);
            blade.rotation.x = Math.PI / 2;
            blade.castShadow = true;
            group.add(blade);

            // Back rubber side (black for player, red for AI)
            const backMat = new THREE.MeshStandardMaterial({ color: rubberColor === 0xef4444 ? 0x0f172a : 0xef4444, roughness: 0.4 });
            const backBlade = new THREE.Mesh(bladeGeo, backMat);
            backBlade.rotation.x = -Math.PI / 2;
            backBlade.position.z = -0.002;
            group.add(backBlade);

            // Handle
            const handleGeo = new THREE.CylinderGeometry(0.016, 0.018, 0.13, 16);
            const handleMat = new THREE.MeshStandardMaterial({ color: 0x9a3412, roughness: 0.7 });
            const handle = new THREE.Mesh(handleGeo, handleMat);
            handle.position.y = -0.14;
            handle.castShadow = true;
            group.add(handle);

            return group;
        }

        const playerPaddle = createPaddle(0xef4444); // Red Rubber Player Paddle
        scene.add(playerPaddle);

        const aiPaddle = createPaddle(0x1e293b); // Black Rubber AI Paddle
        scene.add(aiPaddle);

        // 3D Ball
        const ballGeo = new THREE.SphereGeometry(BALL_RADIUS, 32, 32);
        const ballMat = new THREE.MeshStandardMaterial({ color: 0xfff7ed, roughness: 0.2 });
        const ballMesh = new THREE.Mesh(ballGeo, ballMat);
        ballMesh.castShadow = true;
        scene.add(ballMesh);

        // Ball Trail Particle Effect
        const trailCount = 8;
        const ballTrailMeshes = [];
        for(let i=0; i<trailCount; i++) {
            const tMat = new THREE.MeshBasicMaterial({ color: 0xfbbf24, transparent: true, opacity: 0 });
            const tMesh = new THREE.Mesh(ballGeo, tMat);
            scene.add(tMesh);
            ballTrailMeshes.push(tMesh);
        }
        let trailHistory = [];

        // Ball Physics Physics State Object
        const ballPhysics = {
            pos: new THREE.Vector3(0, TABLE.height + 0.2, TABLE.length / 2 - 0.2),
            vel: new THREE.Vector3(),
            spin: new THREE.Vector3(), // Topspin/Backspin & Sidespin
            isSmash: false
        };

        // Camera Views Setup
        function updateCameraTransform() {
            if (currentCameraView === 'player') {
                camera.position.set(0, TABLE.height + 0.6, TABLE.length / 2 + 1.25);
                camera.lookAt(0, TABLE.height + 0.1, -0.4);
            } else if (currentCameraView === 'quarter') {
                camera.position.set(1.8, TABLE.height + 1.2, 1.8);
                camera.lookAt(0, TABLE.height, 0);
            } else if (currentCameraView === 'side') {
                camera.position.set(2.4, TABLE.height + 0.4, 0);
                camera.lookAt(0, TABLE.height + 0.1, 0);
            }
        }
        updateCameraTransform();

        function setCameraView(view) {
            currentCameraView = view;
            document.querySelectorAll('.cam-btn').forEach(btn => {
                btn.className = 'cam-btn px-2.5 py-1 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-300 font-semibold transition';
            });
            document.getElementById(`cam-${view}`).className = 'cam-btn px-2.5 py-1 bg-blue-600 rounded-lg text-white font-bold transition';
            updateCameraTransform();
        }

        // ==========================================
        // 4. Game Logic & Serve Management
        // ==========================================
        const AI_CONFIGS = {
            easy: { speed: 4.5, error: 0.25, label: 'AI (쉬움)' },
            medium: { speed: 7.2, error: 0.12, label: 'AI (보통)' },
            hard: { speed: 10.5, error: 0.04, label: 'AI (어려움)' }
        };

        function selectDifficulty(diff) {
            difficulty = diff;
            document.querySelectorAll('.diff-btn').forEach(btn => {
                btn.className = 'diff-btn py-2.5 rounded-xl font-bold text-sm bg-slate-800 border border-slate-600 text-slate-300 hover:bg-slate-700 transition';
            });
            document.getElementById(`btn-${diff}`).className = 'diff-btn py-2.5 rounded-xl font-bold text-sm bg-blue-600 border border-blue-400 text-white shadow-lg transition';
            document.getElementById('ai-label').innerText = AI_CONFIGS[diff].label;
        }

        function updateServeBadges() {
            document.getElementById('player-serve-badge').classList.toggle('hidden', server !== 'player');
            document.getElementById('ai-serve-badge').classList.toggle('hidden', server !== 'ai');
        }

        function prepareServe() {
            gameState = 'SERVE';
            lastBounceSide = null;
            bounceCountThisTurn = 0;
            ballPhysics.spin.set(0,0,0);
            ballPhysics.isSmash = false;

            const prompt = document.getElementById('serve-prompt');
            const promptText = document.getElementById('serve-prompt-text');

            if (server === 'player') {
                ballPhysics.pos.set(0.15, TABLE.height + 0.18, TABLE.length / 2 - 0.1);
                ballPhysics.vel.set(0, 0, 0);
                promptText.innerText = '당신의 서브 순서입니다! (클릭/스윙하여 서브)';
                prompt.classList.remove('hidden');
            } else {
                ballPhysics.pos.set(-0.15, TABLE.height + 0.18, -TABLE.length / 2 + 0.1);
                ballPhysics.vel.set(0, 0, 0);
                promptText.innerText = 'AI의 서브 차례입니다...';
                prompt.classList.remove('hidden');

                // Trigger AI serve after short delay
                setTimeout(() => {
                    if (gameState === 'SERVE' && server === 'ai') {
                        executeAIServe();
                    }
                }, 1100);
            }
            updateServeBadges();
        }

        function executeAIServe() {
            gameState = 'PLAYING';
            document.getElementById('serve-prompt').classList.add('hidden');
            
            // AI serves ball to player side with bounce
            ballPhysics.vel.set(
                (Math.random() - 0.5) * 0.8,
                2.2,
                4.2
            );
            audio.playPaddleHit(false);
        }

        function startGame() {
            audio.init();
            playerScore = 0;
            aiScore = 0;
            rallyCount = 0;
            maxRallyCount = 0;
            smashCount = 0;
            server = 'player';
            totalServesCount = 0;

            updateScoreUI();
            document.getElementById('modal-start').classList.add('hidden');
            document.getElementById('modal-over').classList.add('hidden');

            prepareServe();
        }

        function restartGame() {
            startGame();
        }

        function updateScoreUI() {
            document.getElementById('player-score').innerText = playerScore;
            document.getElementById('ai-score').innerText = aiScore;
            document.getElementById('current-rally').innerText = rallyCount;
            document.getElementById('max-rally').innerText = maxRallyCount;

            const badge = document.getElementById('game-status-badge');
            if (playerScore >= 10 && aiScore >= 10) {
                badge.innerText = '듀스 (2점 차 승부)';
                badge.className = 'mt-1 inline-block px-3 py-0.5 rounded-full text-xs font-bold bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse';
            } else if (playerScore >= 10 || aiScore >= 10) {
                badge.innerText = '매치 포인트!';
                badge.className = 'mt-1 inline-block px-3 py-0.5 rounded-full text-xs font-bold bg-red-500/20 text-red-300 border border-red-500/30 animate-pulse';
            } else {
                badge.innerText = '11점 선승 (2점 차 승부)';
                badge.className = 'mt-1 inline-block px-3 py-0.5 rounded-full text-xs font-bold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
            }
        }

        function handlePointScore(winner) {
            if (gameState === 'SCORED' || gameState === 'OVER') return;
            gameState = 'SCORED';

            if (winner === 'player') {
                playerScore++;
                audio.playScore(true);
            } else {
                aiScore++;
                audio.playScore(false);
            }

            if (rallyCount > maxRallyCount) maxRallyCount = rallyCount;
            rallyCount = 0;
            updateScoreUI();

            // Check Serve alternation (every 2 points or every 1 point during deuce)
            totalServesCount++;
            const isDeuce = playerScore >= 10 && aiScore >= 10;
            if (isDeuce || totalServesCount % 2 === 0) {
                server = (server === 'player') ? 'ai' : 'player';
            }

            // Check Match Winner
            if ((playerScore >= 11 || aiScore >= 11) && Math.abs(playerScore - aiScore) >= 2) {
                gameState = 'OVER';
                const isPlayerWinner = playerScore > aiScore;
                
                const winnerIcon = document.getElementById('winner-icon');
                const winnerTitle = document.getElementById('winner-title');
                const winnerDesc = document.getElementById('winner-desc');

                if (isPlayerWinner) {
                    winnerIcon.className = 'w-20 h-20 rounded-full bg-emerald-500/20 border-2 border-emerald-400 flex items-center justify-center mb-4 text-emerald-400 text-4xl shadow-xl';
                    winnerIcon.innerHTML = '<i class="fa-solid fa-trophy"></i>';
                    winnerTitle.innerText = '승리하셨습니다!';
                    winnerDesc.innerText = '정교한 라켓 컨트롤과 강력한 타이밍으로 승리했습니다!';
                } else {
                    winnerIcon.className = 'w-20 h-20 rounded-full bg-red-500/20 border-2 border-red-400 flex items-center justify-center mb-4 text-red-400 text-4xl shadow-xl';
                    winnerIcon.innerHTML = '<i class="fa-solid fa-face-frown"></i>';
                    winnerTitle.innerText = '패배하였습니다';
                    winnerDesc.innerText = 'AI의 까다로운 리턴에 고전했습니다. 다시 도전해보세요!';
                }

                document.getElementById('final-score').innerText = `${playerScore} - ${aiScore}`;
                document.getElementById('final-rally').innerText = `${maxRallyCount} 회`;
                document.getElementById('final-smashes').innerText = `${smashCount} 회`;
                document.getElementById('modal-over').classList.remove('hidden');
            } else {
                setTimeout(() => {
                    prepareServe();
                }, 1300);
            }
        }

        // ==========================================
        // 5. Input Controls & Raycasting
        // ==========================================
        const raycaster = new THREE.Raycaster();
        const inputPlane = new THREE.Plane(new THREE.Vector3(0, 0, 1), -TABLE.length / 2 - 0.1);

        function onPointerMove(event) {
            mouse2D.x = (event.clientX / window.innerWidth) * 2 - 1;
            mouse2D.y = -(event.clientY / window.innerHeight) * 2 + 1;

            raycaster.setFromCamera(mouse2D, camera);
            const intersectPoint = new THREE.Vector3();
            raycaster.ray.intersectPlane(inputPlane, intersectPoint);

            if (intersectPoint) {
                // Limit Player paddle movement within playable zone
                targetPaddlePos.x = THREE.MathUtils.clamp(intersectPoint.x, -TABLE.width / 2 - 0.3, TABLE.width / 2 + 0.3);
                targetPaddlePos.y = THREE.MathUtils.clamp(intersectPoint.y, TABLE.height + 0.05, TABLE.height + 0.7);
                targetPaddlePos.z = THREE.MathUtils.clamp(intersectPoint.z, 0.2, TABLE.length / 2 + 0.6);
            }
        }

        window.addEventListener('pointermove', onPointerMove);

        // Serve trigger on click/tap
        window.addEventListener('pointerdown', () => {
            if (gameState === 'SERVE' && server === 'player') {
                gameState = 'PLAYING';
                document.getElementById('serve-prompt').classList.add('hidden');
                
                // Serve forward impulse
                ballPhysics.vel.set(
                    paddleVelocity.x * 0.5,
                    2.0 + paddleVelocity.y * 0.4,
                    -4.8 - Math.abs(paddleVelocity.z) * 0.5
                );
                audio.playPaddleHit(false);
            }
        });

        // ==========================================
        // 6. Physics Simulation Loop
        // ==========================================
        const clock = new THREE.Clock();

        function updatePhysics(dt) {
            if (gameState !== 'PLAYING') return;

            const gravity = -9.8;
            
            // Magnus force effect from spin (Topspin pulls down, Sidespin curves X)
            const magnusX = ballPhysics.spin.y * 0.003;
            const magnusY = -ballPhysics.spin.x * 0.004;

            ballPhysics.vel.x += magnusX * dt;
            ballPhysics.vel.y += (gravity + magnusY) * dt;
            ballPhysics.pos.addScaledVector(ballPhysics.vel, dt);

            // Trail positioning
            trailHistory.unshift(ballPhysics.pos.clone());
            if (trailHistory.length > trailCount) trailHistory.pop();

            trailHistory.forEach((pos, idx) => {
                ballTrailMeshes[idx].position.copy(pos);
                ballTrailMeshes[idx].material.opacity = ballPhysics.isSmash ? (1 - idx / trailCount) * 0.6 : 0;
            });

            // --- Table Bounce Physics ---
            const onTableX = Math.abs(ballPhysics.pos.x) <= TABLE.width / 2 + BALL_RADIUS;
            const onTableZ = Math.abs(ballPhysics.pos.z) <= TABLE.length / 2 + BALL_RADIUS;
            
            if (onTableX && onTableZ && ballPhysics.pos.y - BALL_RADIUS <= TABLE.height) {
                // Table Surface Collision
                if (ballPhysics.vel.y < 0) {
                    ballPhysics.pos.y = TABLE.height + BALL_RADIUS;
                    ballPhysics.vel.y = -ballPhysics.vel.y * 0.85; // Restitution
                    
                    // Friction alters spin
                    ballPhysics.vel.x += ballPhysics.spin.y * 0.02;
                    ballPhysics.spin.multiplyScalar(0.5);

                    audio.playTableBounce();

                    // Track table side of bounce
                    const currentSide = ballPhysics.pos.z > 0 ? 'player' : 'ai';
                    if (lastBounceSide === currentSide) {
                        bounceCountThisTurn++;
                    } else {
                        lastBounceSide = currentSide;
                        bounceCountThisTurn = 1;
                    }

                    // Double bounce rule violation
                    if (bounceCountThisTurn >= 2) {
                        handlePointScore(currentSide === 'player' ? 'ai' : 'player');
                    }
                }
            }

            // --- Net Collision ---
            const netZ = 0;
            if (Math.abs(ballPhysics.pos.z) < 0.04 && Math.abs(ballPhysics.pos.x) <= TABLE.width / 2 + 0.05) {
                if (ballPhysics.pos.y <= TABLE.height + TABLE.netHeight + BALL_RADIUS) {
                    ballPhysics.vel.z *= -0.4; // Bounce back from net
                    ballPhysics.vel.y *= 0.5;
                    audio.playTableBounce();
                }
            }

            // --- Out of Bounds / Floor hit ---
            if (ballPhysics.pos.y < TABLE.height - 0.4 || Math.abs(ballPhysics.pos.z) > TABLE.length / 2 + 1.2) {
                // Point scoring logic based on last bounce
                if (lastBounceSide === 'ai') {
                    handlePointScore('player');
                } else if (lastBounceSide === 'player') {
                    handlePointScore('ai');
                } else {
                    // Flew directly out without bouncing on receiver table
                    handlePointScore(ballPhysics.vel.z > 0 ? 'ai' : 'player');
                }
            }

            // --- Player Paddle Collision ---
            const distPlayer = ballPhysics.pos.distanceTo(playerPaddle.position);
            if (distPlayer < PADDLE_RADIUS + BALL_RADIUS + 0.04 && ballPhysics.vel.z > 0) {
                const swingSpeed = paddleVelocity.length();
                const isSmash = swingSpeed > 3.5 || paddleVelocity.z < -2.0;
                
                if (isSmash) smashCount++;

                ballPhysics.isSmash = isSmash;
                const returnSpeedZ = isSmash ? -8.5 : -5.8;

                ballPhysics.vel.set(
                    (ballPhysics.pos.x - playerPaddle.position.x) * 4.0 + paddleVelocity.x * 0.4,
                    Math.max(1.8, paddleVelocity.y * 0.6 + 2.2),
                    returnSpeedZ
                );

                // Add spin based on paddle movement
                ballPhysics.spin.set(paddleVelocity.y * 12.0, paddleVelocity.x * 12.0, 0);

                rallyCount++;
                if (rallyCount > maxRallyCount) maxRallyCount = rallyCount;
                updateScoreUI();

                audio.playPaddleHit(isSmash);
            }

            // --- AI Paddle & Movement Logic ---
            const aiConfig = AI_CONFIGS[difficulty];
            const aiTarget = new THREE.Vector3();

            if (ballPhysics.vel.z < 0) { // Ball coming towards AI
                // Predict intercept point
                const timeToAI = Math.abs((ballPhysics.pos.z - (-TABLE.length / 2)) / ballPhysics.vel.z);
                aiTarget.x = THREE.MathUtils.clamp(
                    ballPhysics.pos.x + ballPhysics.vel.x * timeToAI + (Math.sin(Date.now() * 0.005) * aiConfig.error),
                    -TABLE.width / 2, TABLE.width / 2
                );
                aiTarget.y = THREE.MathUtils.clamp(TABLE.height + 0.15 + (ballPhysics.pos.y - TABLE.height) * 0.5, TABLE.height + 0.05, TABLE.height + 0.5);
                aiTarget.z = -TABLE.length / 2 - 0.15;
            } else {
                // Neutral AI position
                aiTarget.set(0, TABLE.height + 0.2, -TABLE.length / 2 - 0.2);
            }

            aiPaddle.position.lerp(aiTarget, dt * aiConfig.speed);

            // AI Collision check
            const distAI = ballPhysics.pos.distanceTo(aiPaddle.position);
            if (distAI < PADDLE_RADIUS + BALL_RADIUS + 0.04 && ballPhysics.vel.z < 0) {
                const isAISmash = difficulty === 'hard' && Math.random() < 0.35;
                ballPhysics.isSmash = isAISmash;
                
                const returnSpeedZ = isAISmash ? 8.2 : 5.6;
                ballPhysics.vel.set(
                    (ballPhysics.pos.x - aiPaddle.position.x) * 3.8,
                    2.0 + Math.random() * 0.8,
                    returnSpeedZ
                );

                rallyCount++;
                if (rallyCount > maxRallyCount) maxRallyCount = rallyCount;
                updateScoreUI();

                audio.playPaddleHit(isAISmash);
            }
        }

        // ==========================================
        // 7. Render Loop & Window Resize
        // ==========================================
        function animate() {
            requestAnimationFrame(animate);

            const dt = Math.min(clock.getDelta(), 0.033);

            // Calculate Player Paddle Velocity
            paddleVelocity.subVectors(targetPaddlePos, lastPaddlePos).divideScalar(dt);
            lastPaddlePos.copy(targetPaddlePos);

            // Smoothly move Player Paddle mesh
            playerPaddle.position.lerp(targetPaddlePos, 0.4);
            // Dynamic paddle tilt based on swing
            playerPaddle.rotation.z = -paddleVelocity.x * 0.08;
            playerPaddle.rotation.x = Math.PI / 6 - paddleVelocity.z * 0.05;

            // Physics step
            updatePhysics(dt);

            // Update 3D Ball mesh position
            ballMesh.position.copy(ballPhysics.pos);

            renderer.render(scene, camera);
        }

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        function toggleMute() {
            audio.muted = !audio.muted;
            const soundIcon = document.getElementById('icon-sound');
            const soundText = document.getElementById('text-sound');

            if (audio.muted) {
                soundIcon.className = 'fa-solid fa-volume-xmark';
                soundText.innerText = '효과음 OFF';
            } else {
                audio.init();
                soundIcon.className = 'fa-solid fa-volume-high';
                soundText.innerText = '효과음 ON';
            }
        }

        // Start animation loop on window load
        window.onload = () => {
            selectDifficulty('medium');
            animate();
        };
    </script>
</body>
</html>
