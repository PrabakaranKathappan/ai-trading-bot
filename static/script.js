// API base URL
const API_URL = '';

// Refresh interval (in milliseconds)
const REFRESH_INTERVAL = 5000;

// Auto-refresh timer
let refreshTimer = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function () {
    console.log('Dashboard initialized');
    registerServiceWorker();
    checkInstallPrompt();
    refreshData();
    startAutoRefresh();
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
    try {
        const response = await fetch(`${API_URL}/api/status`);
        const data = await response.json();

        updateStatus(data);
        updatePositions(data.positions || []);
        updateTrades(data.trades || []);
        updatePerformance(data.stats || {});
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
function updatePerformance(stats) {
    document.getElementById('totalTrades').textContent = stats.total_trades || 0;
    document.getElementById('winningTrades').textContent = stats.winning_trades || 0;
    document.getElementById('avgWin').textContent = formatCurrency(stats.avg_win || 0);
    document.getElementById('avgLoss').textContent = formatCurrency(stats.avg_loss || 0);
}

// Update risk metrics
function updateRiskMetrics(metrics) {
    const openPos = metrics.open_positions || 0;
    const maxPos = metrics.max_positions || 3;
    document.getElementById('openPositions').textContent = `${openPos} / ${maxPos}`;

    document.getElementById('dailyLossLimit').textContent = formatCurrency(metrics.remaining_daily_loss || 0);
    document.getElementById('totalExposure').textContent = formatCurrency(metrics.total_exposure || 0);
}

// Control functions
async function pauseTrading() {
    try {
        const response = await fetch(`${API_URL}/api/control/pause`, {
            method: 'POST'
        });
        const data = await response.json();
        console.log('Trading paused:', data);
        refreshData();
    } catch (error) {
        console.error('Error pausing trading:', error);
        alert('Failed to pause trading');
    }
}

async function resumeTrading() {
    try {
        const response = await fetch(`${API_URL}/api/control/resume`, {
            method: 'POST'
        });
        const data = await response.json();
        console.log('Trading resumed:', data);
        refreshData();
    } catch (error) {
        console.error('Error resuming trading:', error);
        alert('Failed to resume trading');
    }
}

async function squareOffAll() {
    if (!confirm('Are you sure you want to square off all positions?')) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/control/square-off`, {
            method: 'POST'
        });
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
