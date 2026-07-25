import pandas as pd
from tkinter import messagebox
from database import get_connection
from datetime import datetime


def validate_ticket_data(title, description, requester, department, priority):
    errors = []
    if not title or not title.strip():
        errors.append("Title is required.")
    if not description or not description.strip():
        errors.append("Description is required.")
    if not requester or not requester.strip():
        errors.append("Requester name is required.")
    if not department or not department.strip():
        errors.append("Department is required.")
    valid_priorities = ["Low", "Medium", "High", "Critical"]
    if priority not in valid_priorities:
        errors.append(f"Priority must be one of: {', '.join(valid_priorities)}.")
    return errors


def create_ticket(title, description, requester, department, priority="Medium", assignee=""):
    errors = validate_ticket_data(title, description, requester, department, priority)
    if errors:
        messagebox.showwarning("Validation Error", "\n".join(errors))
        return None

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO tickets (title, description, requester, department, priority, assignee)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (title.strip(), description.strip(), requester.strip(), department.strip(), priority, assignee.strip()))
    conn.commit()
    ticket_id = cursor.lastrowid
    conn.close()
    messagebox.showinfo("Success", f"Ticket #{ticket_id} created successfully.")
    return ticket_id


def get_all_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets ORDER BY id DESC")
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tickets


def get_ticket_by_id(ticket_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def search_tickets(query):
    if not query or not query.strip():
        return get_all_tickets()
    conn = get_connection()
    cursor = conn.cursor()
    search_param = f"%{query.strip()}%"
    cursor.execute("""
        SELECT * FROM tickets
        WHERE title LIKE ? OR description LIKE ? OR requester LIKE ?
        OR department LIKE ? OR assignee LIKE ? OR status LIKE ? OR priority LIKE ?
        ORDER BY id DESC
    """, (search_param, search_param, search_param, search_param, search_param, search_param, search_param))
    tickets = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return tickets


def close_ticket(ticket_id):
    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        messagebox.showerror("Error", f"Ticket #{ticket_id} not found.")
        return False
    if ticket["status"] == "Closed":
        messagebox.showwarning("Warning", f"Ticket #{ticket_id} is already closed.")
        return False

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tickets SET status = 'Closed', closed_at = ?, updated_at = ?
        WHERE id = ?
    """, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ticket_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Ticket #{ticket_id} closed successfully.")
    return True


def update_ticket(ticket_id, title, description, requester, department, priority, assignee, status):
    errors = validate_ticket_data(title, description, requester, department, priority)
    if errors:
        messagebox.showwarning("Validation Error", "\n".join(errors))
        return False

    valid_statuses = ["Open", "In Progress", "Closed"]
    if status not in valid_statuses:
        messagebox.showwarning("Validation Error", f"Status must be one of: {', '.join(valid_statuses)}.")
        return False

    ticket = get_ticket_by_id(ticket_id)
    if not ticket:
        messagebox.showerror("Error", f"Ticket #{ticket_id} not found.")
        return False

    closed_at = None
    if status == "Closed" and ticket["status"] != "Closed":
        closed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tickets SET title=?, description=?, requester=?, department=?,
        priority=?, assignee=?, status=?, updated_at=?, closed_at=?
        WHERE id=?
    """, (title.strip(), description.strip(), requester.strip(), department.strip(),
          priority, assignee.strip(), status, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
          closed_at, ticket_id))
    conn.commit()
    conn.close()
    messagebox.showinfo("Success", f"Ticket #{ticket_id} updated successfully.")
    return True


def export_tickets_to_excel(filepath):
    tickets = get_all_tickets()
    if not tickets:
        messagebox.showwarning("Warning", "No tickets to export.")
        return False

    df = pd.DataFrame(tickets)
    column_order = ["id", "title", "description", "requester", "department",
                    "priority", "status", "assignee", "created_at", "updated_at", "closed_at"]
    df = df[[c for c in column_order if c in df.columns]]
    df.columns = ["ID", "Title", "Description", "Requester", "Department",
                  "Priority", "Status", "Assignee", "Created At", "Updated At", "Closed At"]

    try:
        df.to_excel(filepath, index=False, engine="openpyxl")
        messagebox.showinfo("Success", f"Exported {len(tickets)} tickets to:\n{filepath}")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to export tickets:\n{str(e)}")
        return False


def import_tickets_from_excel(filepath):
    try:
        df = pd.read_excel(filepath, engine="openpyxl")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read Excel file:\n{str(e)}")
        return 0

    column_map = {
        "Title": "title", "Description": "description", "Requester": "requester",
        "Department": "department", "Priority": "priority", "Assignee": "assignee",
        "Status": "status"
    }

    imported = 0
    conn = get_connection()
    cursor = conn.cursor()

    for _, row in df.iterrows():
        title = str(row.get("Title", "")).strip() if pd.notna(row.get("Title")) else ""
        description = str(row.get("Description", "")).strip() if pd.notna(row.get("Description")) else ""
        requester = str(row.get("Requester", "")).strip() if pd.notna(row.get("Requester")) else ""
        department = str(row.get("Department", "")).strip() if pd.notna(row.get("Department")) else ""
        priority = str(row.get("Priority", "Medium")).strip() if pd.notna(row.get("Priority")) else "Medium"
        assignee = str(row.get("Assignee", "")).strip() if pd.notna(row.get("Assignee")) else ""
        status = str(row.get("Status", "Open")).strip() if pd.notna(row.get("Status")) else "Open"

        if priority not in ["Low", "Medium", "High", "Critical"]:
            priority = "Medium"
        if status not in ["Open", "In Progress", "Closed"]:
            status = "Open"

        if not title or not description or not requester or not department:
            continue

        cursor.execute("""
            INSERT INTO tickets (title, description, requester, department, priority, assignee, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (title, description, requester, department, priority, assignee, status))
        imported += 1

    conn.commit()
    conn.close()

    if imported > 0:
        messagebox.showinfo("Success", f"Imported {imported} tickets from Excel.")
    else:
        messagebox.showwarning("Warning", "No valid tickets found in the Excel file.")

    return imported
