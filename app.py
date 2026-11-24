<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>리얼 2D 탁구 게임 (Table Tennis)</title>
    <!-- Tailwind CSS for UI controls & responsive styling -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- FontAwesome icons for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Pretendard:wght@400;600;800&display=swap');
        
        body {
            font-family: 'Pretendard', sans-serif;
            background-color: #0f172a;
            color: #f8fafc;
            user-select: none;
            -webkit-user-select: none;
            touch-action: none;
            overflow: hidden;
        }

        #game-canvas {
            background: radial-gradient(circle at center, #1e293b 0%, #0f172a 100%);
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.4);
        }

        /* Glassmorphism styling for panels */
        .glass-panel {
            background: rgba(30, 41, 59, 0.75);
            backdrop-filter: blur(12px);
            -webkit-backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        /* Pulsing animation for smash warning */
        @keyframes pulse-fast {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.8; transform: scale(1.05); }
        }
        .animate-pulse-fast {
            animation: pulse-fast 0.6s infinite;
        }
    </style>
</head>
<body class="w-screen h-screen flex flex-col items-center justify-between p-2 md:p-4">

    <!-- Top Navigation / Scorebar -->
    <header class="w-full max-w-4xl glass-panel rounded-2xl p-3 md:p-4 flex items-center justify-between z-10 shadow-lg">
        <!-- Player Info (Left/Bottom paddle) -->
        <div class="flex items-center space-x-3">
            <div class="w-10 h-10 md:w-12 md:h-12 rounded-full bg-blue-600 flex items-center justify-center font-bold text-lg border-2 border-blue-300 shadow">
                <i class="fa-solid fa-user"></i>
            </div>
            <div>
                <div class="text-xs text-blue-300 font-semibold uppercase tracking-wider">Player</div>
                <div class="text-xl md:text-3xl font-extrabold text-blue-400" id="player-score">0</div>
            </div>
        </div>

        <!-- Game Center Info (Rally & Match Info) -->
        <div class="text-center">
            <div class="text-xs md:text-sm text-slate-400 font-medium">최고 랠리: <span id="max-rally" class="text-amber-400 font-bold">0</span></div>
            <div class="text-lg md:text-2xl font-black text-white tracking-widest my-0.5">
                랠리 <span id="current-rally" class="text-emerald-400">0</span>
            </div>
            <div id="game-status-badge" class="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30">
                11점 내기 (듀스 2점차)
            </div>
        </div>

        <!-- AI Info (Right/Top paddle) -->
        <div class="flex items-center space-x-3 text-right">
            <div>
                <div class="text-xs text-red-300 font-semibold uppercase tracking-wider" id="ai-difficulty-label">AI (보통)</div>
                <div class="text-xl md:text-3xl font-extrabold text-red-400" id="ai-score">0</div>
            </div>
            <div class="w-10 h-10 md:w-12 md:h-12 rounded-full bg-red-600 flex items-center justify-center font-bold text-lg border-2 border-red-300 shadow">
                <i class="fa-solid fa-robot"></i>
            </div>
        </div>
    </header>

    <!-- Canvas Container -->
    <main class="relative w-full max-w-4xl flex-1 my-2 flex items-center justify-center overflow-hidden">
        <canvas id="game-canvas" class="rounded-2xl border-4 border-slate-700/50 w-full h-full object-contain"></canvas>

        <!-- Overlay: Start / Difficulty Select Modal -->
        <div id="modal-start" class="absolute inset-0 glass-panel rounded-2xl flex flex-col items-center justify-center p-6 text-center z-20">
            <div class="w-20 h-20 bg-emerald-500/20 border-2 border-emerald-400 rounded-full flex items-center justify-center mb-4 text-emerald-400 text-4xl shadow-lg animate-pulse-fast">
                <i class="fa-solid fa-table-tennis-paddle-ball"></i>
            </div>
            <h1 class="text-3xl md:text-5xl font-black text-white mb-2 tracking-tight">리얼 탁구 시뮬레이터</h1>
            <p class="text-slate-300 text-sm md:text-base max-w-md mb-6">
                마우스 / 터치 드래그 또는 방향키(W, S)로 패들을 조작하세요.<br>
                패들을 빠른 속도로 휘둘러 <strong>회전(Spin)</strong> 및 <strong>스매시(Smash)</strong> 공격을 구사할 수 있습니다.
            </p>

            <div class="w-full max-w-xs space-y-3 mb-6">
                <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider text-left">AI 난이도 선택</label>
                <div class="grid grid-cols-3 gap-2">
                    <button type="button" onclick="selectDifficulty('easy')" id="btn-easy" class="diff-btn py-2.5 rounded-xl font-bold text-sm bg-slate-800 border border-slate-600 text-slate-300 hover:bg-slate-700 transition">쉬움</button>
                    <button type="button" onclick="selectDifficulty('medium')" id="btn-medium" class="diff-btn py-2.5 rounded-xl font-bold text-sm bg-blue-600 border border-blue-400 text-white shadow-lg transition">보통</button>
                    <button type="button" onclick="selectDifficulty('hard')" id="btn-hard" class="diff-btn py-2.5 rounded-xl font-bold text-sm bg-slate-800 border border-slate-600 text-slate-300 hover:bg-slate-700 transition">어려움</button>
                </div>
            </div>

            <button onclick="startGame()" class="w-full max-w-xs py-4 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-black text-lg rounded-xl shadow-xl transition transform hover:scale-105 active:scale-95 flex items-center justify-center space-x-2">
                <i class="fa-solid fa-play"></i>
                <span>게임 시작하기</span>
            </button>
        </div>

        <!-- Overlay: Match Over Modal -->
        <div id="modal-over" class="hidden absolute inset-0 glass-panel rounded-2xl flex flex-col items-center justify-center p-6 text-center z-20">
            <div id="winner-icon" class="w-20 h-20 rounded-full flex items-center justify-center mb-4 text-4xl shadow-lg"></div>
            <h2 id="winner-title" class="text-3xl md:text-4xl font-black text-white mb-2"></h2>
            <p id="winner-desc" class="text-slate-300 text-sm md:text-base mb-6"></p>

            <div class="bg-slate-800/80 rounded-xl p-4 w-full max-w-xs mb-6 border border-slate-700 text-left space-y-2 text-sm">
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
    </main>

    <!-- Bottom Controls & Instruction Banner -->
    <footer class="w-full max-w-4xl glass-panel rounded-2xl p-2.5 md:p-3 flex items-center justify-between text-xs text-slate-400">
        <div class="flex items-center space-x-4">
            <span class="hidden md:inline"><i class="fa-solid fa-gamepad mr-1 text-slate-300"></i> 조작: <kbd class="px-1.5 py-0.5 bg-slate-800 rounded border border-slate-600 text-slate-200">W</kbd>/<kbd class="px-1.5 py-0.5 bg-slate-800 rounded border border-slate-600 text-slate-200">S</kbd> 키, 방향키, 또는 마우스/터치 드래그</span>
            <span class="md:hidden"><i class="fa-solid fa-hand-pointer mr-1 text-slate-300"></i> 드래그 / 화살표 조작</span>
        </div>
        <div class="flex items-center space-x-3">
            <button onclick="toggleMute()" id="btn-sound" class="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg border border-slate-700 text-slate-200 font-semibold transition flex items-center space-x-1.5">
                <i class="fa-solid fa-volume-high" id="icon-sound"></i>
                <span id="text-sound">효과음 ON</span>
            </button>
        </div>
    </footer>

    <!-- Game Script logic -->
    <script>
        // --- Web Audio API Synth Engine ---
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
                    
                    const freq = isSmash ? 650 : 420;
                    osc.frequency.setValueAtTime(freq, this.ctx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(120, this.ctx.currentTime + (isSmash ? 0.15 : 0.08));

                    gain.gain.setValueAtTime(isSmash ? 0.4 : 0.25, this.ctx.currentTime);
                    gain.gain.exponentialRampToValueAtTime(0.001, this.ctx.currentTime + (isSmash ? 0.15 : 0.08));

                    osc.connect(gain);
                    gain.connect(this.ctx.destination);

                    osc.start();
                    osc.stop(this.ctx.currentTime + (isSmash ? 0.15 : 0.08));
                } catch(e){}
            }

            playTableBounce() {
                if (this.muted || !this.ctx) return;
                try {
                    const osc = this.ctx.createOscillator();
                    const gain = this.ctx.createGain();
                    osc.type = 'triangle';
                    
                    osc.frequency.setValueAtTime(280, this.ctx.currentTime);
                    osc.frequency.exponentialRampToValueAtTime(80, this.ctx.currentTime + 0.06);

                    gain.gain.setValueAtTime(0.2, this.ctx.currentTime);
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
                        gain.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.1 + 0.2);

                        osc.connect(gain);
                        gain.connect(this.ctx.destination);

                        osc.start(now + idx * 0.1);
                        osc.stop(now + idx * 0.1 + 0.2);
                    });
                } catch(e){}
            }
        }

        const audio = new SoundEngine();

        // --- Game Setup & State ---
        const canvas = document.getElementById('game-canvas');
        const ctx = canvas.getContext('2d');

        // Virtual internal resolution for consistent physics & crisp graphics
        const V_WIDTH = 1200;
        const V_HEIGHT = 700;
        canvas.width = V_WIDTH;
        canvas.height = V_HEIGHT;

        let gameState = 'START'; // 'START', 'PLAYING', 'SCORED', 'OVER'
        let difficulty = 'medium'; // 'easy', 'medium', 'hard'

        let playerScore = 0;
        let aiScore = 0;
        let rallyCount = 0;
        let maxRallyCount = 0;
        let smashCount = 0;

        // Input state
        const keys = { ArrowUp: false, ArrowDown: false, KeyW: false, KeyS: false };
        let touchY = null;
        let lastPointerY = V_HEIGHT / 2;
        let paddleVelocityY = 0;

        // Table Tennis Table geometry
        const tableMargin = 80;
        const table = {
            x: tableMargin,
            y: tableMargin,
            width: V_WIDTH - tableMargin * 2,
            height: V_HEIGHT - tableMargin * 2,
            netWidth: 8
        };

        // Paddle Dimensions
        const paddleWidth = 16;
        const paddleHeight = 110;

        // Player (Left side)
        const player = {
            x: table.x + 25,
            y: V_HEIGHT / 2 - paddleHeight / 2,
            width: paddleWidth,
            height: paddleHeight,
            vy: 0,
            color: '#3b82f6',
            rubberColor: '#ef4444'
        };

        // AI (Right side)
        const ai = {
            x: table.x + table.width - 25 - paddleWidth,
            y: V_HEIGHT / 2 - paddleHeight / 2,
            width: paddleWidth,
            height: paddleHeight,
            vy: 0,
            speed: 7,
            color: '#ef4444',
            rubberColor: '#1e293b',
            targetY: V_HEIGHT / 2 - paddleHeight / 2,
            reactionDelay: 0
        };

        // Ball Physics State
        const ball = {
            x: V_WIDTH / 2,
            y: V_HEIGHT / 2,
            radius: 12,
            vx: 0,
            vy: 0,
            spin: 0, // Curve spin effect (Magnus effect)
            speed: 0,
            lastHit: null, // 'player' or 'ai'
            isSmash: false,
            trail: []
        };

        // Visual FX Particles
        let particles = [];

        function createSparkles(x, y, color, count = 12) {
            for (let i = 0; i < count; i++) {
                const angle = Math.random() * Math.PI * 2;
                const speed = 2 + Math.random() * 6;
                particles.push({
                    x, y,
                    vx: Math.cos(angle) * speed,
                    vy: Math.sin(angle) * speed,
                    radius: 2 + Math.random() * 3,
                    color: color,
                    life: 1.0,
                    decay: 0.03 + Math.random() * 0.04
                });
            }
        }

        // --- Difficulty Configurations ---
        const AI_CONFIGS = {
            easy: { speed: 6.2, errorMargin: 45, spinReaction: 0.2, label: 'AI (쉬움)' },
            medium: { speed: 8.8, errorMargin: 20, spinReaction: 0.5, label: 'AI (보통)' },
            hard: { speed: 12.5, errorMargin: 5, spinReaction: 0.85, label: 'AI (어려움)' }
        };

        function selectDifficulty(diff) {
            difficulty = diff;
            document.querySelectorAll('.diff-btn').forEach(btn => {
                btn.className = 'diff-btn py-2.5 rounded-xl font-bold text-sm bg-slate-800 border border-slate-600 text-slate-300 hover:bg-slate-700 transition';
            });

            const activeBtn = document.getElementById(`btn-${diff}`);
            if (activeBtn) {
                activeBtn.className = 'diff-btn py-2.5 rounded-xl font-bold text-sm bg-blue-600 border border-blue-400 text-white shadow-lg transition';
            }
            document.getElementById('ai-difficulty-label').innerText = AI_CONFIGS[diff].label;
        }

        // --- Game Logic Functions ---
        function resetBall(server = 'player') {
            ball.x = V_WIDTH / 2;
            ball.y = V_HEIGHT / 2;
            ball.spin = 0;
            ball.isSmash = false;
            ball.trail = [];

            const baseSpeed = 8;
            const dir = server === 'player' ? 1 : -1;
            const angle = (Math.random() - 0.5) * 0.6; // Slight random Y angle

            ball.vx = dir * baseSpeed * Math.cos(angle);
            ball.vy = baseSpeed * Math.sin(angle);
            ball.speed = baseSpeed;
            ball.lastHit = null;
        }

        function startGame() {
            audio.init();
            playerScore = 0;
            aiScore = 0;
            rallyCount = 0;
            maxRallyCount = 0;
            smashCount = 0;

            updateScoreUI();
            document.getElementById('modal-start').classList.add('hidden');
            document.getElementById('modal-over').classList.add('hidden');

            gameState = 'PLAYING';
            resetBall(Math.random() > 0.5 ? 'player' : 'ai');
        }

        function restartGame() {
            startGame();
        }

        function updateScoreUI() {
            document.getElementById('player-score').innerText = playerScore;
            document.getElementById('ai-score').innerText = aiScore;
            document.getElementById('current-rally').innerText = rallyCount;
            document.getElementById('max-rally').innerText = maxRallyCount;

            // Deuce or Match point indicator
            const statusBadge = document.getElementById('game-status-badge');
            if (playerScore >= 10 && aiScore >= 10) {
                statusBadge.innerText = '듀스 (2점차 승부)';
                statusBadge.className = 'inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-amber-500/20 text-amber-300 border border-amber-500/30 animate-pulse';
            } else if (playerScore >= 10 || aiScore >= 10) {
                statusBadge.innerText = '매치 포인트!';
                statusBadge.className = 'inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-red-500/20 text-red-300 border border-red-500/30 animate-pulse';
            } else {
                statusBadge.innerText = '11점 내기 (듀스 2점차)';
                statusBadge.className = 'inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30';
            }
        }

        function checkMatchWinner() {
            // Standard 11 points rule (with deuce rule: 2 points lead required)
            if ((playerScore >= 11 || aiScore >= 11) && Math.abs(playerScore - aiScore) >= 2) {
                gameState = 'OVER';
                const isPlayerWinner = playerScore > aiScore;

                audio.playScore(isPlayerWinner);

                const winnerIcon = document.getElementById('winner-icon');
                const winnerTitle = document.getElementById('winner-title');
                const winnerDesc = document.getElementById('winner-desc');

                if (isPlayerWinner) {
                    winnerIcon.className = 'w-20 h-20 rounded-full bg-emerald-500/20 border-2 border-emerald-400 flex items-center justify-center mb-4 text-emerald-400 text-4xl shadow-lg';
                    winnerIcon.innerHTML = '<i class="fa-solid fa-trophy"></i>';
                    winnerTitle.innerText = '승리하였습니다!';
                    winnerDesc.innerText = '뛰어난 컨트롤과 감각적인 스핀으로 경기를 지배했습니다!';
                } else {
                    winnerIcon.className = 'w-20 h-20 rounded-full bg-red-500/20 border-2 border-red-400 flex items-center justify-center mb-4 text-red-400 text-4xl shadow-lg';
                    winnerIcon.innerHTML = '<i class="fa-solid fa-face-frown"></i>';
                    winnerTitle.innerText = '패배하였습니다';
                    winnerDesc.innerText = 'AI의 날카로운 리턴에 고전했습니다. 다시 도전해보세요!';
                }

                document.getElementById('final-score').innerText = `${playerScore} - ${aiScore}`;
                document.getElementById('final-rally').innerText = `${maxRallyCount} 회`;
                document.getElementById('final-smashes').innerText = `${smashCount} 회`;

                document.getElementById('modal-over').classList.remove('hidden');
            }
        }

        function handlePointScore(winner) {
            if (winner === 'player') {
                playerScore++;
                audio.playScore(true);
                createSparkles(table.x + table.width, ball.y, '#3b82f6', 25);
            } else {
                aiScore++;
                audio.playScore(false);
                createSparkles(table.x, ball.y, '#ef4444', 25);
            }

            if (rallyCount > maxRallyCount) {
                maxRallyCount = rallyCount;
            }
            rallyCount = 0;

            updateScoreUI();
            checkMatchWinner();

            if (gameState !== 'OVER') {
                gameState = 'SCORED';
                setTimeout(() => {
                    if (gameState === 'SCORED') {
                        gameState = 'PLAYING';
                        resetBall(winner === 'player' ? 'ai' : 'player');
                    }
                }, 1200);
            }
        }

        // --- Update & Physics Simulation ---
        function updatePlayer() {
            let prevY = player.y;

            // Keyboard movement
            const speed = 9;
            if (keys.ArrowUp || keys.KeyW) {
                player.y -= speed;
            }
            if (keys.ArrowDown || keys.KeyS) {
                player.y += speed;
            }

            // Pointer (Mouse / Touch) Movement interpolation
            if (touchY !== null) {
                const targetY = touchY - player.height / 2;
                player.y += (targetY - player.y) * 0.35;
            }

            // Clamp inside table boundary
            player.y = Math.max(table.y, Math.min(table.y + table.height - player.height, player.y));
            paddleVelocityY = player.y - prevY;
        }

        function updateAI() {
            const config = AI_CONFIGS[difficulty];
            const aiCenter = ai.y + ai.height / 2;

            // AI recalculates target with prediction & mistake margin
            if (ball.vx > 0) { // Ball moving towards AI
                // Simple bounce trajectory prediction
                let predictedY = ball.y + (ball.vy / Math.max(1, ball.vx)) * (ai.x - ball.x);
                // Clamp prediction
                predictedY = Math.max(table.y, Math.min(table.y + table.height, predictedY));
                
                // Add error offset based on difficulty
                const error = (Math.sin(Date.now() * 0.005) * config.errorMargin);
                ai.targetY = predictedY - ai.height / 2 + error;
            } else {
                // Return to center slowly
                ai.targetY = V_HEIGHT / 2 - ai.height / 2;
            }

            // Move AI towards targetY
            const diffY = ai.targetY - ai.y;
            const moveAmt = Math.min(Math.abs(diffY), config.speed) * Math.sign(diffY);
            ai.y += moveAmt;

            // Clamp
            ai.y = Math.max(table.y, Math.min(table.y + table.height - ai.height, ai.y));
        }

        function updateBall() {
            if (gameState !== 'PLAYING') return;

            // Apply Spin Magnus force (curve effect)
            ball.vy += ball.spin * 0.12;

            // Update Ball position
            ball.x += ball.vx;
            ball.y += ball.vy;

            // Ball Trail history
            ball.trail.push({ x: ball.x, y: ball.y, radius: ball.radius });
            if (ball.trail.length > 10) ball.trail.shift();

            // Table top / bottom edge collision (Bounce sound & curve dampening)
            if (ball.y - ball.radius <= table.y) {
                ball.y = table.y + ball.radius;
                ball.vy *= -0.95;
                ball.spin *= 0.5;
                audio.playTableBounce();
            } else if (ball.y + ball.radius >= table.y + table.height) {
                ball.y = table.y + table.height - ball.radius;
                ball.vy *= -0.95;
                ball.spin *= 0.5;
                audio.playTableBounce();
            }

            // Net Collision (Center line)
            const netX = V_WIDTH / 2;
            if (Math.abs(ball.x - netX) < table.netWidth / 2 + ball.radius) {
                // If ball is low (near net height simulation)
                if (Math.random() < 0.15) { // Occasional net clip
                    ball.vx *= -0.5;
                    ball.spin = 0;
                    audio.playTableBounce();
                    createSparkles(netX, ball.y, '#ffffff', 8);
                }
            }

            // --- Player Paddle Collision ---
            if (
                ball.vx < 0 &&
                ball.x - ball.radius <= player.x + player.width &&
                ball.x + ball.radius >= player.x &&
                ball.y >= player.y - 10 &&
                ball.y <= player.y + player.height + 10
            ) {
                ball.x = player.x + player.width + ball.radius;

                // Calculate relative hit position (-1: top, 0: center, 1: bottom)
                const relativeHit = (ball.y - (player.y + player.height / 2)) / (player.height / 2);
                
                // Spin & Speed calculation based on paddle swipe velocity
                const isSmash = Math.abs(paddleVelocityY) > 6 || Math.abs(relativeHit) > 0.8;
                const speedBoost = isSmash ? 1.35 : 1.08;

                if (isSmash) smashCount++;

                ball.spin = paddleVelocityY * 0.45;
                
                // Return angle
                const bounceAngle = relativeHit * (Math.PI / 3.5);
                const currentSpeed = Math.min(22, Math.max(9, Math.hypot(ball.vx, ball.vy) * speedBoost));

                ball.vx = Math.cos(bounceAngle) * currentSpeed;
                ball.vy = Math.sin(bounceAngle) * currentSpeed + (paddleVelocityY * 0.3);
                ball.speed = currentSpeed;
                ball.isSmash = isSmash;
                ball.lastHit = 'player';

                rallyCount++;
                if (rallyCount > maxRallyCount) maxRallyCount = rallyCount;
                updateScoreUI();

                audio.playPaddleHit(isSmash);
                createSparkles(ball.x, ball.y, isSmash ? '#fbbf24' : '#60a5fa', isSmash ? 18 : 10);
            }

            // --- AI Paddle Collision ---
            if (
                ball.vx > 0 &&
                ball.x + ball.radius >= ai.x &&
                ball.x - ball.radius <= ai.x + ai.width &&
                ball.y >= ai.y - 10 &&
                ball.y <= ai.y + ai.height + 10
            ) {
                ball.x = ai.x - ball.radius;

                const relativeHit = (ball.y - (ai.y + ai.height / 2)) / (ai.height / 2);
                const config = AI_CONFIGS[difficulty];
                
                // AI smash back if hard mode and good position
                const isSmash = difficulty === 'hard' && Math.random() < 0.35;
                const speedBoost = isSmash ? 1.3 : 1.05;

                const bounceAngle = relativeHit * (Math.PI / 3.8);
                const currentSpeed = Math.min(21, Math.max(9, Math.hypot(ball.vx, ball.vy) * speedBoost));

                ball.vx = -Math.cos(bounceAngle) * currentSpeed;
                ball.vy = Math.sin(bounceAngle) * currentSpeed;
                ball.spin = (Math.random() - 0.5) * 4 * config.spinReaction;
                ball.speed = currentSpeed;
                ball.isSmash = isSmash;
                ball.lastHit = 'ai';

                rallyCount++;
                if (rallyCount > maxRallyCount) maxRallyCount = rallyCount;
                updateScoreUI();

                audio.playPaddleHit(isSmash);
                createSparkles(ball.x, ball.y, isSmash ? '#fbbf24' : '#f87171', isSmash ? 18 : 10);
            }

            // --- Out of bounds / Scoring ---
            if (ball.x < table.x - 40) {
                // Ball passed player (AI scores)
                handlePointScore('ai');
            } else if (ball.x > table.x + table.width + 40) {
                // Ball passed AI (Player scores)
                handlePointScore('player');
            }
        }

        function updateParticles() {
            for (let i = particles.length - 1; i >= 0; i--) {
                const p = particles[i];
                p.x += p.vx;
                p.y += p.vy;
                p.life -= p.decay;
                if (p.life <= 0) {
                    particles.splice(i, 1);
                }
            }
        }

        // --- Render Functions ---
        function drawTable() {
            // Outer Floor Dark Vignette background already in canvas background

            // Table Outer Blue Border & Surface Shadow
            ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
            ctx.shadowBlur = 30;
            ctx.shadowOffsetY = 15;

            // Tournament Blue Table Surface
            ctx.fillStyle = '#1e40af'; // Rich tournament blue
            ctx.beginPath();
            ctx.roundRect(table.x, table.y, table.width, table.height, 16);
            ctx.fill();

            ctx.shadowColor = 'transparent'; // Reset shadow

            // White Outer Boundary Lines
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 4;
            ctx.strokeRect(table.x + 4, table.y + 4, table.width - 8, table.height - 8);

            // Center White Line (Horizontal division line)
            ctx.strokeStyle = 'rgba(255, 255, 255, 0.4)';
            ctx.lineWidth = 2;
            ctx.setLineDash([8, 6]);
            ctx.beginPath();
            ctx.moveTo(table.x + 4, V_HEIGHT / 2);
            ctx.lineTo(table.x + table.width - 4, V_HEIGHT / 2);
            ctx.stroke();
            ctx.setLineDash([]); // Reset dash

            // Center Net (Vertical dark line with white posts)
            const netX = V_WIDTH / 2;
            ctx.fillStyle = 'rgba(15, 23, 42, 0.8)';
            ctx.fillRect(netX - table.netWidth / 2, table.y - 12, table.netWidth, table.height + 24);

            // Net Top Line Highlight
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(netX, table.y - 12);
            ctx.lineTo(netX, table.y + table.height + 12);
            ctx.stroke();
        }

        function drawPaddles() {
            // Draw Player Paddle (Left)
            ctx.shadowColor = 'rgba(0, 0, 0, 0.4)';
            ctx.shadowBlur = 10;
            ctx.shadowOffsetX = -5;

            // Wood handle & rubber
            ctx.fillStyle = player.rubberColor;
            ctx.beginPath();
            ctx.roundRect(player.x, player.y, player.width, player.height, 8);
            ctx.fill();

            // Inner wood border accent
            ctx.fillStyle = player.color;
            ctx.fillRect(player.x - 4, player.y + 15, 4, player.height - 30);

            // Draw AI Paddle (Right)
            ctx.shadowOffsetX = 5;
            ctx.fillStyle = ai.rubberColor;
            ctx.beginPath();
            ctx.roundRect(ai.x, ai.y, ai.width, ai.height, 8);
            ctx.fill();

            ctx.fillStyle = ai.color;
            ctx.fillRect(ai.x + ai.width, ai.y + 15, 4, ai.height - 30);

            ctx.shadowColor = 'transparent';
        }

        function drawBall() {
            if (gameState === 'START') return;

            // Ball Trail
            ball.trail.forEach((t, index) => {
                const alpha = (index + 1) / ball.trail.length * 0.4;
                ctx.fillStyle = ball.isSmash ? `rgba(251, 191, 36, ${alpha})` : `rgba(255, 255, 255, ${alpha})`;
                ctx.beginPath();
                ctx.arc(t.x, t.y, t.radius * (0.5 + 0.5 * index / ball.trail.length), 0, Math.PI * 2);
                ctx.fill();
            });

            // Ball Shadow on table
            ctx.fillStyle = 'rgba(0, 0, 0, 0.3)';
            ctx.beginPath();
            ctx.ellipse(ball.x + 6, ball.y + 12, ball.radius, ball.radius * 0.6, 0, 0, Math.PI * 2);
            ctx.fill();

            // Ball Main Body (Orange/White tournament ball)
            const ballColor = ball.isSmash ? '#fbbf24' : '#f8fafc';
            const grad = ctx.createRadialGradient(
                ball.x - 3, ball.y - 3, 2,
                ball.x, ball.y, ball.radius
            );
            grad.addColorStop(0, '#ffffff');
            grad.addColorStop(0.8, ballColor);
            grad.addColorStop(1, '#cbd5e1');

            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(ball.x, ball.y, ball.radius, 0, Math.PI * 2);
            ctx.fill();

            // Smash Effect Aura
            if (ball.isSmash) {
                ctx.strokeStyle = '#f59e0b';
                ctx.lineWidth = 3;
                ctx.beginPath();
                ctx.arc(ball.x, ball.y, ball.radius + 4 + Math.sin(Date.now() * 0.02) * 2, 0, Math.PI * 2);
                ctx.stroke();
            }
        }

        function drawParticles() {
            particles.forEach(p => {
                ctx.fillStyle = p.color;
                ctx.globalAlpha = p.life;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                ctx.fill();
            });
            ctx.globalAlpha = 1.0;
        }

        // --- Main Game Loop ---
        function loop() {
            // 1. Clear Screen
            ctx.clearRect(0, 0, V_WIDTH, V_HEIGHT);

            // 2. Physics & Logic Update
            updatePlayer();
            updateAI();
            updateBall();
            updateParticles();

            // 3. Rendering
            drawTable();
            drawPaddles();
            drawBall();
            drawParticles();

            requestAnimationFrame(loop);
        }

        // --- Input Event Listeners ---
        window.addEventListener('keydown', e => {
            if (e.code in keys) keys[e.code] = true;
        });

        window.addEventListener('keyup', e => {
            if (e.code in keys) keys[e.code] = false;
        });

        // Pointer (Mouse / Touch) Event Handlers for responsive feel
        function updatePointerPosition(clientY) {
            const rect = canvas.getBoundingClientRect();
            const scaleY = V_HEIGHT / rect.height;
            touchY = (clientY - rect.top) * scaleY;
        }

        canvas.addEventListener('mousemove', e => {
            updatePointerPosition(e.clientY);
        });

        canvas.addEventListener('touchstart', e => {
            if (e.touches.length > 0) {
                updatePointerPosition(e.touches[0].clientY);
            }
        }, { passive: true });

        canvas.addEventListener('touchmove', e => {
            if (e.touches.length > 0) {
                updatePointerPosition(e.touches[0].clientY);
            }
        }, { passive: true });

        canvas.addEventListener('touchend', () => {
            touchY = null;
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

        // Start Loop on Load
        window.onload = () => {
            selectDifficulty('medium');
            loop();
        };
    </script>
</body>
</html>
