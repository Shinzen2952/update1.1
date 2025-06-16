from flask import Flask, redirect, url_for, render_template, request,flash,session,jsonify
import sqlite3
import os 
app=Flask(__name__,template_folder='templates')



@app.route("/view_orders")
def view_orders():
    if session.get("username") != "admin" or session.get("password") != "admin123":
        return "Unauthorized Access", 403

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY order_time DESC")
    orders = cursor.fetchall()
    conn.close()

    return render_template("orders.html", orders=orders)

from datetime import datetime

@app.route("/my_orders")
def my_orders():
    if "user_id" not in session:
        flash("Please log in to view your orders.")
        return redirect(url_for("loging"))

    user_id = session["user_id"]
    conn = sqlite3.connect("orders.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE user_id = ?", (user_id,))
    orders = cursor.fetchall()
    conn.close()

    return render_template("my_orders.html", orders=orders)


@app.route("/update_status", methods=["POST"])
def update_status():
    if session.get("username") != "admin" or session.get("password") != "admin123":
        return "Unauthorized", 403

    order_id = request.form.get("order_id")
    new_status = request.form.get("status")

    conn = sqlite3.connect("orders.db")
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()

    return redirect(url_for("view_orders"))



from datetime import datetime, timedelta

@app.route('/confirm_order', methods=['POST'])
def confirm_order():
    if "user_id" not in session:
        return redirect(url_for('loging'))

    user_id = session["user_id"]

    conn1 = get_db_connection()
    cursor1 = conn1.cursor()
    cursor1.execute("SELECT title, img FROM shelf WHERE user_id = ?", (user_id,))
    books = cursor1.fetchall()
    conn1.close()

    order_time = datetime.now()
    return_time = order_time + timedelta(days=3)

    conn2 = sqlite3.connect("orders.db")
    cursor2 = conn2.cursor()

    for book in books:
        cursor2.execute("""
            INSERT INTO orders (user_id, username, title, img, order_time, status, expected_return_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, session["username"], book["title"], book["img"],
            order_time.strftime("%Y-%m-%d %H:%M:%S"),
            "To Be Claimed",
            return_time.strftime("%Y-%m-%d")
        ))

    conn2.commit()
    conn2.close()

    return redirect(url_for('about'))


@app.route("/add_to_shelf", methods=["POST"])
def add_to_shelf():
    if "user_id" not in session:
        return jsonify({"message": "❌ Please log in to add books to your shelf."}), 401

    data = request.get_json()
    title = data.get("title")
    img = data.get("img")
    user_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO shelf (user_id, title, img) VALUES (?, ?, ?)", (user_id, title, img))
        conn.commit()
        message = f"✅ \"{title}\" added to your shelf!"
    except sqlite3.IntegrityError:
        message = f"⚠️ \"{title}\" is already on your shelf."

    conn.close()
    return jsonify({"message": message})
app.secret_key = os.urandom(24) 
@app.route('/')
def zero(): 
    return redirect(url_for('web')) 

@app.route('/user/func')
def web():
    return render_template("web.html")

from datetime import datetime

@app.route('/Shelf')
def about():
    if "user_id" not in session:
        flash("Please log in to view your shelf.")
        return redirect(url_for("loging"))

    user_id = session["user_id"]

    conn1 = get_db_connection()
    cursor1 = conn1.cursor()
    cursor1.execute("SELECT title, img FROM shelf WHERE user_id = ?", (user_id,))
    books = cursor1.fetchall()
    conn1.close()

    conn2 = sqlite3.connect("orders.db")
    conn2.row_factory = sqlite3.Row
    cursor2 = conn2.cursor()
    cursor2.execute("SELECT title, status, order_time FROM orders WHERE user_id = ?", (user_id,))
    orders = cursor2.fetchall()
    conn2.close()

    orders_dict = {}
    for row in orders:
        title = row["title"]
        order_time = datetime.strptime(row["order_time"], "%Y-%m-%d %H:%M:%S")
        days_passed = (datetime.now() - order_time).days
        status = row["status"]

        if status != "Finished" and days_passed > 3:
            status = f"Expired ({days_passed - 3} days overdue)"

        orders_dict[title] = status

    books_with_status = []
    for book in books:
        status = orders_dict.get(book["title"], "To Be Claimed")
        books_with_status.append({
            "title": book["title"],
            "img": book["img"],
            "status": status
        })

    return render_template('Shelf.html', books=books_with_status)


@app.route('/remove_book', methods=['POST'])
def remove_book():
    if "user_id" not in session:
        return "Unauthorized", 401

    title = request.form.get('title')
    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shelf WHERE user_id = ? AND title = ?", (user_id, title))
    conn.commit()
    conn.close()
    return "Book removed", 200


@app.route('/clear_shelf', methods=['POST'])
def clear_shelf():
    if "user_id" not in session:
        return "Unauthorized", 401

    user_id = session['user_id']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM shelf WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return "Shelf cleared", 200


@app.route('/Home')
def black_holes():
    return render_template('web.html')

@app.route("/loging")
def logging():
    return render_template('loging.html')    

@app.route("/BTOD")
def btod():
    return render_template('BTOD.html')   

def get_db_connection():
    conn = sqlite3.connect('users.db')   
    conn.row_factory = sqlite3.Row      
    return conn

@app.route("/register", methods=["GET", "POST"])
def register():
    msg = ''
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        email = request.form.get("email")

        conn = get_db_connection()  
        cursor = conn.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)",
                           (username, password, email))
            conn.commit()
            msg = "✅ Successfully registered!"
        except sqlite3.IntegrityError:
            msg = "❌ Username or Email already exists!"
        conn.close()

    return render_template('register.html', msg=msg)


@app.route("/loging", methods=["GET", "POST"])
def loging():
    msg = ''

    if "user_id" in session:
        msg = "⚠️ You are already logged in."
        return render_template("loging.html", msg=msg)

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user:
            if user["password"] == password:
                session["user_id"] = user["id"]
                session["username"] = user["username"]
                session["password"] = user["password"]  # 

                msg = "✅ Login successful!"
                return redirect(url_for("web"))
            else:
                msg = "❌ Incorrect password."
        else:
            msg = "❌ Username not found."

    return render_template("loging.html", msg=msg)


@app.route("/logout")
def logout():
    session.clear()  
    flash("You have been logged out.")
    return redirect(url_for("loging"))

@app.route('/authorized')
def view_users():
    if session.get("username") != "admin" or session.get("password") != "admin123":
        return "Unauthorized Access", 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()

    output = """
    <h2 style="font-family: Arial, sans-serif; color: #333;">Registered Users:</h2>
    <table border="1" cellpadding="8" cellspacing="0" 
           style="border-collapse: collapse; width: 90%; font-family: Arial, sans-serif;">
        <thead style="background-color: #f2f2f2;">
            <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Password</th>
                <th>Email</th>
                <th>Action</th>
            </tr>
        </thead>
        <tbody>
    """

    for user in users:
        output += f"""
        <tr style="text-align: center;">
            <td>{user['id']}</td>
            <td>{user['username']}</td>
            <td>{user['password']}</td>
            <td>{user['email']}</td>
            <td><a href="/remove_user/{user['id']}" 
                   style="color: red; text-decoration: none;" 
                   onclick="return confirm('Are you sure?')">Remove</a></td>
        </tr>
        """

    output += """
        </tbody>
    </table>
    <br><br>
    <form method="POST" action="/clear_users" onsubmit="return confirm('Clear all users?')">
        <input type="submit" value="Clear All" 
               style="padding: 10px 20px; background-color: red; color: white; border: none; 
                      border-radius: 5px; cursor: pointer; font-weight: bold;" />
    </form>
    """

    return output

@app.route('/remove_user/<int:user_id>')
def remove_user(user_id):
    if session.get("username") != "admin" or session.get("password") != "admin123":
        return "Unauthorized Access", 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/authorized')

@app.route('/clear_users', methods=['POST'])
def clear_users():
    if session.get("username") != "admin" or session.get("password") != "admin123":
        return "Unauthorized Access", 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users")
    conn.commit()
    conn.close()
    return redirect('/authorized')


def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == '__main__':
    app.run(debug=True)


