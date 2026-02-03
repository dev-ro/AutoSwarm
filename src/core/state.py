
import sqlite3
import json
import os
from typing import Optional, List, Dict
from datetime import datetime
from src.agents.schemas import Plan, Task

DB_PATH = "autoswarm.db"

class StateManager:
    """
    Manages the persistent state of the AutoSwarm using SQLite.
    Stores plans and tasks to allow resumption after crashes.
    """
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the database schema."""
        conn = sqlite3.connect(self.db_path)
        # Enable Foreign Keys
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        
        # Table for Plans
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                goal TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'active'  -- active, completed, failed
            )
        ''')

        # Table for Tasks
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER,
                step_index INTEGER,
                description TEXT,
                assigned_agent TEXT,
                status TEXT DEFAULT 'pending', -- pending, in_progress, completed, failed
                result TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(plan_id) REFERENCES plans(id)
            )
        ''')
        
        # Table for Task Artifacts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS task_artifacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                artifact_type TEXT,
                content TEXT,
                source_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(task_id) REFERENCES tasks(id)
            )
        ''')

        # Table for Social Personas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_personas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                handle TEXT NOT NULL,
                platform TEXT NOT NULL,
                description TEXT,
                tags TEXT, -- JSON list of strings
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Table for Social Posts
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS social_posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER NOT NULL,
                assigned_persona_id INTEGER,
                content TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT DEFAULT 'draft', -- draft, approved, published, failed
                metrics TEXT, -- JSON dict
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                published_at TIMESTAMP,
                FOREIGN KEY(task_id) REFERENCES tasks(id),
                FOREIGN KEY(assigned_persona_id) REFERENCES social_personas(id)
            )
        ''')
        
        conn.commit()
        conn.close()

    def create_plan(self, plan: Plan) -> int:
        """
        Saves a new plan and its tasks to the DB.
        Returns the plan_id.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # 1. Insert Plan
            cursor.execute("INSERT INTO plans (goal) VALUES (?)", (plan.goal,))
            plan_id = cursor.lastrowid
            
            # 2. Insert Tasks
            for i, task in enumerate(plan.steps, 1):
                cursor.execute('''
                    INSERT INTO tasks (plan_id, step_index, description, assigned_agent, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (plan_id, i, task.description, task.assigned_agent, 'pending'))
            
            conn.commit()
            print(f"[State] Plan saved with ID: {plan_id}")
            return plan_id
        except Exception as e:
            print(f"[State] Error creating plan: {e}")
            conn.rollback()
            return -1
        finally:
            conn.close()

    def get_active_plan(self) -> Optional[Dict]:
        """
        Checks for an active plan. Returns a dict with plan info and tasks if found, else None.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM plans WHERE status = 'active' ORDER BY id DESC LIMIT 1")
        plan_row = cursor.fetchone()
        
        if not plan_row:
            conn.close()
            return None
            
        plan_data = dict(plan_row)
        
        # Get tasks
        cursor.execute("SELECT * FROM tasks WHERE plan_id = ? ORDER BY step_index ASC", (plan_data['id'],))
        tasks_rows = cursor.fetchall()
        
        tasks_data = [dict(row) for row in tasks_rows]
        
        conn.close()
        return {"plan": plan_data, "tasks": tasks_data}

    def get_task_id(self, plan_id: int, step_index: int) -> Optional[int]:
        """
        Retrieves the task_id for a given plan and step index.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM tasks WHERE plan_id = ? AND step_index = ?", (plan_id, step_index))
        row = cursor.fetchone()
        
        conn.close()
        return row[0] if row else None

    def update_task_status(self, plan_id: int, step_index: int, status: str, result: str = None):
        """
        Updates the status of a specific task.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if result:
            cursor.execute('''
                UPDATE tasks 
                SET status = ?, result = ?, updated_at = CURRENT_TIMESTAMP
                WHERE plan_id = ? AND step_index = ?
            ''', (status, result, plan_id, step_index))
        else:
            cursor.execute('''
                UPDATE tasks 
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE plan_id = ? AND step_index = ?
            ''', (status, plan_id, step_index))
            
        conn.commit()
        conn.close()

    def log_artifact(self, task_id: int, artifact_type: str, content: str, source_url: str = None):
        """
        Logs a detailed artifact (search result, citation, etc.) for a task.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO task_artifacts (task_id, artifact_type, content, source_url)
                VALUES (?, ?, ?, ?)
            ''', (task_id, artifact_type, content, source_url))
            conn.commit()
            print(f"[State] Logged artifact '{artifact_type}' for task {task_id}")
        except Exception as e:
            print(f"[State] Error logging artifact: {e}")
        finally:
            conn.close()

    def get_artifact_count(self, task_id: int) -> int:
        """Counts artifacts for a specific task."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM task_artifacts WHERE task_id = ?", (task_id,))
        count = cursor.fetchone()[0]
        conn.close()
        return count

    def complete_plan(self, plan_id: int):
        """
        Mark a plan as completed.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE plans SET status = 'completed' WHERE id = ?", (plan_id,))
        conn.commit()
        conn.close()

    # --- Social Media Extensions ---

    def create_persona(self, name: str, handle: str, platform: str, description: str, tags: List[str]) -> int:
        """Creates a new social persona."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO social_personas (name, handle, platform, description, tags)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, handle, platform, description, json.dumps(tags)))
            persona_id = cursor.lastrowid
            conn.commit()
            print(f"[State] Created persona '{name}' with ID: {persona_id}")
            return persona_id
        except Exception as e:
            print(f"[State] Error creating persona: {e}")
            return -1
        finally:
            conn.close()

    def get_persona_by_tag(self, tag: str) -> Optional[Dict]:
        """
        Finds a persona that has the specified tag.
        Returns the first match found.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM social_personas")
        rows = cursor.fetchall()
        
        for row in rows:
            try:
                tags = json.loads(row['tags']) if row['tags'] else []
                if tag in tags:
                    conn.close()
                    return dict(row)
            except json.JSONDecodeError:
                continue
                
        conn.close()
        return None

    def create_post(self, task_id: int, content: str, platform: str, assigned_persona_id: Optional[int] = None) -> int:
        """
        Creates a new social post tracked against a task.
        """
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON") # Ensure FKs are enforced
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO social_posts (task_id, assigned_persona_id, content, platform, status)
                VALUES (?, ?, ?, ?, 'draft')
            ''', (task_id, assigned_persona_id, content, platform))
            post_id = cursor.lastrowid
            conn.commit()
            print(f"[State] Created post for task {task_id} with ID: {post_id}")
            return post_id
        except sqlite3.IntegrityError as e:
            print(f"[State] Integrity error creating post (likely invalid task_id): {e}")
            return -1
        except Exception as e:
            print(f"[State] Error creating post: {e}")
            return -1
        finally:
            conn.close()

    def update_post_status(self, post_id: int, status: str, metrics: Optional[Dict] = None):
        """Updates the status and metrics of a post."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            if metrics:
                cursor.execute('''
                    UPDATE social_posts 
                    SET status = ?, metrics = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, json.dumps(metrics), post_id))
            else:
                cursor.execute('''
                    UPDATE social_posts 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (status, post_id))
            conn.commit()
        except Exception as e:
            print(f"[State] Error updating post {post_id}: {e}")
        finally:
            conn.close()

