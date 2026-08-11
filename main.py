
from datetime import datetime
import sqlite3
import os

DB_FILE = "clinic.db"


def get_db():
    return sqlite3.connect(DB_FILE)


def create_database():
    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        address TEXT,
        service TEXT,
        amount REAL NOT NULL,
        date TEXT NOT NULL
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT NOT NULL
    )
    """)

    db.commit()
    db.close()


def add_patient(name, age, address, service, amount):
    db = get_db()

    db.execute("""
    INSERT INTO patients
    (name, age, address, service, amount, date)
    VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        address,
        service,
        amount,
        datetime.now().strftime("%Y-%m-%d")
    ))

    db.commit()
    db.close()


def add_expense(description, amount):
    db = get_db()

    db.execute("""
    INSERT INTO expenses
    (description, amount, date)
    VALUES (?, ?, ?)
    """, (
        description,
        amount,
        datetime.now().strftime("%Y-%m-%d")
    ))

    db.commit()
    db.close()


def get_today_finance():
    today = datetime.now().strftime("%Y-%m-%d")

    db = get_db()

    revenue = db.execute("""
    SELECT COALESCE(SUM(amount), 0)
    FROM patients
    WHERE date = ?
    """, (today,)).fetchone()[0]

    expenses = db.execute("""
    SELECT COALESCE(SUM(amount), 0)
    FROM expenses
    WHERE date = ?
    """, (today,)).fetchone()[0]

    patients = db.execute("""
    SELECT COUNT(*)
    FROM patients
    WHERE date = ?
    """, (today,)).fetchone()[0]

    db.close()

    return revenue, expenses, revenue - expenses, patients


create_database()

print("Clinic application core is ready.")
