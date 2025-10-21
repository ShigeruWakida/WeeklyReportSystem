// 週報管理システム フロントエンド - 修正版
let allReports = [];
let selectedReports = new Map();
let currentPage = 1;
let totalPages = 1;

// 初期化
document.addEventListener('DOMContentLoaded', function() {
    console.log('週報システム初期化開始');
    
    try {
        // 各機能を順番に初期化
        loadReporters();
        loadClients();
        loadProducts();
        loadReports();
        loadStats();
        
        // イベントリスナー設定
        const applyBtn = document.getElementById('applyFilter');
        if (applyBtn) {
            applyBtn.addEventListener('click', function() {
                loadReports();
            });
        }
        
        const clearBtn = document.getElementById('clearFilter');
        if (clearBtn) {
            clearBtn.addEventListener('click', function() {
                clearAllFilters();
            });
        }
        
        // Enterキーで検索
        const searchInput = document.getElementById('searchText');
        if (searchInput) {
            searchInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    loadReports();
                }
            });
        }
        
        console.log('初期化完了');
    } catch (error) {
        console.error('初期化エラー:', error);
        const container = document.getElementById('reportsContainer');
        if (container) {
            container.innerHTML = '<div class="alert alert-danger">初期化エラー: ' + error.message + '</div>';
        }
    }
});

// 報告者リスト読み込み
async function loadReporters() {
    try {
        const response = await fetch('/api/reporters');
        const reporters = await response.json();
        const select = document.getElementById('reporterFilter');
        if (select) {
            select.innerHTML = '<option value="">全て</option>';
            reporters.forEach(reporter => {
                const option = document.createElement('option');
                option.value = reporter;
                option.textContent = reporter;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('報告者リスト読み込みエラー:', error);
    }
}

// 客先リスト読み込み
async function loadClients() {
    try {
        const response = await fetch('/api/clients');
        const clients = await response.json();
        const select = document.getElementById('clientFilter');
        if (select) {
            select.innerHTML = '<option value="">全て</option>';
            clients.forEach(client => {
                const option = document.createElement('option');
                option.value = client;
                option.textContent = client;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('客先リスト読み込みエラー:', error);
    }
}

// 製品リスト読み込み
async function loadProducts() {
    try {
        const response = await fetch('/api/products');
        const products = await response.json();
        const select = document.getElementById('productFilter');
        if (select) {
            select.innerHTML = '<option value="">全て</option>';
            products.forEach(product => {
                const option = document.createElement('option');
                option.value = product;
                option.textContent = product;
                select.appendChild(option);
            });
        }
    } catch (error) {
        console.error('製品リスト読み込みエラー:', error);
    }
}

// レポート読み込み
async function loadReports(page = 1) {
    try {
        currentPage = page;
        const params = new URLSearchParams();
        
        const reporter = document.getElementById('reporterFilter')?.value;
        if (reporter) params.append('reporter', reporter);
        
        const client = document.getElementById('clientFilter')?.value;
        if (client) params.append('client', client);
        
        const product = document.getElementById('productFilter')?.value;
        if (product) params.append('product', product);
        
        const dateFrom = document.getElementById('dateFrom')?.value;
        if (dateFrom) params.append('date_from', dateFrom);
        
        const dateTo = document.getElementById('dateTo')?.value;
        if (dateTo) params.append('date_to', dateTo);
        
        const search = document.getElementById('searchText')?.value;
        if (search) params.append('search', search);
        
        params.append('page', page);
        params.append('per_page', '10');
        
        const response = await fetch('/api/reports?' + params.toString());
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        
        const data = await response.json();
        allReports = data.reports;
        totalPages = Math.ceil(data.total_count / 10);
        
        displayReports(allReports);
        displayPagination(data.total_count);
        
        // 件数表示を更新
        const totalCount = document.getElementById('totalCount');
        if (totalCount) {
            totalCount.textContent = data.total_count;
        }
    } catch (error) {
        console.error('レポート読み込みエラー:', error);
        const container = document.getElementById('reportsContainer');
        if (container) {
            container.innerHTML = '<div class="alert alert-danger">データの読み込みに失敗しました: ' + error.message + '</div>';
        }
    }
}

// レポート表示
function displayReports(reports) {
    const container = document.getElementById('reportsContainer');
    if (!container) return;
    
    if (!reports || reports.length === 0) {
        container.innerHTML = '<div class="alert alert-info">該当する週報がありません</div>';
        return;
    }
    
    let html = '<div class="table-responsive">';
    html += '<table class="table table-hover">';
    html += '<thead><tr>';
    html += '<th width="40px"><input type="checkbox" id="selectAll" onchange="toggleSelectAll()" class="form-check-input"></th>';
    html += '<th>日付</th><th>報告者</th><th>客先</th><th>製品</th>';
    html += '</tr></thead><tbody>';
    
    reports.forEach(report => {
        const isSelected = selectedReports.has(report.mail_id);
        html += '<tr>';
        html += '<td><input type="checkbox" class="form-check-input report-checkbox" ';
        html += 'data-mail-id="' + report.mail_id + '" ';
        html += 'onchange="toggleReportSelection(\'' + report.mail_id + '\')" ';
        html += (isSelected ? 'checked' : '') + '></td>';
        
        html += '<td>' + formatDate(report.report_date) + '</td>';
        
        html += '<td>';
        if (report.reporter && report.reporter !== '-') {
            html += '<a href="javascript:void(0)" onclick="filterByReporter(\'' + report.reporter + '\')" class="reporter-link">';
            html += report.reporter + '</a>';
        } else {
            html += '-';
        }
        html += '</td>';
        
        html += '<td>';
        const clients = (report.clients || '-').split(',');
        clients.forEach((client, index) => {
            const trimmedClient = client.trim();
            if (trimmedClient && trimmedClient !== '-') {
                if (index > 0) html += ', ';
                html += '<a href="javascript:void(0)" onclick="showClientProjects(\'' + trimmedClient + '\')" class="client-link">';
                html += trimmedClient + '</a>';
            }
        });
        html += '</td>';
        
        html += '<td>';
        const productsText = report.products || '-';
        if (productsText !== '-') {
            // カンマ（,）と日本語読点（、）の両方で分割
            const products = productsText.split(/[,、]/).map(p => p.trim()).filter(p => p && p !== '-');
            products.forEach((product, index) => {
                if (index > 0) html += ', ';
                html += '<a href="javascript:void(0)" onclick="showProductProjects(\'' + product + '\')" class="product-link">';
                html += product + '</a>';
            });
        } else {
            html += '-';
        }
        html += '</td>';
        
        html += '</tr>';
    });
    
    html += '</tbody></table></div>';
    container.innerHTML = html;
}

// 日付フォーマット
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ja-JP');
}

// ページネーション表示
function displayPagination(totalCount) {
    const container = document.getElementById('paginationContainer');
    if (!container) return;
    
    const perPage = 10;
    const totalPages = Math.ceil(totalCount / perPage);
    
    // ページが1つ以下の場合はページネーションを非表示
    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }
    
    let html = '<nav><ul class="pagination pagination-sm mb-0">';
    
    // 前へボタン
    const prevDisabled = currentPage <= 1 ? ' disabled' : '';
    html += `<li class="page-item${prevDisabled}">`;
    if (currentPage > 1) {
        html += `<a class="page-link" href="javascript:void(0)" onclick="loadReports(${currentPage - 1})">前へ</a>`;
    } else {
        html += '<span class="page-link">前へ</span>';
    }
    html += '</li>';
    
    // ページ番号ボタン
    const startPage = Math.max(1, currentPage - 2);
    const endPage = Math.min(totalPages, currentPage + 2);
    
    if (startPage > 1) {
        html += '<li class="page-item"><a class="page-link" href="javascript:void(0)" onclick="loadReports(1)">1</a></li>';
        if (startPage > 2) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        const active = i === currentPage ? ' active' : '';
        html += `<li class="page-item${active}">`;
        if (i === currentPage) {
            html += `<span class="page-link">${i}</span>`;
        } else {
            html += `<a class="page-link" href="javascript:void(0)" onclick="loadReports(${i})">${i}</a>`;
        }
        html += '</li>';
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += '<li class="page-item disabled"><span class="page-link">...</span></li>';
        }
        html += `<li class="page-item"><a class="page-link" href="javascript:void(0)" onclick="loadReports(${totalPages})">${totalPages}</a></li>`;
    }
    
    // 次へボタン
    const nextDisabled = currentPage >= totalPages ? ' disabled' : '';
    html += `<li class="page-item${nextDisabled}">`;
    if (currentPage < totalPages) {
        html += `<a class="page-link" href="javascript:void(0)" onclick="loadReports(${currentPage + 1})">次へ</a>`;
    } else {
        html += '<span class="page-link">次へ</span>';
    }
    html += '</li>';
    
    html += '</ul></nav>';
    
    // 件数表示も追加
    const startItem = (currentPage - 1) * perPage + 1;
    const endItem = Math.min(currentPage * perPage, totalCount);
    html += `<div class="small text-muted mt-2">${startItem} - ${endItem} 件 (全 ${totalCount} 件中)</div>`;
    
    container.innerHTML = html;
}

// 統計情報読み込み
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) {
            throw new Error('統計API応答エラー: ' + response.status);
        }
        const stats = await response.json();
        displayStats(stats);
    } catch (error) {
        console.error('統計情報読み込みエラー:', error);
        const container = document.getElementById('statsContainer');
        if (container) {
            container.innerHTML = '<div class="alert alert-danger small">統計データの読み込みに失敗しました</div>';
        }
    }
}

// 統計情報表示
function displayStats(stats) {
    const container = document.getElementById('statsContainer');
    if (!container || !stats) return;
    
    let html = '<div class="mb-3">';
    html += '<h6>報告者別</h6>';
    html += '<ul class="list-unstyled small">';
    (stats.by_reporter || []).slice(0, 5).forEach(item => {
        html += '<li>' + item.reporter + ': <span class="badge bg-primary">' + item.count + '</span></li>';
    });
    html += '</ul></div>';
    
    html += '<div class="mb-3">';
    html += '<h6>客先別TOP5</h6>';
    html += '<ul class="list-unstyled small">';
    (stats.by_client || []).slice(0, 5).forEach(item => {
        html += '<li>' + item.client + ': <span class="badge bg-success">' + item.count + '</span></li>';
    });
    html += '</ul></div>';
    
    container.innerHTML = html;
}

// フィルタクリア
function clearAllFilters() {
    const elements = ['reporterFilter', 'clientFilter', 'productFilter', 'dateFrom', 'dateTo', 'searchText'];
    elements.forEach(id => {
        const element = document.getElementById(id);
        if (element) element.value = '';
    });
    loadReports();
}

// 報告者でフィルタ
function filterByReporter(reporter) {
    const select = document.getElementById('reporterFilter');
    if (select) {
        select.value = reporter;
        loadReports();
    }
}

// チェックボックス関連（簡略版）
function toggleSelectAll() {
    const selectAll = document.getElementById('selectAll');
    const checkboxes = document.querySelectorAll('.report-checkbox');
    
    checkboxes.forEach(cb => {
        cb.checked = selectAll.checked;
        const mailId = cb.getAttribute('data-mail-id');
        
        if (selectAll.checked) {
            // すべて選択の場合
            selectedReports.set(mailId, true);
            loadMailDetail(mailId);
        } else {
            // すべて解除の場合
            selectedReports.delete(mailId);
            const card = document.getElementById('selected-' + mailId);
            if (card) {
                card.remove();
            }
        }
    });
    
    updateSelectedReportsDisplay();
}

function toggleReportSelection(mailId) {
    const checkbox = document.querySelector(`input[data-mail-id="${mailId}"]`);
    
    if (checkbox && checkbox.checked) {
        // チェックされた場合、選択に追加して詳細を読み込み
        selectedReports.set(mailId, true);
        loadMailDetail(mailId);
    } else {
        // チェック解除された場合、選択から削除
        selectedReports.delete(mailId);
    }
    updateSelectedReportsDisplay();
}

function updateSelectedReportsDisplay() {
    const count = selectedReports.size;
    const countElement = document.getElementById('selectedCount');
    if (countElement) {
        countElement.textContent = count;
    }
    
    // 選択された週報エリアの表示/非表示
    const selectedArea = document.getElementById('selectedReportsArea');
    if (selectedArea) {
        selectedArea.style.display = count > 0 ? 'block' : 'none';
    }
}

// メール詳細を読み込み
async function loadMailDetail(mailId) {
    try {
        const response = await fetch('/api/mail_detail/' + mailId);
        if (!response.ok) {
            throw new Error('HTTP ' + response.status);
        }
        const reports = await response.json();
        displaySelectedReport(mailId, reports);
    } catch (error) {
        console.error('メール詳細読み込みエラー:', error);
    }
}

// 選択された週報を表示
function displaySelectedReport(mailId, reports) {
    const container = document.getElementById('selectedReportsContainer');
    if (!container || !reports || reports.length === 0) return;
    
    // 既存の同じmailIdの表示を削除
    const existingCard = document.getElementById('selected-' + mailId);
    if (existingCard) {
        existingCard.remove();
    }
    
    let html = '<div class="card mb-3" id="selected-' + mailId + '">';
    html += '<div class="card-header d-flex justify-content-between align-items-center">';
    html += '<h6 class="mb-0">' + formatDate(reports[0].report_date) + ' - ' + (reports[0].reporter || '-') + '</h6>';
    html += '<div class="d-flex align-items-center gap-2">';
    html += '<button type="button" class="btn btn-sm btn-outline-danger" onclick="deleteAllProjectsInMail(\'' + mailId + '\')" title="このメールの全案件を削除">';
    html += '<i class="bi bi-trash"></i> 削除';
    html += '</button>';
    html += '<button type="button" class="btn-close" onclick="removeSelectedReport(\'' + mailId + '\')"></button>';
    html += '</div>';
    html += '</div>';
    html += '<div class="card-body">';
    
    reports.forEach((report, index) => {
        if (index > 0) html += '<hr>';
        html += '<div class="mb-2">';
        html += '<div class="d-flex justify-content-between align-items-start">';
        html += '<div class="flex-grow-1">';
        html += '<strong>客先:</strong> ' + (report.client_name || '-');
        if (report.client_department) html += '(' + report.client_department + ')';
        if (report.client_person) html += ':' + report.client_person;
        html += '<br>';
        if (report.employee_name) html += '<strong>同行社員:</strong> ' + report.employee_name + '<br>';
        if (report.product_name) html += '<strong>製品名:</strong> ' + report.product_name + '<br>';
        html += '</div>';
        html += '<div class="text-end">';
        html += '<a href="javascript:void(0)" onclick="editProjectData(' + report.id + ')" class="btn btn-sm btn-outline-primary" title="データベース修正">ID:' + report.id + '</a>';
        html += '</div>';
        html += '</div>';
        if (report.content) {
            html += '<strong>内容:</strong><br>';
            html += '<div class="mt-1" style="white-space: pre-wrap;">' + report.content + '</div>';
        }
        html += '</div>';
    });
    
    html += '</div>';
    html += '</div>';
    
    container.insertAdjacentHTML('beforeend', html);
}

// 選択された週報を削除
function removeSelectedReport(mailId) {
    selectedReports.delete(mailId);
    const card = document.getElementById('selected-' + mailId);
    if (card) {
        card.remove();
    }
    
    // チェックボックスも解除
    const checkbox = document.querySelector(`input[data-mail-id="${mailId}"]`);
    if (checkbox) {
        checkbox.checked = false;
    }
    
    updateSelectedReportsDisplay();
}

// メール内の全案件を一括削除
async function deleteAllProjectsInMail(mailId) {
    try {
        const response = await fetch('/api/mail_detail/' + mailId);
        if (!response.ok) {
            throw new Error('メール詳細の取得に失敗しました');
        }
        const reports = await response.json();
        
        if (reports && reports.length > 0) {
            const confirmed = confirm(`このメール（${formatDate(reports[0].report_date)}）の全案件 ${reports.length} 件を削除しますか？`);
            if (confirmed) {
                const deleteResponse = await fetch('/api/delete_mail_projects/' + mailId, {
                    method: 'DELETE'
                });
                
                if (deleteResponse.ok) {
                    alert('全案件を削除しました');
                    // 選択されたレポートから削除
                    removeSelectedReport(mailId);
                    // リストを再読み込み
                    loadReports();
                } else {
                    throw new Error('削除に失敗しました');
                }
            }
        }
    } catch (error) {
        console.error('エラー:', error);
        alert('削除処理でエラーが発生しました: ' + error.message);
    }
}

// 客先案件表示
async function showClientProjects(client) {
    try {
        const response = await fetch('/api/client_projects/' + encodeURIComponent(client));
        const projects = await response.json();
        displayClientProjects(client, projects);
    } catch (error) {
        console.error('客先案件読み込みエラー:', error);
    }
}

function displayClientProjects(client, projects) {
    const container = document.getElementById('clientProjectsContainer');
    const titleElement = document.getElementById('clientProjectsTitle');
    const areaElement = document.getElementById('clientProjectsArea');
    
    if (!container || !titleElement || !areaElement) return;
    
    titleElement.textContent = client + 'の案件一覧 (' + projects.length + '件)';
    
    if (projects.length === 0) {
        container.innerHTML = '<div class="alert alert-info">該当する案件がありません</div>';
    } else {
        let html = '';
        projects.forEach(project => {
            html += '<div class="card mb-2">';
            html += '<div class="card-body">';
            html += '<div class="d-flex justify-content-between align-items-start">';
            html += '<div>';
            html += '<strong>' + formatDate(project.report_date) + '</strong> ';
            html += '<span class="text-muted">' + (project.reporter || '-') + '</span><br>';
            html += '客先: ' + (project.client_name || '-');
            if (project.client_department) html += '(' + project.client_department + ')';
            if (project.client_person) html += ':' + project.client_person;
            html += '<br>';
            if (project.employee_name) html += '同行: ' + project.employee_name + '<br>';
            if (project.product_name) html += '製品: ' + project.product_name + '<br>';
            html += '</div>';
            html += '<div class="text-end">';
            html += '<a href="javascript:void(0)" onclick="editProjectData(' + project.id + ')" class="btn btn-sm btn-outline-primary">ID:' + project.id + '</a>';
            html += '</div>';
            html += '</div>';
            if (project.content) {
                html += '<div class="mt-2"><small>' + project.content + '</small></div>';
            }
            html += '</div>';
            html += '</div>';
        });
        container.innerHTML = html;
    }
    
    areaElement.style.display = 'block';
}

// 製品案件表示
async function showProductProjects(product) {
    try {
        const response = await fetch('/api/product_projects/' + encodeURIComponent(product));
        const projects = await response.json();
        displayProductProjects(product, projects);
    } catch (error) {
        console.error('製品案件読み込みエラー:', error);
    }
}

function displayProductProjects(product, projects) {
    const container = document.getElementById('productProjectsContainer');
    const titleElement = document.getElementById('productProjectsTitle');
    const areaElement = document.getElementById('productProjectsArea');
    
    if (!container || !titleElement || !areaElement) return;
    
    titleElement.textContent = product + 'の案件一覧 (' + projects.length + '件)';
    
    if (projects.length === 0) {
        container.innerHTML = '<div class="alert alert-info">該当する案件がありません</div>';
    } else {
        let html = '';
        projects.forEach(project => {
            html += '<div class="card mb-2">';
            html += '<div class="card-body">';
            html += '<div class="d-flex justify-content-between align-items-start">';
            html += '<div>';
            html += '<strong>' + formatDate(project.report_date) + '</strong> ';
            html += '<span class="text-muted">' + (project.reporter || '-') + '</span><br>';
            html += '客先: ' + (project.client_name || '-');
            if (project.client_department) html += '(' + project.client_department + ')';
            if (project.client_person) html += ':' + project.client_person;
            html += '<br>';
            if (project.employee_name) html += '同行: ' + project.employee_name + '<br>';
            if (project.product_name) html += '製品: ' + project.product_name + '<br>';
            html += '</div>';
            html += '<div class="text-end">';
            html += '<a href="javascript:void(0)" onclick="editProjectData(' + project.id + ')" class="btn btn-sm btn-outline-primary">ID:' + project.id + '</a>';
            html += '</div>';
            html += '</div>';
            if (project.content) {
                html += '<div class="mt-2"><small>' + project.content + '</small></div>';
            }
            html += '</div>';
            html += '</div>';
        });
        container.innerHTML = html;
    }
    
    areaElement.style.display = 'block';
}

// 週報処理関連の機能は削除されました

// サイドバー表示切替
function toggleSidebar() {
    const sidebarColumn = document.getElementById('sidebarColumn');
    const mainColumn = document.getElementById('mainColumn');
    const toggleBtn = document.getElementById('toggleSidebarBtn');
    
    if (sidebarColumn.style.display === 'none') {
        // サイドバーを表示
        sidebarColumn.style.display = 'block';
        mainColumn.className = 'col-md-9';
        toggleBtn.innerHTML = '<i class="bi bi-layout-sidebar-inset"></i>';
        toggleBtn.title = 'サイドバー表示切替';
    } else {
        // サイドバーを非表示
        sidebarColumn.style.display = 'none';
        mainColumn.className = 'col-12';
        toggleBtn.innerHTML = '<i class="bi bi-layout-sidebar-inset-reverse"></i>';
        toggleBtn.title = 'サイドバー表示';
    }
}
