import pytest
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
import sqlite3
from werkzeug.security import generate_password_hash


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )''')
    c.execute('''CREATE TABLE tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        task TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'admin')",
              ('admin', generate_password_hash('password')))
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'user')",
              ('user', generate_password_hash('password')))
    conn.commit()
    conn.close()

    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret'
    with app.test_client() as client:
        yield client

def test_index(client):
    r = client.get('/')
    assert r.status_code == 200

def test_login_exitoso(client):
    r = client.post('/login', data={'username': 'admin', 'password': 'password'},
                    follow_redirects=True)
    assert r.status_code == 200

def test_login_fallido(client):
    r = client.post('/login', data={'username': 'admin', 'password': 'wrong'})
    assert r.status_code == 401

def test_sql_injection_bloqueada(client):
    r = client.post('/login',
                    data={'username': "admin' OR '1'='1", 'password': "' OR '1'='1"})
    assert r.status_code == 401

def test_dashboard_sin_sesion(client):
    r = client.get('/dashboard', follow_redirects=False)
    assert r.status_code == 302

def test_admin_sin_rol(client):
    client.post('/login', data={'username': 'user', 'password': 'password'})
    r = client.get('/admin', follow_redirects=False)
    assert r.status_code == 302