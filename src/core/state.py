
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

    def complete_plan(self, plan_id: int):
        """
        Mark a plan as completed.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("UPDATE plans SET status = 'completed' WHERE id = ?", (plan_id,))
        conn.commit()
        conn.close()
