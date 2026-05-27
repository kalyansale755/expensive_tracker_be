from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import os


# =========================================
# FASTAPI APP
# =========================================

app = FastAPI()


# =========================================
# CORS
# =========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================
# DATABASE CONNECTION
# =========================================

try:

    conn_obj = mysql.connector.connect(
        host=os.getenv("db_host"),
        user=os.getenv("db_user"),
        password=os.getenv("db_password"),
        database=os.getenv("db_name"),
        port=int(os.getenv("db_port"))
    )

    cur_obj = conn_obj.cursor(
        dictionary=True
    )

    print("✅ Database Connected Successfully - main.py:45")

    
    # =========================================
    # CREATE TABLE IF NOT EXISTS
    # =========================================

    create_table_query = """
    CREATE TABLE IF NOT EXISTS expenses (

        id INT PRIMARY KEY AUTO_INCREMENT,

        title VARCHAR(255) NOT NULL,

        amount DECIMAL(10,2) NOT NULL,

        category VARCHAR(100) NOT NULL,

        expense_date DATE NOT NULL

    )
    """

    cur_obj.execute(create_table_query)

    conn_obj.commit()

    print("✅ Expenses Table Ready - main.py:72")

    
except Exception as e:

    print("❌ Database Connection Error - main.py:77")
    print(e)

    conn_obj = None
    cur_obj = None


# =========================================
# ROOT ROUTE
# =========================================

@app.get("/")
def home():

    return {
        "message": "Expense Tracker Backend Running Successfully"
    }


# =========================================
# CHECK DATABASE
# =========================================

def check_db():

    if conn_obj is None or cur_obj is None:

        raise HTTPException(
            status_code=500,
            detail="Database Connection Failed"
        )


# =========================================
# ADD EXPENSE
# =========================================

@app.post("/expenses")
def add_expense(new_data: dict):

    check_db()

    try:

        title = new_data.get("title")
        amount = new_data.get("amount")
        category = new_data.get("category")
        date = new_data.get("date")

        if not title:

            raise HTTPException(
                status_code=400,
                detail="Title is required"
            )

        query = """
        INSERT INTO expenses(
            title,
            amount,
            category,
            expense_date
        )
        VALUES(%s, %s, %s, %s)
        """

        values = (
            title,
            amount,
            category,
            date
        )

        cur_obj.execute(query, values)

        conn_obj.commit()

        return {
            "message": "Expense added successfully"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================
# VIEW EXPENSES
# =========================================

@app.get("/expenses")
def view_expenses():

    check_db()

    try:

        query = """
        SELECT *
        FROM expenses
        """

        cur_obj.execute(query)

        data = cur_obj.fetchall()

        return data

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================
# UPDATE EXPENSE
# =========================================

@app.put("/expenses/{expense_id}")
def update_expense(
    expense_id: int,
    update_data: dict
):

    check_db()

    try:

        title = update_data.get("title")
        amount = update_data.get("amount")
        category = update_data.get("category")

        query = """
        UPDATE expenses
        SET title = %s,
            amount = %s,
            category = %s
        WHERE id = %s
        """

        values = (
            title,
            amount,
            category,
            expense_id
        )

        cur_obj.execute(query, values)

        conn_obj.commit()

        return {
            "message": "Expense updated successfully"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================
# DELETE EXPENSE
# =========================================

@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):

    check_db()

    try:

        query = """
        DELETE FROM expenses
        WHERE id = %s
        """

        values = (expense_id,)

        cur_obj.execute(query, values)

        conn_obj.commit()

        return {
            "message": "Expense deleted successfully"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================
# SEARCH EXPENSE
# =========================================

@app.get("/expenses/search/{keyword}")
def search_expense(keyword: str):

    check_db()

    try:

        query = """
        SELECT *
        FROM expenses
        WHERE title LIKE %s
           OR category LIKE %s
        """

        values = (
            f"%{keyword}%",
            f"%{keyword}%"
        )

        cur_obj.execute(query, values)

        data = cur_obj.fetchall()

        return data

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================
# FILTER EXPENSES
# =========================================

@app.get("/expenses/filter/{category}")
def filter_expense(category: str):

    check_db()

    try:

        query = """
        SELECT *
        FROM expenses
        WHERE category = %s
        """

        values = (category,)

        cur_obj.execute(query, values)

        data = cur_obj.fetchall()

        return data

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================
# SORT EXPENSES
# =========================================

@app.get("/expenses/sort/{field}")
def sort_expenses(field: str):

    check_db()

    try:

        allowed_fields = [
            "amount",
            "expense_date",
            "category"
        ]

        if field not in allowed_fields:

            raise HTTPException(
                status_code=400,
                detail="Invalid sorting field"
            )

        query = f"""
        SELECT *
        FROM expenses
        ORDER BY {field}
        """

        cur_obj.execute(query)

        data = cur_obj.fetchall()

        return data

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================
# ANALYSIS
# =========================================

@app.get("/expenses/analysis")
def analyze_spending():

    check_db()

    try:

        total_query = """
        SELECT SUM(amount)
        AS total_spending
        FROM expenses
        """

        cur_obj.execute(total_query)

        total_data = cur_obj.fetchone()

        category_query = """
        SELECT category,
               SUM(amount) AS total
        FROM expenses
        GROUP BY category
        """

        cur_obj.execute(category_query)

        category_data = cur_obj.fetchall()

        return {
            "total_spending":
                total_data["total_spending"],

            "category_wise":
                category_data
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )