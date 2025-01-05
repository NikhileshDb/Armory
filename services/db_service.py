import sqlite3
import json
import os


def get_db_connection():

    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    db_path = os.path.join(data_dir, 'tiny.db')

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Allows column access by name

    return conn


def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        path TEXT NOT NULL,
        upload_date REAL NOT NULL,
        is_deleted INTEGER        
    );                     
    ''')

    cursor.execute('''            
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        added_date REAL,
        is_active BOOLEAN NOT NULL
    ); 
    ''')

    cursor.execute('''            
    CREATE TABLE IF NOT EXISTS category_attributes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_id INTEGER NOT NULL,
        data TEXT NOT NULL 
    ); 
    ''')

    cursor.execute('''            
    CREATE TABLE IF NOT EXISTS assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT NOT NULL,
        added_date REAL,
        category_id INTEGER NOT NULL,  
        is_active BOOLEAN NOT NULL      
    ); 
    ''')

    conn.commit()
    conn.close()


def get_all_samples():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM samples')

    samples = cursor.fetchall()

    conn.close()
    return samples


def get_sample(sample_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM samples WHERE id = ?', (sample_id,))
    sample = cursor.fetchone()

    conn.close()
    return sample


def insert_sample(name, path, upload_date, is_deleted=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO samples (name, path, upload_date, is_deleted)
    VALUES (?, ?, ?, ?)
    ''', (name, path, upload_date, is_deleted))

    conn.commit()
    conn.close()


def get_all_assets():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM assets')

    assets = cursor.fetchall()

    conn.close()
    return assets


def insert_asset(name, description, added_date, category_id, is_active=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO assets (name, description, added_date, category_id, is_active)
    VALUES (?, ?, ?, ?, ?)
    ''', (name, description, added_date, category_id, is_active))

    conn.commit()
    conn.close()


def get_all_categories():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('SELECT * FROM categories')

    categories = cursor.fetchall()

    conn.close()
    return categories


def insert_category(name, description, added_date, is_active=False):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute('''
    INSERT INTO categories (name, description, added_date, is_active)
    VALUES (?, ?, ?, ?)
    ''', (name, description, added_date, is_active))

    conn.commit()
    conn.close()


def get_category_attribute_data_by_name(category_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT ca.data FROM categories c join category_attributes ca on c.id = ca.category_id WHERE c.name = ?', (category_name,))
    sample = cursor.fetchone()

    conn.close()

    if sample:
        return sample['data']
    else:
        return None


def get_category_attributes(category_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM category_attributes WHERE category_id = ?', (category_id,))
    sample = cursor.fetchone()

    conn.close()
    return sample


def insert_category_attributes(categoryId, data):
    conn = get_db_connection()
    cursor = conn.cursor()

    data_json = json.dumps(data)

    cursor.execute('''
    INSERT INTO category_attributes (category_id, data)
    VALUES (?, ?)
    ''', (categoryId, data_json))

    conn.commit()
    conn.close()
