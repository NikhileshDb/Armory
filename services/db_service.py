import logging
import sqlite3
import json
import os
from .helper_log import logger


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

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL,
        class_name TEXT NOT NULL,
        attributes TEXT,
        confidence REAL NOT NULL,
        bbox TEXT NOT NULL,
        annotated_image TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()


def get_all_samples():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT * FROM samples')

        # Fetch column names and rows
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()

        # Convert rows to a list of dictionaries
        samples = [dict(zip(columns, row)) for row in rows]

        # Serialize to JSON
        # Use `default=str` for datetime and other non-serializable objects
        formatted_data = json.dumps(samples, default=str)
        logging.info(formatted_data)
        return formatted_data
    except Exception as e:
        print(f"An error occurred: {e}")
        return json.dumps({'error': 'Unable to fetch samples'})
    finally:
        if conn:
            conn.close()


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


def get_sample_details_by_name(image_name):
    conn = get_db_connection()
    cursor = conn.cursor()

    try:

        query = """
            SELECT name, path, upload_date, is_deleted
            FROM samples
            WHERE name = ?;
        """
        cursor.execute(query, (image_name,))
        result = cursor.fetchone()

        if result:
            return {
                "name": result[0],
                "path": result[1],
                "upload_date": result[2],
                # Convert is_deleted to a boolean
                "is_deleted": bool(result[3])
            }
        else:
            return {"error": "Image not found"}

    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}

    finally:
        conn.close()


def save_prediction_to_db(prediction, annotated_image):
    try:
        # Establish database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Execute the insert query
        cursor.execute('''
            INSERT INTO predictions (class_id, class_name, attributes, confidence, bbox, annotated_image)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            prediction[0]['class_id'],
            prediction[0]['class_name'],
            # Serialize attributes to JSON (ensure attributes is serializable)
            prediction[0]['attributes'],
            prediction[0]['confidence'],
            json.dumps(prediction[0]['bbox']),  # Serialize bbox to JSON
            annotated_image
        ))

        # INFO: root: Prediction: [{'class_id': 2, 'class_name': 'car', 'attributes': None, 'confidence': 0.3884711265563965, 'bbox': [[0.0, 428.875244140625, 715.8741455078125, 850.5654296875]]}]
        # data = {
        #     'class_id': prediction[0]['class_id'],
        #     'class_name': prediction[0]['class_name'],
        #     'attributes': prediction[0]['attributes'],
        #     'confidence': prediction[0]['confidence'],
        #     'bbox': prediction[0]['bbox'],
        #     'annotated_image': annotated_image
        # }

        # Commit changes and close connection

        # logger.critical(data)
        conn.commit()
        logger.info(f"Prediction saved to database: {
                    prediction[0]['class_name']} - {prediction[0]['confidence']}")

    except Exception as e:
        # Log any database-related errors
        logger.error(f"Database error while saving prediction: {e}")
    except Exception as e:
        # Log any other exceptions
        logger.error(f"Error occurred while saving prediction: {e}")
    finally:
        # Ensure the database connection is closed
        if conn:
            conn.close()
            logger.info("Database connection closed.")


def get_all_predictions():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all predictions from the database
    cursor.execute("SELECT * FROM predictions")
    rows = cursor.fetchall()

    # Format the results into a JSON-serializable list
    predictions = []
    for row in rows:
        predictions.append({
            "id": row[0],
            "class_id": row[1],
            "class_name": row[2],
            # Deserialize JSON if present
            "attributes": json.loads(row[3]) if row[3] else None,
            "confidence": row[4],
            "bbox": json.loads(row[5]),  # Deserialize JSON bounding box
            # Base64 string is already JSON-serializable
            "annotated_image": row[6]
        })

    conn.close()
    return predictions


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
