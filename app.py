from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a random secret key for production

# Hàm kết nối đến cơ sở dữ liệu
def connect_to_db(username, password):
    try:
        connection = psycopg2.connect(
            dbname="MyDatabase",
            user=username,
            password=password,
            host="localhost"
        )
        return connection
    except Exception as e:
        return None

# Chức năng tìm kiếm sản phẩm không phân biệt hoa thường
def search_product(connection, product_name):
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM products WHERE product_name ILIKE %s"
        cursor.execute(query, ('%' + product_name + '%',))
        result = cursor.fetchall()
        cursor.close()
        return result
    except Exception as e:
        return None

# Chức năng thêm sản phẩm mới
def add_product(connection, product_name, product_price, category_id):
    try:
        cursor = connection.cursor()
        query = "INSERT INTO products (product_name, product_price, category_id) VALUES (%s, %s, %s)"
        cursor.execute(query, (product_name, product_price, category_id))
        connection.commit()
        cursor.close()
    except Exception as e:
        return None

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        connection = connect_to_db(username, password)
        if connection:
            session['username'] = username  # Store username in session
            session['password'] = password  # Store password in session
            return redirect(url_for('menu'))
        else:
            flash('Không thể kết nối đến cơ sở dữ liệu. Vui lòng kiểm tra lại thông tin.')
    return render_template('login.html')

@app.route('/menu')
def menu():
    return render_template('menu.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        product_name = request.form['product_name']
        username = session.get('username')
        password = session.get('password')
        connection = connect_to_db(username, password)
        results = search_product(connection, product_name)
        return render_template('search.html', results=results)
    return render_template('search.html', results=None)

@app.route('/add_product', methods=['GET', 'POST'])
def add_product_route():
    if request.method == 'POST':
        product_name = request.form['product_name']
        product_price = request.form['product_price']
        category_id = request.form['category_id']
        username = session.get('username')
        password = session.get('password')
        connection = connect_to_db(username, password)
        add_product(connection, product_name, product_price, category_id)
        flash('Thêm sản phẩm thành công!')  # Flash message
        return redirect(url_for('menu'))
    return render_template('add_product.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
