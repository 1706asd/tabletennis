import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="리얼 3D 탁구 시뮬레이터",
    page_icon="🏓",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 여백 제거용 CSS
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# 3D 탁구 게임 HTML 코드 (반드시 삼중 따옴표 안에 위치해야 함)
html_code = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>리얼 3D 탁구 시뮬레이터 (3D Table Tennis)</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; user-select: none; }
        body {
            background-color: #0f172a;
            color: #f8fafc;
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            overflow: hidden;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
        }
        #game-container {
            position: relative;
            width: 100%;
            height: 100%;
        }
        canvas {
            display: block;
            width: 100%;
            height: 100%;
        }
        /* 상단 스코어보드 */
        #scoreboard {
            position: absolute;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            align-items: center;
            gap: 24px;
            background: rgba(15, 23, 42, 0.85);
            backdrop-filter: blur(8px);
            padding: 12px 32px;
            border-radius: 50px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
            z-index: 10;
        }
        .score-box {
            text-align: center;
        }
        .player-label {
            font-size: 12px;
            font-weight: bold;
            letter-spacing: 1px;
            color: #94a3b8;
        }
        .score-num {
            font-size: 32px;
            font-weight: 900;
            line-height: 1.1;
        }
        #player-score { color: #38bdf8; }
        #ai-score { color: #f43f5e; }
        .vs-divider {
            font-size: 14px;
            font-weight: bold;
            color: #64748b;
        }
        /* 컨트롤 바 */
        #controls {
            position: absolute;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            display: flex;
            gap: 12px;
            background: rgba(15, 23, 42, 0.8);
            padding: 10px 20px;
            border-radius: 30px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            z-index: 10;
        }
        button, select {
            background: #1e293b;
            color: #f8fafc;
            border: 1px solid #334155;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 13px;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.2s;
        }
        button:hover, select:hover {
            background: #334155;
            border-color: #38bdf8;
        }
        /* 안내 및 상태 메시지 */
        #message-overlay {
            position: absolute;
            top: 42%;
            left: 50%;
            transform: translate(-50%, -50%);
            text-align: center;
            pointer-events: none;
            z-index: 20;
        }
        #status-text {
            font-size: 36px;
            font-weight: 900;
            color: #fbbf24;
            text-shadow: 0 4px 15px rgba(0,0,0,0.8);
            opacity: 0;
            transition: opacity 0.3s;
        }
        #guide-text {
            position: absolute;
            bottom: 75px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 13px;
            color: #cbd5e1;
            background: rgba(0,0,0,0.5);
            padding: 6px 14px;
            border-radius: 15px;
            pointer-events: none;
        }
    </style>
    <!-- Three.js CDN -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
</head>
<body>
    <div id="game-container">
        <div id="scoreboard">
            <div class="score-box">
                <div class="player-label">PLAYER (나)</div>
                <div class="score-num" id="player-score">0</div>
            </div>
            <div class="vs-divider">VS</div>
            <div class="score-box">
                <div class="player-label">AI BOT</div>
                <div class="score-num" id="ai-score">0</div>
            </div>
        </div>

        <div id="message-overlay">
            <div id="status-text">SMASH!</div>
        </div>

        <div id="guide-text">🖱️ 마우스 이동: 라켓 조작 | 🖱️ 클릭: 서브 및 스매시</div>

        <div id="controls">
            <select id="difficulty">
                <option value="easy">난이도: 쉬움</option>
                <option value="normal" selected>난이도: 보통</option>
                <option value="hard">난이도: 어려움</option>
            </select>
            <button id="cam-btn">🎥 시점 전환</button>
            <button id="reset-btn">🔄 새 게임</button>
        </div>
    </div>

    <script>
        // 1. 사운드 합성 (Web Audio API)
        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        function playSound(type) {
            if (audioCtx.state === 'suspended') audioCtx.resume();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);

            const now = audioCtx.currentTime;
            if (type === 'paddle') {
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(520, now);
                osc.frequency.exponentialRampToValueAtTime(180, now + 0.08);
                gain.gain.setValueAtTime(0.4, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.08);
                osc.start(now);
                osc.stop(now + 0.08);
            } else if (type === 'smash') {
                osc.type = 'sawtooth';
                osc.frequency.setValueAtTime(750, now);
                osc.frequency.exponentialRampToValueAtTime(120, now + 0.14);
                gain.gain.setValueAtTime(0.6, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.14);
                osc.start(now);
                osc.stop(now + 0.14);
            } else if (type === 'table') {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(340, now);
                osc.frequency.exponentialRampToValueAtTime(140, now + 0.05);
                gain.gain.setValueAtTime(0.25, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.05);
                osc.start(now);
                osc.stop(now + 0.05);
            } else if (type === 'score') {
                osc.type = 'sine';
                osc.frequency.setValueAtTime(587.33, now);
                osc.frequency.setValueAtTime(880, now + 0.1);
                gain.gain.setValueAtTime(0.3, now);
                gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);
                osc.start(now);
                osc.stop(now + 0.3);
            }
        }

        // 2. Three.js 씬 설정
        const container = document.getElementById('game-container');
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0x0f172a);
        scene.fog = new THREE.Fog(0x0f172a, 12, 32);

        const camera = new THREE.PerspectiveCamera(48, window.innerWidth / window.innerHeight, 0.1, 100);
        let cameraMode = 0;
        function updateCameraPosition() {
            if (cameraMode === 0) {
                camera.position.set(0, 4.6, 8.8);
                camera.lookAt(0, 0.6, -1.2);
            } else {
                camera.position.set(0, 6.8, 7.2);
                camera.lookAt(0, 0.4, 0);
            }
        }
        updateCameraPosition();

        const renderer = new THREE.WebGLRenderer({ antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.shadowMap.enabled = true;
        renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        container.appendChild(renderer.domElement);

        // 조명
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.55);
        scene.add(ambientLight);

        const dirLight = new THREE.DirectionalLight(0xffffff, 0.9);
        dirLight.position.set(5, 12, 6);
        dirLight.castShadow = true;
        dirLight.shadow.mapSize.width = 2048;
        dirLight.shadow.mapSize.height = 2048;
        scene.add(dirLight);

        // 경기장 바닥
        const floorGeo = new THREE.PlaneGeometry(40, 40);
        const floorMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.8 });
        const floor = new THREE.Mesh(floorGeo, floorMat);
        floor.rotation.x = -Math.PI / 2;
        floor.position.y = -1.5;
        floor.receiveShadow = true;
        scene.add(floor);

        // 3. 탁구대 제작 (국제 규격 비율: 가로 4.5, 세로 8.2)
        const TABLE_W = 4.6;
        const TABLE_L = 8.4;
        const TABLE_H = 0.2;

        const tableGroup = new THREE.Group();
        const tableGeo = new THREE.BoxGeometry(TABLE_W, TABLE_H, TABLE_L);
        const tableMat = new THREE.MeshStandardMaterial({ color: 0x1d4ed8, roughness: 0.35 });
        const tableMesh = new THREE.Mesh(tableGeo, tableMat);
        tableMesh.position.y = -TABLE_H / 2;
        tableMesh.receiveShadow = true;
        tableGroup.add(tableMesh);

        // 흰색 라인
        const lineMat = new THREE.MeshBasicMaterial({ color: 0xffffff });
        const centerLine = new THREE.Mesh(new THREE.PlaneGeometry(0.05, TABLE_L), lineMat);
        centerLine.rotation.x = -Math.PI / 2;
        centerLine.position.y = 0.005;
        tableGroup.add(centerLine);

        const borderL = new THREE.Mesh(new THREE.PlaneGeometry(0.07, TABLE_L), lineMat);
        borderL.rotation.x = -Math.PI / 2;
        borderL.position.set(-TABLE_W / 2 + 0.035, 0.005, 0);
        tableGroup.add(borderL);

        const borderR = borderL.clone();
        borderR.position.x = TABLE_W / 2 - 0.035;
        tableGroup.add(borderR);

        const borderTop = new THREE.Mesh(new THREE.PlaneGeometry(TABLE_W, 0.07), lineMat);
        borderTop.rotation.x = -Math.PI / 2;
        borderTop.position.set(0, 0.005, -TABLE_L / 2 + 0.035);
        tableGroup.add(borderTop);

        const borderBot = borderTop.clone();
        borderBot.position.z = TABLE_L / 2 - 0.035;
        tableGroup.add(borderBot);

        // 네트
        const netGeo = new THREE.BoxGeometry(TABLE_W + 0.3, 0.42, 0.04);
        const netMat = new THREE.MeshStandardMaterial({
            color: 0xe2e8f0,
            transparent: true,
            opacity: 0.85,
            roughness: 0.6
        });
        const netMesh = new THREE.Mesh(netGeo, netMat);
        netMesh.position.y = 0.21;
        netMesh.castShadow = true;
        tableGroup.add(netMesh);

        // 탁구대 다리
        const legGeo = new THREE.BoxGeometry(0.2, 1.5, 0.2);
        const legMat = new THREE.MeshStandardMaterial({ color: 0x0f172a });
        [[-1.8, -3.2], [1.8, -3.2], [-1.8, 3.2], [1.8, 3.2]].forEach(([lx, lz]) => {
            const leg = new THREE.Mesh(legGeo, legMat);
            leg.position.set(lx, -0.85, lz);
            tableGroup.add(leg);
        });

        scene.add(tableGroup);

        // 4. 라켓 생성 함수
        function createPaddle(rubberColor) {
            const group = new THREE.Group();
            const bladeGeo = new THREE.CylinderGeometry(0.45, 0.45, 0.06, 32);
            bladeGeo.rotateX(Math.PI / 2);
            const bladeMat = new THREE.MeshStandardMaterial({ color: rubberColor, roughness: 0.4 });
            const blade = new THREE.Mesh(bladeGeo, bladeMat);
            blade.castShadow = true;
            group.add(blade);

            const handleGeo = new THREE.BoxGeometry(0.14, 0.45, 0.08);
            const handleMat = new THREE.MeshStandardMaterial({ color: 0xd97706 });
            const handle = new THREE.Mesh(handleGeo, handleMat);
            handle.position.y = -0.55;
            group.add(handle);

            return group;
        }

        const playerPaddle = createPaddle(0xef4444); // 빨간 러버
        playerPaddle.position.set(0, 0.6, 4.4);
        scene.add(playerPaddle);

        const aiPaddle = createPaddle(0x1e293b); // 검은 러버
        aiPaddle.position.set(0, 0.6, -4.4);
        scene.add(aiPaddle);

        // 5. 탁구공 및 바닥 그림자
        const BALL_R = 0.11;
        const ballGeo = new THREE.SphereGeometry(BALL_R, 24, 24);
        const ballMat = new THREE.MeshStandardMaterial({ color: 0xfbbf24, roughness: 0.2 });
        const ball = new THREE.Mesh(ballGeo, ballMat);
        ball.castShadow = true;
        scene.add(ball);

        const shadowGeo = new THREE.CircleGeometry(BALL_R * 1.3, 16);
        shadowGeo.rotateX(-Math.PI / 2);
        const shadowMat = new THREE.MeshBasicMaterial({ color: 0x000000, transparent: true, opacity: 0.35 });
        const ballShadow = new THREE.Mesh(shadowGeo, shadowMat);
        ballShadow.position.y = 0.01;
        scene.add(ballShadow);

        // 6. 게임 상태 및 물리 변수
        let playerScore = 0;
        let aiScore = 0;
        let gameState = 'SERVE_PLAYER'; // SERVE_PLAYER, PLAYING, POINT_OVER, GAME_OVER
        let ballVel = new THREE.Vector3(0, 0, 0);
        let ballSpin = new THREE.Vector3(0, 0, 0); // x: topspin, y: sidespin
        let lastHitter = null;
        let bounceCount = 0;

        let targetPaddleX = 0;
        let targetPaddleY = 0.6;
        let prevPaddleX = 0;
        let smashCharge = false;

        const statusText = document.getElementById('status-text');
        function showMessage(text, color = '#fbbf24', duration = 900) {
            statusText.textContent = text;
            statusText.style.color = color;
            statusText.style.opacity = 1;
            clearTimeout(statusText._timer);
            statusText._timer = setTimeout(() => {
                statusText.style.opacity = 0;
            }, duration);
        }

        function updateScoreUI() {
            document.getElementById('player-score').textContent = playerScore;
            document.getElementById('ai-score').textContent = aiScore;
        }

        function resetBallForServe(server = 'PLAYER') {
            ballVel.set(0, 0, 0);
            ballSpin.set(0, 0, 0);
            bounceCount = 0;
            lastHitter = null;
            if (server === 'PLAYER') {
                gameState = 'SERVE_PLAYER';
                ball.position.set(playerPaddle.position.x, playerPaddle.position.y + 0.35, 3.8);
            } else {
                gameState = 'SERVE_AI';
                ball.position.set(aiPaddle.position.x, aiPaddle.position.y + 0.35, -3.8);
                setTimeout(() => {
                    if (gameState === 'SERVE_AI') {
                        aiServe();
                    }
                }, 900);
            }
        }

        function playerServe() {
            if (gameState !== 'SERVE_PLAYER') return;
            gameState = 'PLAYING';
            lastHitter = 'PLAYER';
            bounceCount = 0;
            const aimX = (Math.random() - 0.5) * 2.2;
            ballVel.set((aimX - ball.position.x) * 1.1, 3.2, -9.8);
            ballSpin.set(1.5, (playerPaddle.position.x - prevPaddleX) * 8, 0);
            playSound('paddle');
        }

        function aiServe() {
            gameState = 'PLAYING';
            lastHitter = 'AI';
            bounceCount = 0;
            const aimX = (Math.random() - 0.5) * 2.4;
            ballVel.set((aimX - ball.position.x) * 1.1, 3.1, 9.5);
            ballSpin.set(1.2, 0, 0);
            playSound('paddle');
        }

        function awardPoint(winner, reason = '') {
            if (gameState === 'POINT_OVER' || gameState === 'GAME_OVER') return;
            gameState = 'POINT_OVER';
            playSound('score');

            if (winner === 'PLAYER') {
                playerScore++;
                showMessage(reason || 'POINT! (+1)', '#38bdf8', 1100);
            } else {
                aiScore++;
                showMessage(reason || 'AI POINT!', '#f43f5e', 1100);
            }
            updateScoreUI();

            // 11점 듀스 규칙 체크
            if ((playerScore >= 11 || aiScore >= 11) && Math.abs(playerScore - aiScore) >= 2) {
                gameState = 'GAME_OVER';
                const winMsg = playerScore > aiScore ? '🏆 승리했습니다!' : '💀 패배했습니다!';
                showMessage(winMsg, '#fbbf24', 4000);
                return;
            }

            setTimeout(() => {
                resetBallForServe(winner);
            }, 1200);
        }

        // 7. 입력 이벤트
        window.addEventListener('mousemove', (e) => {
            const normX = (e.clientX / window.innerWidth) * 2 - 1;
            const normY = -(e.clientY / window.innerHeight) * 2 + 1;
            targetPaddleX = normX * 3.1;
            targetPaddleY = Math.max(0.25, Math.min(2.0, (normY + 0.6) * 1.2));
        });

        window.addEventListener('mousedown', () => {
            if (gameState === 'SERVE_PLAYER') {
                playerServe();
            } else if (gameState === 'PLAYING') {
                smashCharge = true;
                playerPaddle.rotation.x = -0.55;
                setTimeout(() => {
                    smashCharge = false;
                    playerPaddle.rotation.x = 0;
                }, 220);
            }
        });

        document.getElementById('cam-btn').addEventListener('click', () => {
            cameraMode = (cameraMode + 1) % 2;
            updateCameraPosition();
        });

        document.getElementById('reset-btn').addEventListener('click', () => {
            playerScore = 0;
            aiScore = 0;
            updateScoreUI();
            resetBallForServe('PLAYER');
            showMessage('NEW MATCH!', '#38bdf8', 900);
        });

        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        // 8. 메인 물리 및 렌더링 루프
        const clock = new THREE.Clock();
        const GRAVITY = -16.5;

        function animate() {
            requestAnimationFrame(animate);
            const dt = Math.min(clock.getDelta(), 0.033);

            // 플레이어 라켓 부드러운 이동
            prevPaddleX = playerPaddle.position.x;
            playerPaddle.position.x += (targetPaddleX - playerPaddle.position.x) * 18 * dt;
            playerPaddle.position.y += (targetPaddleY - playerPaddle.position.y) * 18 * dt;
            playerPaddle.rotation.z = -(targetPaddleX - playerPaddle.position.x) * 0.4;

            if (gameState === 'SERVE_PLAYER') {
                ball.position.set(playerPaddle.position.x, playerPaddle.position.y + 0.35 + Math.sin(Date.now() * 0.008) * 0.06, 3.8);
            } else if (gameState === 'PLAYING') {
                // 마그누스(회전) 효과 및 중력
                ballVel.x += ballSpin.y * dt * 1.8;
                ballVel.y += (GRAVITY - ballSpin.x * 2.2) * dt;

                ball.position.addScaledVector(ballVel, dt);

                // 탁구대 바운스 판정
                const onTableX = Math.abs(ball.position.x) <= TABLE_W / 2 + BALL_R * 0.5;
                const onTableZ = Math.abs(ball.position.z) <= TABLE_L / 2 + BALL_R * 0.5;

                if (onTableX && onTableZ && ball.position.y <= BALL_R && ballVel.y < 0) {
                    ball.position.y = BALL_R;
                    ballVel.y = -ballVel.y * 0.84;
                    ballVel.z *= 0.97;
                    playSound('table');

                    // 어느 코트에 튀었는지 확인
                    const isPlayerSide = ball.position.z > 0;
                    if (lastHitter === 'PLAYER' && isPlayerSide && bounceCount === 0) {
                        // 서브 시 자기 코트 원바운드 허용
                        bounceCount++;
                    } else if (lastHitter === 'AI' && !isPlayerSide && bounceCount === 0) {
                        bounceCount++;
                    } else {
                        bounceCount++;
                        if (bounceCount >= 2) {
                            awardPoint(lastHitter, 'TWO BOUNCE!');
                        }
                    }
                }

                // 네트 충돌 판정
                if (Math.abs(ball.position.z) < 0.08 && ball.position.y < 0.44) {
                    ballVel.z *= -0.35;
                    ballVel.y = 1.5;
                    playSound('table');
                    awardPoint(lastHitter === 'PLAYER' ? 'AI' : 'PLAYER', 'NET FAULT!');
                }

                // 플레이어 라켓 타격 판정
                if (ballVel.z > 0 && ball.position.z >= 3.8 && ball.position.z <= 4.7) {
                    const dx = ball.position.x - playerPaddle.position.x;
                    const dy = ball.position.y - playerPaddle.position.y;
                    if (Math.hypot(dx, dy) < 0.68) {
                        const paddleVelX = (playerPaddle.position.x - prevPaddleX) / dt;
                        const isSmash = smashCharge || ball.position.y > 0.95;

                        ballVel.z = isSmash ? -14.8 : -11.2;
                        ballVel.x = dx * 3.8 + paddleVelX * 0.28;
                        ballVel.y = isSmash ? 2.4 : 4.2;

                        ballSpin.set(isSmash ? 3.5 : 1.5, paddleVelX * 0.35, 0);
                        lastHitter = 'PLAYER';
                        bounceCount = 0;

                        if (isSmash) {
                            playSound('smash');
                            showMessage('🔥 SMASH!', '#fbbf24', 650);
                        } else {
                            playSound('paddle');
                        }
                    }
                }

                // AI 이동 및 타격 로직
                const diff = document.getElementById('difficulty').value;
                const aiSpeed = diff === 'easy' ? 4.2 : (diff === 'normal' ? 7.2 : 11.5);
                const aiTargetX = ballVel.z < 0 ? ball.position.x : 0;
                aiPaddle.position.x += (aiTargetX - aiPaddle.position.x) * aiSpeed * dt;
                aiPaddle.position.x = Math.max(-2.5, Math.min(2.5, aiPaddle.position.x));

                if (ballVel.z < 0 && ball.position.z <= -3.8 && ball.position.z >= -4.7) {
                    const dx = ball.position.x - aiPaddle.position.x;
                    const dy = ball.position.y - aiPaddle.position.y;
                    if (Math.hypot(dx, dy) < 0.72) {
                        const aimX = (Math.random() - 0.5) * (diff === 'hard' ? 3.4 : 2.2);
                        const shotSpeed = diff === 'easy' ? 9.5 : (diff === 'normal' ? 11.4 : 13.6);
                        ballVel.z = shotSpeed;
                        ballVel.x = (aimX - ball.position.x) * 1.35;
                        ballVel.y = diff === 'hard' ? 3.3 : 4.1;
                        ballSpin.set(diff === 'hard' ? 2.5 : 1.2, (Math.random() - 0.5) * 2.5, 0);
                        lastHitter = 'AI';
                        bounceCount = 0;
                        playSound('paddle');
                    }
                }

                // 아웃 / 실점 판정
                if (ball.position.y < -1.2 || Math.abs(ball.position.z) > 6.5 || Math.abs(ball.position.x) > 4.2) {
                    if (bounceCount === 0) {
                        // 노바운드 아웃: 친 사람 실점
                        awardPoint(lastHitter === 'PLAYER' ? 'AI' : 'PLAYER', 'OUT!');
                    } else {
                        // 원바운드 후 못 받아침: 친 사람 득점
                        awardPoint(lastHitter);
                    }
                }
            }

            // 그림자 위치 업데이트
            ballShadow.position.x = ball.position.x;
            ballShadow.position.z = ball.position.z;
            const onTable = Math.abs(ball.position.x) <= TABLE_W / 2 && Math.abs(ball.position.z) <= TABLE_L / 2;
            ballShadow.visible = onTable && ball.position.y >= 0;
            const shadowScale = Math.max(0.3, 1 - ball.position.y * 0.25);
            ballShadow.scale.set(shadowScale, shadowScale, 1);

            renderer.render(scene, camera);
        }

        resetBallForServe('PLAYER');
        animate();
    </script>
</body>
</html>
"""

# Streamlit 화면에 3D 게임 렌더링
components.html(html_code, height=780, scrolling=False)
