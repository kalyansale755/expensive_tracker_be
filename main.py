from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import mysql.connector
import os


conn_obj = mysql.connector.connect(
    host=os.getenv("db_host"),
    user=os.getenv("db_user"),
    password=os.getenv("db_password"),
    database=os.getenv("db_name"),
    port=int(os.getenv("db_port"))
)

cur_obj = conn_obj.cursor(dictionary=True)


app = FastAPI()


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/expenses")
def add_expense(new_data: dict):

    title = new_data["title"]
    amount = new_data["amount"]
    category = new_data["category"]
    date = new_data["date"]

    query = """
    INSERT INTO expenses(title, amount, category, expense_date)
    VALUES(%s, %s, %s, %s)
    """

    values = (title, amount, category, date)

    cur_obj.execute(query, values)

    conn_obj.commit()

    return {
        "message": "Expense added successfully"
    }



@app.get("/expenses")
def view_expenses():

    query = "SELECT * FROM expenses"

    cur_obj.execute(query)

    data = cur_obj.fetchall()

    return data


@app.put("/expenses/{expense_id}")
def update_expense(expense_id: int, update_data: dict):

    title = update_data["title"]
    amount = update_data["amount"]
    category = update_data["category"]

    query = """
    UPDATE expenses
    SET title = %s,
        amount = %s,
        category = %s
    WHERE id = %s
    """

    values = (title, amount, category, expense_id)

    cur_obj.execute(query, values)

    conn_obj.commit()

    return {
        "message": "Expense updated successfully"
    }


@app.delete("/expenses/{expense_id}")
def delete_expense(expense_id: int):

    query = "DELETE FROM expenses WHERE id = %s"

    values = (expense_id,)

    cur_obj.execute(query, values)

    conn_obj.commit()

    return {
        "message": "Expense deleted successfully"
    }



@app.get("/expenses/search/{keyword}")
def search_expense(keyword: str):

    query = """
    SELECT *
    FROM expenses
    WHERE title LIKE %s
       OR category LIKE %s
    """

    value = (f"%{keyword}%", f"%{keyword}%")

    cur_obj.execute(query, value)

    data = cur_obj.fetchall()

    return data



@app.get("/expenses/filter/{category}")
def filter_expense(category: str):

    query = """
    SELECT *
    FROM expenses
    WHERE category = %s
    """

    values = (category,)

    cur_obj.execute(query, values)

    data = cur_obj.fetchall()

    return data



@app.get("/expenses/sort/{field}")
def sort_expenses(field: str):

    allowed_fields = ["amount", "expense_date", "category"]

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


@app.get("/expenses/analysis")
def analyze_spending():

    # Total Spending

    total_query = """
    SELECT SUM(amount) AS total_spending
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
        "total_spending": total_data["total_spending"],
        "category_wise": category_data
    }