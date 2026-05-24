// IPL Player Analytics JavaScript Controller

document.addEventListener("DOMContentLoaded", () => {
    // State Variables
    let playersData = {};
    let selectedLine = "Middle Stump";
    let selectedLength = "Good Length";
    let selectedX = 300; // Canvas coordinates
    let selectedY = 180;
    let winProbHistory = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5]; // Over history
    let ballCounter = 0;
    let currentMode = "bowling";
    
    // Canvas Setup
    const canvas = document.getElementById("pitch-canvas");
    const ctx = canvas.getContext("2d");
    const crosshair = document.getElementById("target-crosshair");
    
    // UI Elements
    const batsmanSelect = document.getElementById("batsman-select");
    const bowlerSelect = document.getElementById("bowler-select");
    const deliveryVariation = document.getElementById("delivery-variation");
    const deliverySpeed = document.getElementById("delivery-speed");
    const speedVal = document.getElementById("speed-val");
    const simulateBtn = document.getElementById("simulate-btn");
    
    // Toggle / Live sync controls
    const toggleBowlingBtn = document.getElementById("toggle-bowling-btn");
    const toggleBattingBtn = document.getElementById("toggle-batting-btn");
    const syncLiveBtn = document.getElementById("sync-live-btn");
    const liveIndicatorBadge = document.getElementById("live-indicator-badge");
    const liveMatchName = document.getElementById("live-match-name");
    
    // Match Condition Inputs
    const matchVenue = document.getElementById("match-venue");
    const matchWeather = document.getElementById("match-weather");
    const ballType = document.getElementById("ball-type");
    const ballAge = document.getElementById("ball-age");
    const matchInning = document.getElementById("match-inning");
    const matchOvers = document.getElementById("match-overs");
    const matchWickets = document.getElementById("match-wickets");
    const targetRuns = document.getElementById("target-runs");
    const runsNeeded = document.getElementById("runs-needed");
    const ballsRemaining = document.getElementById("balls-remaining");
    const selectChaseFields = document.querySelectorAll(".select-chase-only");
    
    // HUD Elements
    const hudSpeed = document.getElementById("hud-speed");
    const hudReaction = document.getElementById("hud-reaction");
    const hudContact = document.getElementById("hud-contact");
    const hudRuns = document.getElementById("hud-runs");
    const hudOutcomeCard = document.getElementById("hud-outcome-card");
    
    // AI Clipboard Elements
    const aiWeaknessSummary = document.getElementById("ai-weakness-summary");
    const aiOptimalDelivery = document.getElementById("ai-optimal-delivery");
    const aiFieldingSuggestions = document.getElementById("ai-fielding-suggestions");
    
    // Win Prob Elements
    const winProbFill = document.getElementById("win-prob-fill");
    const winProbText = document.getElementById("win-prob-text");
    const batProbDisplay = document.getElementById("bat-prob-display");
    const bowlProbDisplay = document.getElementById("bowl-prob-display");
    const battingTeamLabel = document.getElementById("batting-team-label");
    const bowlingTeamLabel = document.getElementById("bowling-team-label");
    const sparklinePath = document.getElementById("sparkline-path");
    const sparklineDot = document.getElementById("sparkline-dot");

    // Initialize Page
    init();

    async function init() {
        try {
            await fetchPlayers();
            setupCanvas();
            setupEventListeners();
            toggleInningsChaseFields();
            updateAICoach();
            updateWinProbability();
            drawStaticPitch();
        } catch (err) {
            console.error("Initialization error:", err);
            document.getElementById("model-status-text").innerText = "AI MODEL: OFFLINE";
            document.getElementById("model-status-text").style.color = "var(--neon-pink)";
        }
    }

    // 1. Setup API Integration & Dropdown population
    async function fetchPlayers() {
        const response = await fetch("/api/players");
        if (!response.ok) throw new Error("Failed to load players metadata");
        playersData = await response.json();
        
        // Populate dropdowns
        batsmanSelect.innerHTML = "";
        bowlerSelect.innerHTML = "";
        
        Object.entries(playersData).forEach(([name, details]) => {
            const option = document.createElement("option");
            option.value = name;
            option.textContent = name;
            
            if (details.role === "Batsman") {
                batsmanSelect.appendChild(option);
            } else if (details.role === "Bowler") {
                bowlerSelect.appendChild(option);
            }
        });
        
        // Trigger initial profiles update
        updateBatsmanProfile();
        updateBowlerProfile();
    }

    function updateBatsmanProfile() {
        const name = batsmanSelect.value;
        const details = playersData[name];
        if (!details) return;
        
        document.getElementById("batsman-name-display").textContent = name;
        document.getElementById("batsman-meta").textContent = `${details.hand} | ${details.style}`;
        document.getElementById("batsman-img").src = details.image;
        
        // Form & skill indicators
        document.getElementById("batsman-pace-bar").style.width = `${details.pace_rating}%`;
        document.getElementById("batsman-spin-bar").style.width = `${details.spin_rating}%`;
        
        battingTeamLabel.textContent = "Batting (Strike)";
    }

    function updateBowlerProfile() {
        const name = bowlerSelect.value;
        const details = playersData[name];
        if (!details) return;
        
        document.getElementById("bowler-name-display").textContent = name;
        document.getElementById("bowler-meta").textContent = `${details.hand} | ${details.style}`;
        document.getElementById("bowler-img").src = details.image;
        
        // Skill indicators
        document.getElementById("bowler-speed-bar").style.width = `${details.speed_rating}%`;
        document.getElementById("bowler-deception-bar").style.width = `${details.deception_rating}%`;
        
        // Populate variations based on bowler characteristics dynamically from player database
        deliveryVariation.innerHTML = "";
        let vars = details.variations || ["Normal"];
        
        vars.forEach(v => {
            const opt = document.createElement("option");
            opt.value = v;
            opt.textContent = v;
            deliveryVariation.appendChild(opt);
        });

        // Set default speeds based on bowler style
        if (details.style.includes("Fast")) {
            deliverySpeed.min = 130;
            deliverySpeed.max = 160;
            deliverySpeed.value = 142;
        } else {
            deliverySpeed.min = 70;
            deliverySpeed.max = 105;
            deliverySpeed.value = 88;
        }
        speedVal.textContent = deliverySpeed.value;
        bowlingTeamLabel.textContent = "Bowling";
    }

    function toggleInningsChaseFields() {
        const isChase = matchInning.value === "2";
        selectChaseFields.forEach(el => {
            el.style.opacity = isChase ? "1" : "0.3";
            el.querySelector("input").disabled = !isChase;
        });
    }

    // 2. Interactive Pitch Canvas Logic
    function setupCanvas() {
        updateCrosshairPosition(selectedX, selectedY);
        
        canvas.addEventListener("mousedown", (e) => {
            const rect = canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            if (x >= 150 && x <= 450 && y >= 30 && y <= 320) {
                selectedX = x;
                selectedY = y;
                mapCoordinatesToLineLength(x, y);
                updateCrosshairPosition(x, y);
                drawStaticPitch();
            }
        });
    }

    function updateCrosshairPosition(x, y) {
        crosshair.style.display = "block";
        crosshair.style.left = `${(x / canvas.width) * 100}%`;
        crosshair.style.top = `${(y / canvas.height) * 100}%`;
    }

    function mapCoordinatesToLineLength(x, y) {
        const isRightHand = playersData[batsmanSelect.value]?.hand === "Right Hand";
        
        let lineIdx;
        const normX = (x - 150) / 300;
        
        if (normX < 0.2) lineIdx = 0;
        else if (normX < 0.4) lineIdx = 1;
        else if (normX < 0.6) lineIdx = 2;
        else if (normX < 0.8) lineIdx = 3;
        else lineIdx = 4;
        
        const rightHandLines = ['Outside Leg', 'Leg Stump', 'Middle Stump', 'On the Off Stump', 'Outside Off'];
        const leftHandLines = ['Outside Off', 'On the Off Stump', 'Middle Stump', 'Leg Stump', 'Outside Leg'];
        
        selectedLine = isRightHand ? rightHandLines[lineIdx] : leftHandLines[lineIdx];
        document.getElementById("line-badge").textContent = selectedLine;

        const normY = (y - 30) / 290;
        
        if (normY < 0.25) selectedLength = "Short";
        else if (normY < 0.6) selectedLength = "Good Length";
        else if (normY < 0.8) selectedLength = "Full";
        else selectedLength = "Yorker";
        
        document.getElementById("length-badge").textContent = selectedLength;
    }

    function drawStaticPitch() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Draw Outfield background
        ctx.fillStyle = "#0c1527";
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Draw Pitch (Perspective rectangle)
        ctx.fillStyle = "#8a7355";
        ctx.strokeStyle = "rgba(255,255,255,0.15)";
        ctx.lineWidth = 1.5;
        
        ctx.beginPath();
        ctx.moveTo(300 - 60, 40);
        ctx.lineTo(300 + 60, 40);
        ctx.lineTo(300 + 110, 310);
        ctx.lineTo(300 - 110, 310);
        ctx.closePath();
        ctx.fill();
        ctx.stroke();

        // Draw Creases
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        
        // Bowler end crease (top)
        ctx.beginPath();
        ctx.moveTo(300 - 65, 55);
        ctx.lineTo(300 + 65, 55);
        ctx.stroke();
        
        // Batsman end crease (bottom)
        ctx.beginPath();
        ctx.moveTo(300 - 105, 290);
        ctx.lineTo(300 + 105, 290);
        ctx.stroke();

        // Draw Stumps
        ctx.fillStyle = "#ffd700";
        ctx.fillRect(296, 38, 8, 3);
        ctx.fillRect(295, 293, 10, 4);

        // Draw Length Guideline Markings
        ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
        ctx.setLineDash([4, 4]);
        
        ctx.beginPath();
        ctx.moveTo(300 - 75, 110);
        ctx.lineTo(300 + 75, 110);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(300 - 90, 200);
        ctx.lineTo(300 + 90, 200);
        ctx.stroke();
        
        ctx.beginPath();
        ctx.moveTo(300 - 100, 265);
        ctx.lineTo(300 + 100, 265);
        ctx.stroke();
        
        ctx.setLineDash([]);
        
        // Text labels inside the canvas (Zones)
        ctx.fillStyle = "rgba(255,255,255,0.2)";
        ctx.font = "bold 9px 'Outfit'";
        ctx.textAlign = "center";
        ctx.fillText("SHORT BALL ZONE", 300, 85);
        ctx.fillText("GOOD LENGTH ZONE", 300, 160);
        ctx.fillText("FULL LENGTH ZONE", 300, 235);
        ctx.fillText("YORKER / DEATH ZONE", 300, 282);
    }

    function animateBallDelivery(trajectoryMod, onComplete) {
        let frame = 0;
        const totalFrames = 30;
        
        const bowlerX = 300;
        const bowlerY = 50;
        const bounceX = selectedX;
        const bounceY = selectedY;
        
        const endX = 300 + (trajectoryMod.dev_x * 40);
        const endY = 290;
        
        const pathPoints = [];

        function drawFrame() {
            if (frame > totalFrames) {
                drawStaticPitch();
                onComplete();
                return;
            }
            
            drawStaticPitch();
            
            ctx.strokeStyle = "rgba(0, 240, 255, 0.4)";
            ctx.lineWidth = 3;
            ctx.beginPath();
            if (pathPoints.length > 0) {
                ctx.moveTo(pathPoints[0].x, pathPoints[0].y);
                for(let i=1; i<pathPoints.length; i++) {
                    ctx.lineTo(pathPoints[i].x, pathPoints[i].y);
                }
            }
            ctx.stroke();
            
            let currentX, currentY, ballSize;
            const progress = frame / totalFrames;
            
            if (progress <= 0.6) {
                const t = progress / 0.6;
                currentX = bowlerX + (bounceX - bowlerX) * t;
                currentY = bowlerY + (bounceY - bowlerY) * t;
                ballSize = 3 + (t * 2);
            } else {
                const t = (progress - 0.6) / 0.4;
                currentX = bounceX + (endX - bounceX) * t;
                currentY = bounceY + (endY - bounceY) * t;
                ballSize = 5 + (t * 3.5);
                
                const arcHeight = Math.sin(t * Math.PI) * 20 * trajectoryMod.bounce_coeff;
                currentY -= arcHeight;
            }
            
            pathPoints.push({ x: currentX, y: currentY });
            
            const grad = ctx.createRadialGradient(currentX - 2, currentY - 2, 1, currentX, currentY, ballSize);
            grad.addColorStop(0, "#ff7676");
            grad.addColorStop(0.3, "#f44336");
            grad.addColorStop(1, "#9a0f07");
            
            ctx.fillStyle = grad;
            ctx.beginPath();
            ctx.arc(currentX, currentY, ballSize, 0, Math.PI * 2);
            ctx.fill();
            
            frame++;
            requestAnimationFrame(drawFrame);
        }
        
        drawFrame();
    }

    // 3. Event Listeners Setup
    function setupEventListeners() {
        batsmanSelect.addEventListener("change", () => {
            updateBatsmanProfile();
            updateAICoach();
            mapCoordinatesToLineLength(selectedX, selectedY);
        });
        
        bowlerSelect.addEventListener("change", () => {
            updateBowlerProfile();
            updateAICoach();
        });
        
        deliverySpeed.addEventListener("input", (e) => {
            speedVal.textContent = e.target.value;
        });
        
        matchInning.addEventListener("change", () => {
            toggleInningsChaseFields();
            updateWinProbability();
        });
        
        matchVenue.addEventListener("change", () => {
            updateAICoach();
            updateWinProbability();
        });
        matchWeather.addEventListener("change", updateAICoach);
        ballType.addEventListener("change", updateAICoach);
        ballAge.addEventListener("change", updateAICoach);
        
        simulateBtn.addEventListener("click", triggerDeliverySimulation);
        
        // Mode toggle listeners
        toggleBowlingBtn.addEventListener("click", () => {
            if (currentMode === "bowling") return;
            currentMode = "bowling";
            toggleBowlingBtn.classList.add("active");
            toggleBattingBtn.classList.remove("active");
            updateAICoach();
        });
        
        toggleBattingBtn.addEventListener("click", () => {
            if (currentMode === "batting") return;
            currentMode = "batting";
            toggleBattingBtn.classList.add("active");
            toggleBowlingBtn.classList.remove("active");
            updateAICoach();
        });
        
        // Live match sync listener
        syncLiveBtn.addEventListener("click", syncLiveMatch);
    }

    // 4. AI Coach Tactical Clipboard
    async function updateAICoach() {
        const payload = {
            batsman: batsmanSelect.value,
            bowler: bowlerSelect.value,
            weather: matchWeather.value,
            ball_type: ballType.value,
            ball_age: parseFloat(ballAge.value),
            venue: matchVenue.value,
            mode: currentMode
        };
        
        try {
            const res = await fetch("/api/tactical-recommendation", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) throw new Error("Recommendation endpoint failed");
            const data = await res.json();
            
            aiWeaknessSummary.textContent = data.batsman_weakness_summary;
            
            const rec = data.top_recommendations[0];
            
            if (currentMode === "bowling") {
                aiOptimalDelivery.innerHTML = `
                    Pitch: <span class="highlight">${rec.length}</span> at <span class="highlight">${rec.line}</span><br>
                    Variation: <span class="highlight">${rec.variation}</span> (~${rec.speed_kph} kph)<br>
                    <span style="font-size:0.68rem; color:var(--text-dim)">Runs expectation: ${rec.expected_runs} | Wicket probability: ${(rec.wicket_probability*100).toFixed(1)}%</span>
                `;
            } else {
                aiOptimalDelivery.innerHTML = `
                    Shot Recommendation: <span class="highlight">${rec.predicted_shot}</span><br>
                    Expected Runs: <span class="highlight">${rec.expected_runs}</span><br>
                    Wicket Risk: <span class="highlight">${(rec.wicket_probability*100).toFixed(1)}%</span>
                `;
            }
            
            aiFieldingSuggestions.innerHTML = "";
            data.field_suggestions.forEach(field => {
                const li = document.createElement("li");
                li.textContent = field;
                aiFieldingSuggestions.appendChild(li);
            });
            
        } catch (err) {
            console.error("AI coach loading error:", err);
            aiWeaknessSummary.textContent = "Error compiling profile.";
            aiOptimalDelivery.textContent = "Offline.";
        }
    }

    // 4b. Live Cricbuzz Sync Logic
    async function syncLiveMatch() {
        syncLiveBtn.disabled = true;
        const originalText = syncLiveBtn.innerHTML;
        syncLiveBtn.innerHTML = `
            <svg class="spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 6px;"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg>
            SYNCING...
        `;
        
        try {
            const response = await fetch("/api/live-match");
            if (!response.ok) throw new Error("Sync failed");
            const data = await response.json();
            
            // Update Match Conditions
            matchVenue.value = data.venue;
            matchWeather.value = data.weather;
            matchInning.value = data.inning.toString();
            matchOvers.value = data.overs.toString();
            matchWickets.value = data.wickets.toString();
            
            if (data.inning === 2) {
                targetRuns.value = data.target_runs;
                runsNeeded.value = data.runs_needed;
                ballsRemaining.value = data.balls_remaining;
            }
            
            toggleInningsChaseFields();
            
            // Select players
            let batsmanFound = false;
            let bowlerFound = false;
            
            for (let option of batsmanSelect.options) {
                if (option.value === data.batsman) {
                    batsmanSelect.value = data.batsman;
                    batsmanFound = true;
                    break;
                }
            }
            for (let option of bowlerSelect.options) {
                if (option.value === data.bowler) {
                    bowlerSelect.value = data.bowler;
                    bowlerFound = true;
                    break;
                }
            }
            
            if (!batsmanFound) {
                for (let option of batsmanSelect.options) {
                    if (option.value.toLowerCase().includes(data.batsman.toLowerCase()) || data.batsman.toLowerCase().includes(option.value.toLowerCase())) {
                        batsmanSelect.value = option.value;
                        break;
                    }
                }
            }
            if (!bowlerFound) {
                for (let option of bowlerSelect.options) {
                    if (option.value.toLowerCase().includes(data.bowler.toLowerCase()) || data.bowler.toLowerCase().includes(option.value.toLowerCase())) {
                        bowlerSelect.value = option.value;
                        break;
                    }
                }
            }
            
            updateBatsmanProfile();
            updateBowlerProfile();
            
            // Update HUD text & status
            if (data.is_live) {
                liveIndicatorBadge.textContent = "🔴 LIVE MATCH ACTIVE";
                liveIndicatorBadge.classList.add("live-active");
            } else {
                liveIndicatorBadge.textContent = "⚪ SIMULATION MODE (Cached)";
                liveIndicatorBadge.classList.remove("live-active");
            }
            liveMatchName.textContent = data.match_name;
            
            await updateAICoach();
            await updateWinProbability();
            drawStaticPitch();
            
        } catch (err) {
            console.error("Live match sync failed:", err);
            alert("Failed to sync live match. Please check server logs.");
        } finally {
            syncLiveBtn.disabled = false;
            syncLiveBtn.innerHTML = originalText;
        }
    }

    // 5. Model Win Probability Updater
    async function updateWinProbability() {
        const isChase = matchInning.value === "2";
        const totalTarget = parseInt(targetRuns.value);
        const runsToWin = parseInt(runsNeeded.value);
        const ballsLeft = parseInt(ballsRemaining.value);
        
        const oversPlayed = parseFloat(matchOvers.value);
        const curRuns = isChase ? (totalTarget - runsToWin) : Math.round(oversPlayed * 8.2);
        
        const payload = {
            inning: parseInt(matchInning.value),
            overs: oversPlayed,
            wickets: parseInt(matchWickets.value),
            runs_needed: isChase ? runsToWin : 0,
            balls_remaining: isChase ? ballsLeft : 120,
            current_run_rate: parseFloat((curRuns / (oversPlayed > 0 ? oversPlayed : 0.1)).toFixed(2)),
            required_run_rate: isChase ? parseFloat((runsToWin / (ballsLeft / 6.0)).toFixed(2)) : 0.0,
            venue: matchVenue.value,
            weather: matchWeather.value,
            batsman: batsmanSelect.value,
            bowler: bowlerSelect.value
        };

        try {
            const res = await fetch("/api/predict-win-prob", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) throw new Error("Win prob endpoint failed");
            const data = await res.json();
            
            const prob = data.win_probability;
            
            const offset = 251.2 - (prob * 251.2);
            winProbFill.style.strokeDashoffset = offset;
            winProbText.textContent = `${Math.round(prob * 100)}%`;
            
            batProbDisplay.textContent = `${Math.round(prob * 100)}%`;
            bowlProbDisplay.textContent = `${Math.round((1.0 - prob) * 100)}%`;
            
            winProbHistory.shift();
            winProbHistory.push(prob);
            drawSparkline();
            
        } catch (err) {
            console.error("Win prob error:", err);
        }
    }

    function drawSparkline() {
        const xStep = 300 / (winProbHistory.length - 1);
        let pathD = "";
        
        winProbHistory.forEach((prob, index) => {
            const x = index * xStep;
            const y = 70 - (prob * 60);
            
            if (index === 0) {
                pathD = `M ${x} ${y}`;
            } else {
                pathD += ` L ${x} ${y}`;
            }
            
            if (index === winProbHistory.length - 1) {
                sparklineDot.setAttribute("cx", x);
                sparklineDot.setAttribute("cy", y);
            }
        });
        
        sparklinePath.setAttribute("d", pathD);
    }

    // 6. Delivery Simulation Flow
    async function triggerDeliverySimulation() {
        simulateBtn.disabled = true;
        simulateBtn.style.opacity = "0.6";
        
        const payload = {
            batsman: batsmanSelect.value,
            bowler: bowlerSelect.value,
            bowling_speed_kph: parseFloat(deliverySpeed.value),
            bowling_path_type: deliveryVariation.value,
            pitch_line: selectedLine,
            pitch_length: selectedLength,
            weather: matchWeather.value,
            ball_type: ballType.value,
            ball_age: parseFloat(ballAge.value),
            inning: parseInt(matchInning.value),
            overs: parseFloat(matchOvers.value),
            wickets: parseInt(matchWickets.value),
            venue: matchVenue.value
        };

        try {
            const res = await fetch("/api/predict-delivery", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            
            if (!res.ok) throw new Error("Predict delivery failed");
            const data = await res.json();
            
            animateBallDelivery(data.trajectory_mod, () => {
                updateSimulationHUD(payload.bowling_speed_kph, data);
                updateMatchState(data.runs_scored, data.is_wicket);
                simulateBtn.disabled = false;
                simulateBtn.style.opacity = "1";
            });
            
        } catch (err) {
            console.error("Simulation error:", err);
            simulateBtn.disabled = false;
            simulateBtn.style.opacity = "1";
        }
    }

    function updateSimulationHUD(speed, data) {
        document.querySelectorAll(".hud-card").forEach(c => c.classList.add("active"));
        setTimeout(() => {
            document.querySelectorAll(".hud-card").forEach(c => c.classList.remove("active"));
        }, 1200);

        hudSpeed.textContent = `${speed} Kph`;
        hudReaction.textContent = data.batsman_reaction;
        hudContact.textContent = data.shot_contact_quality || "Solid";
        
        const outcomeCard = document.getElementById("hud-outcome-card");
        outcomeCard.classList.remove("wicket-flash");

        if (data.is_wicket === 1) {
            hudRuns.textContent = "OUT (Wicket)";
            outcomeCard.classList.add("wicket-flash");
            hudRuns.style.color = "var(--neon-pink)";
        } else {
            hudRuns.textContent = `${data.runs_scored} Run${data.runs_scored !== 1 ? 's' : ''}`;
            hudRuns.style.color = "var(--neon-green)";
        }
    }

    function updateMatchState(runsScored, isWicket) {
        ballCounter++;
        
        let oversVal = parseFloat(matchOvers.value);
        let wicketsVal = parseInt(matchWickets.value);
        
        let intOvers = Math.floor(oversVal);
        let ballsBowled = Math.round((oversVal - intOvers) * 10);
        
        ballsBowled++;
        if (ballsBowled >= 6) {
            intOvers++;
            ballsBowled = 0;
        }
        matchOvers.value = (intOvers + (ballsBowled / 10)).toFixed(1);
        
        if (isWicket === 1) {
            wicketsVal = Math.min(10, wicketsVal + 1);
            matchWickets.value = wicketsVal;
        }
        
        if (matchInning.value === "2") {
            let runsNeed = parseInt(runsNeeded.value);
            let ballsRem = parseInt(ballsRemaining.value);
            
            runsNeed = Math.max(0, runsNeed - runsScored);
            ballsRem = Math.max(0, ballsRem - 1);
            
            runsNeeded.value = runsNeed;
            ballsRemaining.value = ballsRem;
            
            if (runsNeed <= 0) {
                alert(`${batsmanSelect.value}'s team wins the match!`);
                resetMatchState();
            } else if (wicketsVal >= 10 || ballsRem <= 0) {
                alert(`Bowling team wins the match!`);
                resetMatchState();
            }
        }

        let age = parseFloat(ballAge.value);
        ballAge.value = (age + 0.1).toFixed(1);
        
        updateWinProbability();
    }

    function resetMatchState() {
        matchOvers.value = "15.0";
        matchWickets.value = "4";
        runsNeeded.value = "45";
        ballsRemaining.value = "30";
        ballAge.value = "15.0";
        winProbHistory = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5];
        updateWinProbability();
    }
});
