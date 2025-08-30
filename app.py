import os
import sqlite3
import json
from datetime import datetime
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS

# Flask初期化
app = Flask(__name__)
CORS(app)

# 設定
DATABASE = os.environ.get('DATABASE_PATH', 'weekly_reports.db')
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SECRET_KEY'] = SECRET_KEY

def get_db():
    """データベース接続を取得"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """データベースを初期化"""
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS weekly_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mail_id TEXT,
            report_date TEXT,
            reporter TEXT,
            client_name TEXT,
            client_department TEXT,
            client_person TEXT,
            employee_name TEXT,
            content TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route('/')
def index():
    """メインページ"""
    return render_template('index.html')

@app.route('/api/reports')
def get_reports():
    """週報データを取得するAPI"""
    # クエリパラメータ取得
    reporter = request.args.get('reporter')
    client = request.args.get('client')
    product = request.args.get('product')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    search = request.args.get('search')
    # ページネーション（バリデーション付き）
    try:
        page = int(request.args.get('page', 1))
    except (ValueError, TypeError):
        page = 1
    
    try:
        per_page = int(request.args.get('per_page', 20))
    except (ValueError, TypeError):
        per_page = 20
    
    # メールごとにグループ化したクエリ
    query = '''
        SELECT mail_id, 
               MIN(report_date) as report_date, 
               MIN(reporter) as reporter,
               COUNT(*) as report_count,
               GROUP_CONCAT(DISTINCT client_name) as clients,
               GROUP_CONCAT(DISTINCT product_name) as products,
               GROUP_CONCAT(content, ' | ') as all_content
        FROM weekly_reports
        WHERE 1=1
    '''
    params = []
    
    if reporter:
        query += ' AND reporter = ?'
        params.append(reporter)
    
    if client:
        query += ' AND client_name LIKE ?'
        params.append(f'%{client}%')
    
    if product:
        query += ' AND product_name LIKE ?'
        params.append(f'%{product}%')
    
    if date_from:
        query += ' AND report_date >= ?'
        params.append(date_from)
    
    if date_to:
        query += ' AND report_date <= ?'
        params.append(date_to)
    
    if search:
        query += ' AND (content LIKE ? OR client_name LIKE ? OR client_person LIKE ? OR product_name LIKE ?)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])
    
    # メールごとにグループ化して日付の新しい順にソート
    query += ' GROUP BY mail_id ORDER BY report_date DESC LIMIT ? OFFSET ?'
    params.append(per_page)
    params.append((page - 1) * per_page)
    
    # 総メール数を取得（フィルタ適用）
    count_query = '''
        SELECT COUNT(DISTINCT mail_id) as total
        FROM weekly_reports
        WHERE 1=1
    '''
    count_params = []
    
    if reporter:
        count_query += ' AND reporter = ?'
        count_params.append(reporter)
    
    if client:
        count_query += ' AND client_name LIKE ?'
        count_params.append(f'%{client}%')
    
    if product:
        count_query += ' AND product_name LIKE ?'
        count_params.append(f'%{product}%')
    
    if date_from:
        count_query += ' AND report_date >= ?'
        count_params.append(date_from)
    
    if date_to:
        count_query += ' AND report_date <= ?'
        count_params.append(date_to)
    
    if search:
        count_query += ' AND (content LIKE ? OR client_name LIKE ? OR client_person LIKE ? OR product_name LIKE ?)'
        count_params.extend([f'%{search}%', f'%{search}%', f'%{search}%', f'%{search}%'])
    
    # データ取得
    conn = get_db()
    
    # 総件数取得
    total_count = conn.execute(count_query, count_params).fetchone()['total']
    
    # レポート取得
    cursor = conn.execute(query, params)
    reports = []
    for row in cursor:
        reports.append({
            'mail_id': row['mail_id'],
            'report_date': row['report_date'],
            'reporter': row['reporter'],
            'report_count': row['report_count'],
            'clients': row['clients'],
            'products': row['products'],
            'all_content': row['all_content']
        })
    conn.close()
    
    return jsonify({
        'reports': reports,
        'total_count': total_count,
        'page': page,
        'per_page': per_page,
        'has_more': total_count > page * per_page
    })

@app.route('/api/mail_detail/<mail_id>')
def get_mail_detail(mail_id):
    """メールの詳細情報を取得"""
    conn = get_db()
    cursor = conn.execute('''
        SELECT id, mail_id, report_date, reporter, client_name, 
               client_department, client_person, employee_name, product_name, content
        FROM weekly_reports
        WHERE mail_id = ?
        ORDER BY id
    ''', (mail_id,))
    
    reports = []
    for row in cursor:
        reports.append({
            'id': row['id'],
            'mail_id': row['mail_id'],
            'report_date': row['report_date'],
            'reporter': row['reporter'],
            'client_name': row['client_name'],
            'client_department': row['client_department'],
            'client_person': row['client_person'],
            'employee_name': row['employee_name'],
            'product_name': row['product_name'],
            'content': row['content']
        })
    conn.close()
    return jsonify(reports)

@app.route('/api/reporters')
def get_reporters():
    """報告者リストを取得"""
    conn = get_db()
    cursor = conn.execute('SELECT DISTINCT reporter FROM weekly_reports ORDER BY reporter')
    reporters = [row['reporter'] for row in cursor]
    conn.close()
    return jsonify(reporters)

@app.route('/api/clients')
def get_clients():
    """客先リストを取得（カンマ区切りを分離）"""
    conn = get_db()
    cursor = conn.execute('SELECT DISTINCT client_name FROM weekly_reports WHERE client_name IS NOT NULL AND client_name != ""')
    
    # カンマ（,）と日本語読点（、）で区切りの客先名を個別に分離
    clients_set = set()
    for row in cursor:
        if row['client_name']:
            # カンマと日本語読点で分割して個別の客先名を取得
            import re
            clients = re.split(r'[,、]', row['client_name'])
            for client in clients:
                client = client.strip()  # 前後の空白を削除
                if client:  # 空文字列でない場合のみ追加
                    clients_set.add(client)
    
    # リストに変換してソート
    clients = sorted(list(clients_set))
    conn.close()
    return jsonify(clients)

@app.route('/api/products')
def get_products():
    """製品リストを取得（カンマ区切りを分離）"""
    conn = get_db()
    cursor = conn.execute('SELECT DISTINCT product_name FROM weekly_reports WHERE product_name IS NOT NULL AND product_name != ""')
    
    # カンマ（,）と日本語読点（、）で区切りの製品名を個別に分離
    products_set = set()
    for row in cursor:
        if row['product_name']:
            # カンマと日本語読点で分割して個別の製品名を取得
            import re
            products = re.split(r'[,、]', row['product_name'])
            for product in products:
                product = product.strip()  # 前後の空白を削除
                if product:  # 空文字列でない場合のみ追加
                    products_set.add(product)
    
    # リストに変換してソート
    products = sorted(list(products_set))
    conn.close()
    return jsonify(products)

@app.route('/api/client_projects/<client>')
def get_client_projects(client):
    """特定客先の案件一覧を取得"""
    conn = get_db()
    cursor = conn.execute('''
        SELECT id, mail_id, report_date, reporter, client_name, 
               client_department, client_person, employee_name, product_name, content
        FROM weekly_reports
        WHERE client_name LIKE ?
        ORDER BY report_date DESC, id DESC
    ''', (f'%{client}%',))
    
    projects = []
    for row in cursor:
        projects.append({
            'id': row['id'],
            'mail_id': row['mail_id'],
            'report_date': row['report_date'],
            'reporter': row['reporter'],
            'client_name': row['client_name'],
            'client_department': row['client_department'],
            'client_person': row['client_person'],
            'employee_name': row['employee_name'],
            'product_name': row['product_name'],
            'content': row['content']
        })
    
    conn.close()
    return jsonify(projects)

@app.route('/api/product_projects/<product>')
def get_product_projects(product):
    """特定製品の案件一覧を取得"""
    conn = get_db()
    cursor = conn.execute('''
        SELECT id, mail_id, report_date, reporter, client_name, 
               client_department, client_person, employee_name, product_name, content
        FROM weekly_reports
        WHERE product_name LIKE ?
        ORDER BY report_date DESC, id DESC
    ''', (f'%{product}%',))
    
    projects = []
    for row in cursor:
        projects.append({
            'id': row['id'],
            'mail_id': row['mail_id'],
            'report_date': row['report_date'],
            'reporter': row['reporter'],
            'client_name': row['client_name'],
            'client_department': row['client_department'],
            'client_person': row['client_person'],
            'employee_name': row['employee_name'],
            'product_name': row['product_name'],
            'content': row['content']
        })
    
    conn.close()
    return jsonify(projects)

@app.route('/api/stats')
def get_stats():
    """統計情報を取得"""
    conn = get_db()
    
    # 総件数
    total = conn.execute('SELECT COUNT(*) as cnt FROM weekly_reports').fetchone()['cnt']
    
    # 報告者別件数
    reporter_stats = []
    cursor = conn.execute('''
        SELECT reporter, COUNT(*) as cnt 
        FROM weekly_reports 
        GROUP BY reporter 
        ORDER BY cnt DESC
    ''')
    for row in cursor:
        reporter_stats.append({
            'reporter': row['reporter'],
            'count': row['cnt']
        })
    
    # 客先別件数
    client_stats = []
    cursor = conn.execute('''
        SELECT client_name, COUNT(*) as cnt 
        FROM weekly_reports 
        WHERE client_name IS NOT NULL AND client_name != ''
        GROUP BY client_name 
        ORDER BY cnt DESC
        LIMIT 10
    ''')
    for row in cursor:
        client_stats.append({
            'client': row['client_name'],
            'count': row['cnt']
        })
    
    # 月別件数（最近6ヶ月）
    monthly_stats = []
    cursor = conn.execute('''
        SELECT strftime('%Y-%m', report_date) as month, COUNT(*) as cnt
        FROM weekly_reports
        WHERE report_date IS NOT NULL
        GROUP BY month
        ORDER BY month DESC
        LIMIT 6
    ''')
    for row in cursor:
        monthly_stats.append({
            'month': row['month'],
            'count': row['cnt']
        })
    
    conn.close()
    
    return jsonify({
        'total': total,
        'by_reporter': reporter_stats,
        'by_client': client_stats,
        'by_month': list(reversed(monthly_stats))
    })

@app.route('/api/project/<int:project_id>')
def get_project(project_id):
    """個別プロジェクトデータを取得"""
    conn = get_db()
    cursor = conn.execute('''
        SELECT id, mail_id, report_date, reporter, client_name, 
               client_department, client_person, employee_name, product_name, content
        FROM weekly_reports
        WHERE id = ?
    ''', (project_id,))
    
    project = cursor.fetchone()
    conn.close()
    
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    return jsonify({
        'id': project['id'],
        'mail_id': project['mail_id'],
        'report_date': project['report_date'],
        'reporter': project['reporter'],
        'client_name': project['client_name'],
        'client_department': project['client_department'],
        'client_person': project['client_person'],
        'employee_name': project['employee_name'],
        'product_name': project['product_name'],
        'content': project['content']
    })

@app.route('/api/project/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """プロジェクトデータを更新"""
    data = request.json
    
    conn = get_db()
    cursor = conn.execute('''
        UPDATE weekly_reports 
        SET report_date = ?, reporter = ?, client_name = ?, 
            client_department = ?, client_person = ?, employee_name = ?, 
            product_name = ?, content = ?
        WHERE id = ?
    ''', (
        data.get('report_date'),
        data.get('reporter'),
        data.get('client_name'),
        data.get('client_department'),
        data.get('client_person'),
        data.get('employee_name'),
        data.get('product_name'),
        data.get('content'),
        project_id
    ))
    
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'error': 'Project not found'}), 404
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/delete_mail_projects/<mail_id>', methods=['DELETE'])
def delete_mail_projects(mail_id):
    """指定されたメールIDの全案件を削除"""
    conn = get_db()
    cursor = conn.execute('DELETE FROM weekly_reports WHERE mail_id = ?', (mail_id,))
    
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'deleted_count': deleted_count
    })

# プロセス管理用のグローバル変数
running_processes = {}

@app.route('/api/start_process_reports', methods=['POST'])
def start_process_reports():
    """週報処理スクリプトを非同期で開始"""
    try:
        import subprocess
        import os
        import threading
        import uuid
        import tempfile
        
        # プロセスIDを生成
        process_id = str(uuid.uuid4())
        
        # 一時ログファイルを作成
        log_file = tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.log')
        log_file_path = log_file.name
        log_file.close()
        
        # スクリプトのパスを取得
        script_path = os.path.join(os.path.dirname(__file__), 'weekly_report_processor.py')
        
        # プロセス情報を保存
        running_processes[process_id] = {
            'log_file': log_file_path,
            'is_complete': False,
            'success': False,
            'new_reports': 0,
            'total_reports': 0,
            'process': None
        }
        
        # バックグラウンドでスクリプトを実行する関数
        def run_process():
            try:
                # 初期ログを書き込み
                with open(log_file_path, 'w', encoding='utf-8', errors='replace') as log_f:
                    log_f.write("週報処理を開始します...\n")
                
                # 環境変数でUTF-8を強制
                env = os.environ.copy()
                env['PYTHONIOENCODING'] = 'utf-8'
                
                # Pythonスクリプトを実行（stdout/stderrをPIPEで取得）
                process = subprocess.Popen(
                    ['python', script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    cwd=os.path.dirname(__file__),
                    bufsize=1,
                    universal_newlines=True,
                    encoding='utf-8',
                    errors='replace',
                    env=env
                )
                
                running_processes[process_id]['process'] = process
                
                # プロセス開始をログに記録
                with open(log_file_path, 'a', encoding='utf-8', errors='replace') as log_f:
                    log_f.write(f"プロセス開始 (PID: {process.pid})\n")
                
                # 出力をリアルタイムで読み取ってファイルに書き込み
                with open(log_file_path, 'a', encoding='utf-8', errors='replace') as log_f:
                    for line in iter(process.stdout.readline, ''):
                        log_f.write(line)
                        log_f.flush()
                    
                # プロセスの完了を待機
                return_code = process.wait()
                
                # プロセス完了をログに記録
                with open(log_file_path, 'a', encoding='utf-8', errors='replace') as log_f:
                    log_f.write(f"プロセス完了 (終了コード: {return_code})\n")
                
                # ログファイルから結果を解析
                with open(log_file_path, 'r', encoding='utf-8', errors='replace') as read_log:
                    output = read_log.read()
                    
                    new_reports = 0
                    total_reports = 0
                    
                    # 出力から件数情報を抽出
                    for line in output.split('\n'):
                        if 'をDBに登録しました' in line:
                            new_reports += 1
                        elif '件のメールを処理しました' in line:
                            import re
                            match = re.search(r'(\d+)件のメールを処理しました', line)
                            if match:
                                total_reports = int(match.group(1))
                    
                    # 結果を更新
                    running_processes[process_id].update({
                        'is_complete': True,
                        'success': return_code == 0,
                        'new_reports': new_reports,
                        'total_reports': total_reports
                    })
                    
            except Exception as e:
                # エラーをログファイルに書き込み
                with open(log_file_path, 'a', encoding='utf-8', errors='replace') as log_f:
                    log_f.write(f'\n[ERROR] {str(e)}\n')
                
                running_processes[process_id].update({
                    'is_complete': True,
                    'success': False
                })
        
        # バックグラウンドスレッドで実行
        thread = threading.Thread(target=run_process)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'process_id': process_id
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/process_status/<process_id>')
def get_process_status(process_id):
    """プロセスの状態とログを取得"""
    try:
        if process_id not in running_processes:
            return jsonify({'error': 'Process not found'}), 404
        
        process_info = running_processes[process_id]
        offset = int(request.args.get('offset', 0))
        
        # ログファイルから新しい出力を読み取り
        new_output = ""
        current_offset = offset
        
        try:
            with open(process_info['log_file'], 'r', encoding='utf-8', errors='replace') as f:
                f.seek(offset)
                new_output = f.read()
                current_offset = f.tell()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            new_output = f"[エラー] ログファイルの読み取りに失敗: {str(e)}"
        
        return jsonify({
            'is_complete': process_info['is_complete'],
            'success': process_info['success'],
            'new_reports': process_info['new_reports'],
            'total_reports': process_info['total_reports'],
            'new_output': new_output,
            'current_offset': current_offset
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500


@app.route('/health')
def health():
    """ヘルスチェックエンドポイント（AWS用）"""
    return jsonify({'status': 'healthy'})

# エラーハンドラー
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_db()
    # 開発環境用設定
    app.run(debug=True, host='0.0.0.0', port=5000)