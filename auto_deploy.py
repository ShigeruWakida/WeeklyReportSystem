#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
週報処理からデプロイ用ZIP作成までを自動化するスクリプト

使い方:
    python auto_deploy.py

実行内容:
    1. weekly_report_processor.pyを実行してメール処理
    2. エラーチェック
    3. weekly_reports.dbをwith_db_deploy/にコピー
    4. with_db_deploy/の内容をZIPにパッケージング
"""

import subprocess
import sys
import os
import shutil
import zipfile
from pathlib import Path
from datetime import datetime


def print_section(title):
    """セクションタイトルを表示"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def run_weekly_report_processor():
    """週報処理スクリプトを実行"""
    print_section("ステップ 1: 週報メール処理")

    print("週報処理を開始します...")
    print("python weekly_report_processor.py を実行中...\n")

    try:
        result = subprocess.run(
            [sys.executable, "weekly_report_processor.py"],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        # 出力を表示
        print(result.stdout)

        if result.stderr:
            print("警告/エラー出力:")
            print(result.stderr)

        # エラーチェック
        if result.returncode != 0:
            print(f"\n[エラー] 週報処理が失敗しました (終了コード: {result.returncode})")
            return False

        # 「処理完了」メッセージの確認
        if "処理完了" not in result.stdout:
            print("\n[警告] 処理完了メッセージが見つかりません")
            response = input("続行しますか？ (y/n): ")
            if response.lower() != 'y':
                return False

        print("\n[OK] 週報処理が正常に完了しました")
        return True

    except Exception as e:
        print(f"\n[エラー] 週報処理の実行中に例外が発生しました: {e}")
        return False


def copy_database():
    """データベースファイルをデプロイディレクトリにコピー"""
    print_section("ステップ 2: データベースファイルのコピー")

    src_db = "weekly_reports.db"
    dest_dir = "with_db_deploy"
    dest_db = os.path.join(dest_dir, "weekly_reports.db")

    # ソースファイルの存在確認
    if not os.path.exists(src_db):
        print(f"[エラー] {src_db} が見つかりません")
        return False

    # デプロイディレクトリの存在確認
    if not os.path.exists(dest_dir):
        print(f"[エラー] {dest_dir} ディレクトリが見つかりません")
        return False

    # ファイルサイズ確認
    src_size = os.path.getsize(src_db) / 1024 / 1024
    print(f"コピー元: {src_db} ({src_size:.2f} MB)")

    # バックアップ作成（既存ファイルがある場合）
    if os.path.exists(dest_db):
        backup_name = f"weekly_reports.db.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        backup_path = os.path.join(dest_dir, backup_name)
        shutil.copy2(dest_db, backup_path)
        print(f"既存ファイルをバックアップ: {backup_name}")

    # コピー実行
    try:
        shutil.copy2(src_db, dest_db)
        dest_size = os.path.getsize(dest_db) / 1024 / 1024
        print(f"コピー先: {dest_db} ({dest_size:.2f} MB)")
        print("\n[OK] データベースファイルのコピーが完了しました")
        return True
    except Exception as e:
        print(f"\n[エラー] コピー中に例外が発生しました: {e}")
        return False


def create_deployment_zip():
    """デプロイ用ZIPファイルを作成"""
    print_section("ステップ 3: デプロイ用ZIPファイル作成")

    deploy_dir = Path("with_db_deploy")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    zip_name = f"weekly_reports_deploy_{timestamp}.zip"

    # ZIPファイル作成
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(deploy_dir):
                for file in files:
                    # バックアップファイルをスキップ
                    if '.backup_' in file:
                        print(f"  スキップ: {file} (バックアップファイル)")
                        continue

                    file_path = Path(root) / file
                    # with_db_deploy/ を除いた相対パスでZIPに追加
                    arcname = str(file_path.relative_to(deploy_dir))
                    zipf.write(file_path, arcname)
                    print(f"  追加: {arcname}")

        # ファイルサイズ確認
        size_mb = os.path.getsize(zip_name) / 1024 / 1024
        print(f"\n[OK] デプロイパッケージ作成完了: {zip_name}")
        print(f"   ファイルサイズ: {size_mb:.2f} MB")
        print(f"\n次のステップ:")
        print(f"   このZIPファイルをAWS Elastic Beanstalkにアップロードしてください")
        return True

    except Exception as e:
        print(f"\n[エラー] ZIP作成中に例外が発生しました: {e}")
        return False


def main():
    """メイン処理"""
    print("\n" + "=" * 60)
    print("  週報処理 & デプロイパッケージ自動作成スクリプト")
    print("=" * 60)
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # ステップ1: 週報処理
    if not run_weekly_report_processor():
        print("\n[エラー] 処理を中断しました")
        return 1

    # ステップ2: データベースコピー
    if not copy_database():
        print("\n[エラー] 処理を中断しました")
        return 1

    # ステップ3: ZIP作成
    if not create_deployment_zip():
        print("\n[エラー] 処理を中断しました")
        return 1

    print_section("すべての処理が完了しました")
    print("[OK] 週報処理からデプロイパッケージ作成まで正常に完了しました\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
