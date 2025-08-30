// 案件データ修正モーダルを表示
async function editProjectData(projectId) {
    try {
        const response = await fetch(`/api/project/${projectId}`);
        const project = await response.json();
        displayEditForm(project);
        
        const modal = new bootstrap.Modal(document.getElementById('editModal'));
        modal.show();
    } catch (error) {
        console.error('案件データ取得エラー:', error);
        alert('データの読み込みに失敗しました');
    }
}

// 修正フォームを表示
function displayEditForm(project) {
    const container = document.getElementById('editModalContent');
    
    let html = '<form id="editForm">';
    html += '<input type="hidden" id="editProjectId" value="' + project.id + '">';
    
    html += '<div class="row mb-3">';
    html += '<div class="col-md-6">';
    html += '<label class="form-label">報告日</label>';
    html += '<input type="date" class="form-control" id="editReportDate" value="' + (project.report_date || '') + '">';
    html += '</div>';
    html += '<div class="col-md-6">';
    html += '<label class="form-label">報告者</label>';
    html += '<input type="text" class="form-control" id="editReporter" value="' + (project.reporter || '') + '">';
    html += '</div>';
    html += '</div>';
    
    html += '<div class="row mb-3">';
    html += '<div class="col-md-6">';
    html += '<label class="form-label">客先名</label>';
    html += '<input type="text" class="form-control" id="editClientName" value="' + (project.client_name || '') + '">';
    html += '</div>';
    html += '<div class="col-md-6">';
    html += '<label class="form-label">客先部署</label>';
    html += '<input type="text" class="form-control" id="editClientDepartment" value="' + (project.client_department || '') + '">';
    html += '</div>';
    html += '</div>';
    
    html += '<div class="row mb-3">';
    html += '<div class="col-md-6">';
    html += '<label class="form-label">客先担当者</label>';
    html += '<input type="text" class="form-control" id="editClientPerson" value="' + (project.client_person || '') + '">';
    html += '</div>';
    html += '<div class="col-md-6">';
    html += '<label class="form-label">同行社員</label>';
    html += '<input type="text" class="form-control" id="editEmployeeName" value="' + (project.employee_name || '') + '">';
    html += '</div>';
    html += '</div>';
    
    html += '<div class="mb-3">';
    html += '<label class="form-label">製品名</label>';
    html += '<input type="text" class="form-control" id="editProductName" value="' + (project.product_name || '') + '">';
    html += '</div>';
    
    html += '<div class="mb-3">';
    html += '<label class="form-label">案件内容</label>';
    html += '<textarea class="form-control" id="editContent" rows="8">' + (project.content || '') + '</textarea>';
    html += '</div>';
    
    html += '</form>';
    
    container.innerHTML = html;
}

// 案件データを保存
async function saveProjectData() {
    const projectId = document.getElementById('editProjectId').value;
    
    const data = {
        report_date: document.getElementById('editReportDate').value,
        reporter: document.getElementById('editReporter').value,
        client_name: document.getElementById('editClientName').value,
        client_department: document.getElementById('editClientDepartment').value,
        client_person: document.getElementById('editClientPerson').value,
        employee_name: document.getElementById('editEmployeeName').value,
        product_name: document.getElementById('editProductName').value,
        content: document.getElementById('editContent').value
    };
    
    try {
        const response = await fetch(`/api/project/${projectId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        if (response.ok) {
            alert('データを保存しました');
            
            // モーダルを閉じる
            const modal = bootstrap.Modal.getInstance(document.getElementById('editModal'));
            modal.hide();
            
            // 表示を更新(必要に応じて再読み込み)
            // loadReports();
        } else {
            throw new Error('保存に失敗しました');
        }
    } catch (error) {
        console.error('保存エラー:', error);
        alert('データの保存に失敗しました: ' + error.message);
    }
}