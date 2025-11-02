from flask import Flask, render_template, jsonify, request
import sqlite3
import json
from datetime import datetime

app = Flask(__name__)

# データベースファイルのパス
DB_PATH = 'XBRL_DB_v02.db'


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/companies')
def get_companies():
    """全社名リストを取得"""
    conn = get_db_connection()
    companies = conn.execute('''
        SELECT DISTINCT CompanyName, Code 
        FROM XbrlDB 
        WHERE Code IS NOT NULL
        ORDER BY CompanyName
    ''').fetchall()
    conn.close()

    return jsonify([{
        'name': company['CompanyName'],
        'code': company['Code']
    } for company in companies])


@app.route('/api/company/<code>')
def get_company_by_code(code):
    """証券コードで会社を検索"""
    conn = get_db_connection()

    # 数値型と文字列型の両方で検索
    try:
        code_int = int(code) if code.isdigit() else None
    except:
        code_int = None

    company = conn.execute('''
        SELECT DISTINCT CompanyName, Code 
        FROM XbrlDB 
        WHERE Code = ? OR Code = ?
        LIMIT 1
    ''', (code, code_int)).fetchone()
    conn.close()

    if company:
        return jsonify({
            'name': company['CompanyName'],
            'code': company['Code']
        })
    else:
        return jsonify({'error': 'Company not found'}), 404


@app.route('/api/sales/<company_name>')
def get_sales_data(company_name):
    """特定の会社の売上データを取得"""
    conn = get_db_connection()
    sales_data = conn.execute('''
        SELECT Announcement_date, Sales, Quarter 
        FROM XbrlDB 
        WHERE CompanyName = ?
        ORDER BY Announcement_date
    ''', (company_name,)).fetchall()
    conn.close()

    return jsonify([{
        'date': row['Announcement_date'],
        'sales': row['Sales'],
        'quarter': row['Quarter']
    } for row in sales_data])


if __name__ == '__main__':
    app.run(debug=True)