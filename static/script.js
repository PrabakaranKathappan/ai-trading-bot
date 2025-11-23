// API base URL
const API_URL = '';

// Refresh interval (in milliseconds)
const REFRESH_INTERVAL = 5000;

// Auto-refresh timer
let refreshTimer = null;

// Access PIN (stored in memory only)
let accessPin = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function () {
    console.log('Dashboard initialized');
    registerServiceWorker();
    checkInstallPrompt();

    // Show PIN modal on load
    showPinModal();
});

// Show PIN Modal
function showPinModal() {
    const modal = document.getElementById('pinModal');
    const input = document.getElementById('pinInput');
    const error = document.getElementById('pinError');

    modal.style.display = 'flex';
    input.value = '';
    input.focus();
    error.textContent = '';

    // Stop any existing refresh timer
    stopAutoRefresh();
}

// Submit PIN
async function submitPin() {
    const input = document.getElementById('pinInput');
    const error = document.getElementById('pinError');
    const pin = input.value.trim();

    if (pin.length < 4) {
        error.textContent = 'Please enter a valid PIN';
        return;
    }

    // Store PIN temporarily
    accessPin = pin;

    // Test PIN by fetching status
    try {
        const response = await fetch(`${API_URL}/api/status`, {
            headers: {
                'X-Access-Pin': accessPin
            }
        });

        if (response.ok) {
            // Success
            document.getElementById('pinModal').style.display = 'none';
            refreshData();
            startAutoRefresh();
        } else {
            // Failed
            error.textContent = 'Invalid PIN. Please try again.';
            accessPin = null;
        }
    } catch (err) {
        console.error('Error verifying PIN:', err);
        error.textContent = 'Connection error. Please try again.';
        accessPin = null;
    }
}

// Handle Enter key in PIN input
document.getElementById('pinInput').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        submitPin();
    }
});

// Start auto-refresh
function startAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
    }
    refreshTimer = setInterval(refreshData, REFRESH_INTERVAL);
}

// Stop auto-refresh
function stopAutoRefresh() {
    if (refreshTimer) {
        clearInterval(refreshTimer);
        refreshTimer = null;
    }
}

// Refresh all data
async function refreshData() {
    if (!accessPin) return;

    try {
        const headers = { 'X-Access-Pin': accessPin };

        const response = await fetch(`${API_URL}/api/status`, { headers });

        if (response.status === 401) {
            showPinModal();
            return;
        }

        const data = await response.json();

        updateStatus(data);
        updatePositions(data.positions || []);
        updateTrades(data.trades || []);
        // updatePerformance(data.stats || {});
        updateRiskMetrics(data.risk_metrics || {});
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Update status
function updateStatus(data) {
    // Bot status
    const statusBadge = document.getElementById('botStatus');
    statusBadge.textContent = data.status || 'Unknown';
    statusBadge.className = 'status-badge ' + (data.status === 'running' ? 'running' : 'stopped');

    // Trading mode
    const modeBadge = document.getElementById('tradingMode');
    modeBadge.textContent = data.mode ? data.mode.toUpperCase() : 'PAPER';

    // Today's P&L
    const pnlElement = document.getElementById('todayPnl');
    const pnl = data.today_pnl || 0;
    pnlElement.textContent = formatCurrency(pnl);
    pnlElement.className = 'pnl-amount ' + (pnl < 0 ? 'negative' : '');

    // Capital
    document.getElementById('capital').textContent = formatCurrency(data.capital || 70000);

    // Win rate
    const winRate = data.stats ? data.stats.win_rate || 0 : 0;
    document.getElementById('winRate').textContent = winRate.toFixed(1) + '%';
}

// Update positions
function updatePositions(positions) {
    const container = document.getElementById('positionsContainer');
    const countBadge = document.getElementById('positionCount');

    countBadge.textContent = positions.length;

    if (positions.length === 0) {
        container.innerHTML = '<div class="empty-state">No open positions</div>';
        return;
    }

    container.innerHTML = positions.map(position => `
        <div class="position-card">
            <div class="position-header">
                <div class="position-symbol">${position.symbol || 'N/A'}</div>
                <div class="position-type ${position.option_type}">${position.option_type || 'N/A'}</div>
            </div>
            <div class="position-details">
                <div class="position-detail">
                    <div class="position-detail-label">Entry Price</div>
                    <div class="position-detail-value">${formatCurrency(position.entry_price)}</div>
                </div>
                <div class="position-detail">
                    <div class="position-detail-label">Current Price</div>
                    <div class="position-detail-value">${formatCurrency(position.current_price || position.entry_price)}</div>
                </div>
                <div class="position-detail">
                    <div class="position-detail-label">Quantity</div>
                    <div class="position-detail-value">${position.quantity || 0}</div>
                </div>
                <div class="position-detail">
                    <div class="position-detail-label">Unrealized P&L</div>
                    <div class="position-detail-value" style="color: ${(position.unrealized_pnl || 0) >= 0 ? '#10b981' : '#ef4444'}">
                        ${formatCurrency(position.unrealized_pnl || 0)}
                    </div>
                </div>
                <div class="position-detail">
                    <div class="position-detail-label">Stop Loss</div>
                    <div class="position-detail-value">${formatCurrency(position.stop_loss)}</div>
                </div>
                <div class="position-detail">
                    <div class="position-detail-label">Target</div>
                    <div class="position-detail-value">${formatCurrency(position.target)}</div>
                </div>
            </div>
        </div>
    `).join('');
}

// Update trades
function updateTrades(trades) {
    const container = document.getElementById('tradesContainer');
    const countBadge = document.getElementById('tradeCount');

    countBadge.textContent = trades.length;

    if (trades.length === 0) {
        container.innerHTML = '<div class="empty-state">No trades today</div>';
        return;
    }

    container.innerHTML = trades.map(trade => `
        <div class="trade-card">
            <div class="trade-detail">
                <div class="trade-detail-label">Time</div>
                <div class="trade-detail-value">${formatTime(trade.timestamp)}</div>
            </div>
            <div class="trade-detail">
                <div class="trade-detail-label">Symbol</div>
                <div class="trade-detail-value">${trade.symbol || 'N/A'}</div>
            </div>
            <div class="trade-detail">
                <div class="trade-detail-label">Type</div>
                <div class="trade-detail-value">${trade.option_type || 'N/A'}</div>
            </div>
            <div class="trade-detail">
                <div class="trade-detail-label">Action</div>
                <div class="trade-detail-value">${trade.action || 'N/A'}</div>
            </div>
            <div class="trade-detail">
                <div class="trade-detail-label">Qty</div>
                <div class="trade-detail-value">${trade.quantity || 0}</div>
            </div>
            <div class="trade-detail">
                <div class="trade-detail-label">Entry</div>
                <div class="trade-detail-value">${formatCurrency(trade.entry_price)}</div>
            </div>
            <div class="trade-detail">
                <div class="trade-detail-label">Exit</div>
                <div class="trade-detail-value">${trade.exit_price ? formatCurrency(trade.exit_price) : '-'}</div>
            </div>
            <div class="trade-detail">
                <div class="trade-detail-label">P&L</div>
                <div class="trade-detail-value" style="color: ${(trade.pnl || 0) >= 0 ? '#10b981' : '#ef4444'}">
                    ${trade.pnl ? formatCurrency(trade.pnl) : '-'}
                </div>
            </div>
            <div class="trade-detail">
                <div class="trade-detail-label">Status</div>
                <div class="trade-detail-value">${trade.status || 'N/A'}</div>
            </div>
        </div>
    `).join('');
}

// Update performance stats
// function updatePerformance(stats) {
//     document.getElementById('totalTrades').textContent = stats.total_trades || 0;
//     document.getElementById('winningTrades').textContent = stats.winning_trades || 0;
//     document.getElementById('avgWin').textContent = formatCurrency(stats.avg_win || 0);
//     document.getElementById('avgLoss').textContent = formatCurrency(stats.avg_loss || 0);
// }

// Update risk metrics
// Update risk metrics
function updateRiskMetrics(metrics) {
    const openPos = metrics.open_positions || 0;
    const maxPos = metrics.max_positions || 3;
    document.getElementById('openPositions').textContent = `${openPos} / ${maxPos}`;

    document.getElementById('dailyLossLimit').textContent = formatCurrency(metrics.remaining_daily_loss || 0);
    document.getElementById('totalExposure').textContent = formatCurrency(metrics.total_exposure || 0);
}

// Configuration Functions
// Configuration Functions
async function openConfigModal() {
    document.getElementById('configModal').style.display = 'flex';
    document.getElementById('configError').textContent = '';

    if (accessPin) {
        try {
            // Load Strategies
            const response = await fetch(`${API_URL}/api/strategies`, {
                headers: { 'X-Access-Pin': accessPin }
            });
            if (response.ok) {
                const strategies = await response.json();
                document.getElementById('strat_rsi').checked = strategies.RSI;
                document.getElementById('strat_macd').checked = strategies.MACD;
                document.getElementById('strat_bollinger_bands').checked = strategies.BOLLINGER_BANDS;
                document.getElementById('strat_ema').checked = strategies.EMA;
                document.getElementById('strat_breakout').checked = strategies.BREAKOUT;
                document.getElementById('strat_order_flow').checked = strategies.ORDER_FLOW;
            }

            // Load Risk Settings
            const riskResponse = await fetch(`${API_URL}/api/settings/risk`, {
                headers: { 'X-Access-Pin': accessPin }
            });
            if (riskResponse.ok) {
                const risk = await riskResponse.json();
                document.getElementById('riskPerTrade').value = risk.RISK_PER_TRADE;
                document.getElementById('stopLoss').value = risk.STOP_LOSS_PERCENT;
                document.getElementById('target').value = risk.TARGET_PERCENT;
                document.getElementById('trailingStop').value = risk.TRAILING_STOP_PERCENT;
                document.getElementById('maxDailyLoss').value = risk.MAX_DAILY_LOSS;
                document.getElementById('secureProfitEnabled').checked = risk.SECURE_PROFIT_ENABLED;
                document.getElementById('secureProfitAmount').value = risk.SECURE_PROFIT_AMOUNT;
            }
        } catch (error) {
            console.error('Error loading settings:', error);
        }
    }
}

function closeConfigModal() {
    document.getElementById('configModal').style.display = 'none';
}

async function saveCredentials() {
    const apiKey = document.getElementById('apiKey').value.trim();
    const apiSecret = document.getElementById('apiSecret').value.trim();
    const error = document.getElementById('configError');

    if (!accessPin) return;

    // Save Strategies
    const strategies = {
        RSI: document.getElementById('strat_rsi').checked,
        MACD: document.getElementById('strat_macd').checked,
        BOLLINGER_BANDS: document.getElementById('strat_bollinger_bands').checked,
        EMA: document.getElementById('strat_ema').checked,
        BREAKOUT: document.getElementById('strat_breakout').checked,
        ORDER_FLOW: document.getElementById('strat_order_flow').checked
    };

    // Save Risk Settings
    const riskSettings = {
        RISK_PER_TRADE: document.getElementById('riskPerTrade').value,
        STOP_LOSS_PERCENT: document.getElementById('stopLoss').value,
        TARGET_PERCENT: document.getElementById('target').value,
        TRAILING_STOP_PERCENT: document.getElementById('trailingStop').value,
        MAX_DAILY_LOSS: document.getElementById('maxDailyLoss').value,
        SECURE_PROFIT_ENABLED: document.getElementById('secureProfitEnabled').checked,
        SECURE_PROFIT_AMOUNT: document.getElementById('secureProfitAmount').value
    };

    try {
        // Save Strategies
        await fetch(`${API_URL}/api/strategies`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Access-Pin': accessPin
            },
            body: JSON.stringify(strategies)
        });

        // Save Risk Settings
        await fetch(`${API_URL}/api/settings/risk`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Access-Pin': accessPin
            },
            body: JSON.stringify(riskSettings)
        });
    } catch (e) {
        console.error('Error saving settings:', e);
    }

    // Save Credentials (only if provided)
    if (apiKey && apiSecret) {
        try {
            const response = await fetch(`${API_URL}/api/configure`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Access-Pin': accessPin
                },
                body: JSON.stringify({
                    api_key: apiKey,
                    api_secret: apiSecret
                })
            });

            const data = await response.json();

            if (response.ok) {
                closeConfigModal();
                alert('Settings saved! Please authenticate with Upstox if prompted.');
                checkAuth();
            } else {
                error.textContent = data.error || 'Failed to save credentials';
            }
        } catch (err) {
            console.error('Error saving credentials:', err);
            error.textContent = 'Connection error';
        }
    } else {
        // If only strategies were updated
        closeConfigModal();
        alert('Settings saved!');
    }
}

async function checkAuth() {
    if (!accessPin) return;
    try {
        const response = await fetch(`${API_URL}/login`, {
            headers: { 'X-Access-Pin': accessPin }
        });
        const data = await response.json();
        if (data.auth_url) {
            if (confirm('Authentication required. Open Upstox login page?')) {
                window.open(data.auth_url, '_blank');
            }
        }
    } catch (error) {
        console.error('Error checking auth:', error);
    }
}

// Control functions
async function pauseTrading() {
    if (!accessPin) return;
    try {
        const response = await fetch(`${API_URL}/api/control/pause`, {
            method: 'POST',
            headers: { 'X-Access-Pin': accessPin }
        });
        if (response.status === 401) { showPinModal(); return; }
        const data = await response.json();
        console.log('Trading paused:', data);
        refreshData();
    } catch (error) {
        console.error('Error pausing trading:', error);
        alert('Failed to pause trading');
    }
}

async function resumeTrading() {
    if (!accessPin) return;
    try {
        const response = await fetch(`${API_URL}/api/control/resume`, {
            method: 'POST',
            headers: { 'X-Access-Pin': accessPin }
        });
        if (response.status === 401) { showPinModal(); return; }
        const data = await response.json();
        console.log('Trading resumed:', data);
        refreshData();
    } catch (error) {
        console.error('Error resuming trading:', error);
        alert('Failed to resume trading');
    }
}

async function squareOffAll() {
    if (!accessPin) return;
    if (!confirm('Are you sure you want to square off all positions?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/control/square-off`, {
            method: 'POST',
            headers: { 'X-Access-Pin': accessPin }
        });
        if (response.status === 401) { showPinModal(); return; }
        const data = await response.json();
        console.log('Squared off all positions:', data);
        refreshData();
    } catch (error) {
        console.error('Error squaring off:', error);
        alert('Failed to square off positions');
    }
}

// Utility functions
function formatCurrency(value) {
    if (value === null || value === undefined) return '₹0.00';
    return '₹' + parseFloat(value).toLocaleString('en-IN', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
}

function formatTime(timestamp) {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-IN', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// PWA Service Worker Registration
function registerServiceWorker() {
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/sw.js')
            .then(registration => {
                console.log('Service Worker registered:', registration);
            })
            .catch(error => {
                console.log('Service Worker registration failed:', error);
            });
    }
}

// PWA Install Prompt
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    showInstallButton();
});

function showInstallButton() {
    // You can add an install button to the UI here
    console.log('App can be installed');
}

function checkInstallPrompt() {
    // Check if app is already installed
    if (window.matchMedia('(display-mode: standalone)').matches) {
        console.log('App is installed');
    }
}
