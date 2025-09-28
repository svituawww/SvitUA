#!/usr/bin/env python3
"""
DB Manager - Complete Implementation

"""

import sqlite3



class DP_DB_Manager:
    def __init__(self, db_path: str = "../sqllite/dp_db.db"):
        self.db_path = db_path        
        self.init_db()
    
    def init_db(self):
        """Initialize database with enhanced schema including hash-based identification."""
        with sqlite3.connect(self.db_path) as conn:
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshot_ref (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_work VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
                )
            """)

            # conn.execute("""
            #     CREATE TABLE IF NOT EXISTS files_for_snapshot (
            #         id INTEGER PRIMARY KEY AUTOINCREMENT,
            #         file_path VARCHAR(255) NOT NULL,
            #         file_name VARCHAR(255) NOT NULL,
            #         created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP                    
            #     )
            # """)
            
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS snapshots_files (
                    id_record INTEGER NOT NULL,
                    id_snapshot_ref INTEGER NOT NULL,
                    file_path VARCHAR(255) NOT NULL,
                    file_name VARCHAR(255) NOT NULL,
                    file_size INTEGER NOT NULL,
                    file_hash VARCHAR(255) NOT NULL,
                    dir_or_file VARCHAR(4) NOT NULL,
                    UNIQUE(id_snapshot_ref, id_record),                    
                    FOREIGN KEY (id_snapshot_ref) REFERENCES snapshot_ref(id)
                )
            """)


            conn.execute("""

                CREATE TABLE IF NOT EXISTS settings_for_print_deb (                    
                    id_function INTEGER PRIMARY KEY AUTOINCREMENT,
                    function_name VARCHAR(255) NOT NULL,
                    function_description VARCHAR(255) NOT NULL,                    
                    print_value INTEGER NOT NULL,
                    UNIQUE(id_function)
                )
            """)

            # Create indexes for better performance
            conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_files_id_snapshot_ref ON snapshots_files(id_snapshot_ref, id_record)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_snapshots_files_file_path ON snapshots_files(file_hash)")
    

    def add_file_to_db(self, full_path: str, file_name: str, sha256: str, file_size: int, id_snapshot_ref: int, id_record: int, dir_or_file: str):
        """Add a file to the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("INSERT INTO snapshots_files (id_snapshot_ref, id_record, file_path, file_name, file_hash, file_size, dir_or_file) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                            (id_snapshot_ref, id_record, full_path, file_name, sha256, file_size, dir_or_file))
                conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Database Integrity Error for file {full_path}: {e}")
            raise
        except sqlite3.Error as e:
            print(f"Database Error for file {full_path}: {e}")
            raise

    def get_file_by_hash(self, sha256: str):
        """Get a file by its hash."""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT * FROM snapshots_files WHERE file_hash = ?", (sha256,)).fetchone()

    def add_snapshot_ref(self, id_work: str):
        """Add a snapshot reference to the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("INSERT INTO snapshot_ref (id_work) VALUES (?)", (id_work,))
            conn.commit()
            # id_snapshot_ref is the id of the snapshot reference
            return cursor.lastrowid

    def get_snapshot_ref(self, id_work: str):
        """Get a snapshot reference by its id."""
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute("SELECT * FROM snapshot_ref WHERE id_work = ?", (id_work,)).fetchone()


    def get_deploy_list(self, prev_snapshot_id: int):
        """Get a list of all deploy records."""
        sql1 = f"""
            SELECT
            f1.file_path, 
            f1.dir_or_file,
            CASE 
            WHEN f1.end_fp = f1.beg_fp THEN 'Replace'
            WHEN f1.end_fp = 'Delete' THEN 'Delete'
            WHEN f1.beg_fp = 'New' THEN 'New'
            ELSE 'Unknown'
            END as file_action
            from
            (
            SELECT
            count(o1.file_path) as count_ids, o1.file_path as file_path, o1.dir_or_file as dir_or_file, coalesce(se.file_path,'Delete') as end_fp , coalesce(sb.file_path,'New') as beg_fp
            from
            (
            SELECT
            count(ids) as count_ids, file_path, file_name, file_hash, dir_or_file
            from
            (
            SELECT
            1 as ids, sf.file_path, sf.file_name, sf.file_hash, sf.dir_or_file
            FROM
            snapshots_files sf
            WHERE
            sf.id_snapshot_ref = {prev_snapshot_id}

            union ALL

            SELECT
            2 as ids, sf.file_path, sf.file_name, sf.file_hash, sf.dir_or_file
            FROM
            snapshots_files sf
            WHERE
            sf.id_snapshot_ref = (select max(id) from snapshot_ref)

            )
            group by 2,3,4
            )o1

            left join (
            SELECT
            sf.file_path, sf.file_hash, sf.id_snapshot_ref
            FROM
            snapshots_files sf
            WHERE
            sf.id_snapshot_ref = (select max(id) from snapshot_ref)

            )se on se.file_path = o1.file_path

            left join (
            SELECT
            sf.file_path, sf.file_name, sf.file_hash, sf.id_snapshot_ref
            FROM
            snapshots_files sf
            WHERE
            sf.id_snapshot_ref = {prev_snapshot_id}

            )sb on sb.file_path = o1.file_path

            where
            o1.count_ids <> 2
            group by 2,3,4,5
            )f1
        """
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(sql1).fetchall()
    
    def store_in_db_settings_for_print_deb(self, function_name: str, function_description: str, print_value: int):
        """Store settings for print_deb in the database."""
        with sqlite3.connect(self.db_path) as conn:
            # Check if record already exists
            existing_record = self.get_id_function_for_print_deb(function_name)
            if not existing_record:
                conn.execute("INSERT INTO settings_for_print_deb (function_name, function_description, print_value) VALUES (?, ?, ?)", (function_name, function_description, print_value))            
            conn.commit()
    

    def get_id_function_for_print_deb(self, function_name: str):
        """Get id_function for print_deb from the database."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("SELECT id_function FROM settings_for_print_deb WHERE function_name = ?", (function_name,)).fetchone()
            return result[0] if result else None

    def get_settings_for_print_deb_by_id(self, id_function: int):
        """Get settings for print_deb from the database."""
        with sqlite3.connect(self.db_path) as conn:
            result = conn.execute("SELECT print_value FROM settings_for_print_deb WHERE id_function = ?", (id_function,)).fetchone()
            return result[0] if result else 0




