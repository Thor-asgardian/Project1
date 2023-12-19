from flask import flash, Flask, request, render_template, redirect, session, jsonify
import os
import mysql.connector

from werkzeug.utils import secure_filename
import statistics
import nltk
from string import punctuation
import re
from nltk.corpus import stopwords
from random import randint

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
nltk.download('stopwords')

conn = mysql.connector.connect(host="localhost", user="root", password="root", database="ecommerce", charset="utf8")
cursor = conn.cursor()
cursor1 = conn.cursor()
app = Flask(__name__)
app.secret_key = os.urandom(24)

app.config["IMAGE_UPLOAD"] = "/Static/uploads"

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/Admin')
def Admin():
    return render_template("Admin.html")


@app.route('/AdminLogin', methods=['POST'])
def AdminLogin():
    error = None
    email = request.form.get('email')
    password = request.form.get('password')
    cursor.execute("""select * from `admin` where aemail like '{}' and apswd like '{}'""".format(email, password))
    admin = cursor.fetchall()
    print(admin)
    if len(admin) > 0:
        session['admin_id'] = admin[0][0]
        print(session['admin_id'])
        print(admin[0][0])
        flash('You were successfully logged in')
        return redirect('/adminhome')
    else:
        error = 'Invalid credentials'
        return redirect('/')



@app.route('/Register')
def Register():
    return render_template("register.html")


@app.route('/registration', methods=['POST'])
def registration():
    fname = request.form.get('firstname')
    lname = request.form.get('lastname')
    addrs = request.form.get('addrs')
    phoneno = request.form.get('phoneno')
    email = request.form.get('email')
    password = request.form.get('password')
    cursor.execute("""INSERT INTO `userregister`(`ufname`,`ulname`,`uaddrs`,`uphone`,`uemail`,`upaswd`) VALUES ('{}','{}','{}','{}',
    '{}','{}')""".format(fname, lname, addrs, phoneno, email, password))
    conn.commit()
    return render_template("register.html")

@app.route('/userregister')
def userregister():
    cursor.execute("""SELECT * FROM `userregister`""")
    register = cursor.fetchall()
    return render_template("Admin/viewuserregister.html",data=register)

@app.route('/User')
def User():
    return render_template("User.html")

@app.route('/userlogin', methods=['POST'])
def userlogin():
    uemail = request.form.get('email')
    upassword = request.form.get('password')
    cursor.execute("""select * from `userregister` where uemail like '{}' and upaswd like '{}' """.format(uemail, upassword))
    user = cursor.fetchall()
    # print(user)
    # cursor.execute("""select * from `booking` """)
    # products = cursor.fetchall()
    # print(products)
    cursor.execute("""select `preview` from `booking`""")
    review = cursor.fetchall()
    print(review)


    # products = pd.DataFrame
    # print(products)
    #
    # final_ratings_matrix = products.pivot(index='userId', columns='productId', values='ratings').fillna(0)
    # print(final_ratings_matrix.head())
    # print(products[:2])
    # most_rated = products.groupby('uid').size().sort_values(ascending=False)[:10]
    # print(most_rated)
    if len(user) > 0:
        session['user_id'] = user[0][0]
        return redirect('/Userhome')
    else:
        return redirect('/')

@app.route('/Userhome')
def Userhome():
    return render_template("User/userHome.html")


@app.route('/profile')
def profile():
    return render_template("User/profile.html")


@app.route('/adminviewprd')
def adminviewprd():
    cursor.execute("""SELECT c.`Category`, p.* FROM `product` p JOIN Category c ON c.`cid`=p.`pcategory` """)
    product = cursor.fetchall()
    return render_template("Admin/viewproduct.html",data=product)

@app.route('/delete_product/<string:id_data>/', methods=['POST', 'GET'])
def delete_doctor(id_data):
    cursor.execute("DELETE FROM `product` WHERE  pid = %s", (id_data,))
    conn.commit()
    return redirect('/adminviewprd')


@app.route('/profiledetails')
def profiledetails():
    user = session['user_id']
    cursor.execute("""SELECT * FROM `userregister` where uid like '{}'""".format(user))
    user = cursor.fetchall()
    return render_template("User/profile.html", user=user)

@app.route('/viewproducts')
def viewproducts():
    cursor.execute("""SELECT p.*,ROUND(TRUNCATE(IFNULL((IFNULL((SELECT SUM(`preview`) FROM `booking` b WHERE b.`pid` = p.`pid`), 0) / IFNULL((SELECT COUNT(*) FROM `booking` b WHERE b.`pid` = p.`pid`), 0)), 1),1)) AS rating
FROM `product` p """)
    product = cursor.fetchall()
    return render_template("User/product.html",data=product)

@app.route('/ViewProductsFromAjax')
def ViewProductsFromAjax():
#     cursor.execute("""SELECT p.*,ROUND(TRUNCATE(IFNULL((IFNULL((SELECT SUM(`preview`) FROM `booking` b WHERE b.`pid` = p.`pid`), 0) / IFNULL((SELECT COUNT(*) FROM `booking` b WHERE b.`pid` = p.`pid`), 0)), 1),1)) AS rating
# FROM `product` p """)
    cursor.execute("""SELECT `Category`, p.*, ROUND(TRUNCATE(IFNULL((IFNULL((SELECT SUM(`preview`) FROM `booking` b WHERE b.`pid` = p.`pid`), 0) / IFNULL((SELECT COUNT(*) FROM `booking` b WHERE b.`pid` = p.`pid`), 0)), 1),1)) AS rating FROM `product` p JOIN `category` c ON c.`cid` = p.`pcategory`""")
    product = cursor.fetchall()
    return jsonify(product)

#---------------------------Admin---------------------------


@app.route('/adminhome')
def adminhome():
    return render_template("Admin/adminhomepage.html")

@app.route('/category')
def category():
    return render_template("Admin/addcategory.html")

@app.route('/Adding_category', methods=['POST'])
def Adding_category():
    category = request.form.get('category')

    cursor.execute("""INSERT INTO `category`(`Category`) VALUES ('{}'
    )""".format(category))
    conn.commit()
    return render_template("Admin/addcategory.html")

@app.route('/Product')
def Product():
    cursor.execute("""select cid,Category from `category`""")
    category = cursor.fetchall()
    return render_template("Admin/addproduct.html", data=category)

@app.route('/Adding_Product', methods=['POST'])
def Adding_Product():

    cursor.execute("""select cid,Category from `category`""")
    category1 = cursor.fetchall()

    category = request.form.get('category')
    product = request.form.get('product')
    Price = request.form.get('Price')
    pd = request.form.get('pd')
    image = request.files["file1"]
    image.save(os.path.join(app.config["IMAGE_UPLOAD"],image.filename))
    img = image.filename
    image1 = request.files["file2"]
    image1.save(os.path.join(app.config["IMAGE_UPLOAD"], image1.filename))
    img1 = image1.filename

    cursor.execute("""INSERT INTO `product`(`pcategory`,`productname`,`price`,`productdes`,`pimage1`,`pimage2`) VALUES ('{}','{}','{}','{}','{}','{}'
    )""".format(category, product, Price, pd,img,img1))
    conn.commit()
    return render_template("Admin/addproduct.html", data=category1)


@app.route('/userorders')
def userorders():
    cursor.execute("""SELECT * FROM `booking`""")
    booking = cursor.fetchall()
    return render_template("Admin/viewbooking.html",data=booking)




@app.route('/booking')
def booking():
    return render_template("User/booking.html")

@app.route('/bookingid/<string:id_data>/', methods=['POST', 'GET'])
def bookingid(id_data):
    cursor.execute("Select * FROM `product` WHERE  pid like {}" .format(id_data,))
    products = cursor.fetchall()
    return render_template("User/booking.html",data=products)


@app.route('/userbooking', methods=['POST'])
def userbooking():
    pid = request.form.get('pid')
    print(pid)
    cursor.execute("""Select * FROM `product` where pid like '{}'""".format(pid))
    medical = cursor.fetchall()
    print(medical)
    # cursor.callproc('GetAllProducts')
    # for result in cursor.stored_results():
    #     print(result.fetchall())
    # cursor1.execute("""select `preview` FROM `booking` where pid like '{}'""".format(pid))
    # review = cursor1.fetchall()
    # print(review)
    # print(type(review))
    # my_array = np.array(review)
    # print(my_array)
    # avg = sum(my_array)
    # print(avg)
    # reviewarr = np.asarray(review)
    # print(reviewarr)
    # mean = statistics.mean(reviewarr)
    # print(mean)
    return jsonify(medical)

@app.route('/userbooking1', methods=['POST'])
def userbooking1():
    pid = request.form.get('pid')
    print(pid)
    cursor.execute("""Select * FROM `booking` where bid like '{}'""".format(pid))
    medical = cursor.fetchall()
    print(medical)
    return jsonify(medical)

@app.route('/sendreview', methods=['POST'])
def sendreview():
    stop_words = stopwords.words('english')

    review = request.form.get('review').lower()
    bid = request.form.get('bid')


    text_final = ''.join(c for c in review if not c.isdigit())

    processed_doc1 = ' '.join([word for word in text_final.split() if word not in stop_words])

    sa = SentimentIntensityAnalyzer()

    dd = sa.polarity_scores(text=processed_doc1)

    if dd['compound'] >= 0.05:
        positive = print("Positive")
        value = randint(4, 5)
        print(value)
        print(bid)
        cursor.execute("UPDATE `booking` SET `preview`=%s WHERE `bid`=%s", (value, bid))
        conn.commit()


    elif dd['compound'] <= - 0.05:
        negative = print("Negative")
        value1 = randint(0, 1)
        print(value1)
        print(bid)
        cursor.execute("UPDATE `booking` SET `preview`=%s WHERE `bid`=%s", (value1, bid))
        conn.commit()

    else:
        neutral = print("Neutral")
        value2 = randint(2, 3)
        print(value2)
        print(bid)
        cursor.execute("UPDATE `booking` SET `preview`=%s WHERE `bid`=%s", (value2, bid))
        conn.commit()


    #print(review)
    #bid = request.form.get('bid')
    #print(bid)
    #cursor.execute("UPDATE `booking` SET `preview`=%s WHERE `bid`=%s", (review,bid))
    #medical = conn.commit()
    return jsonify(bid)

@app.route('/ConformBiddingProduct',methods=['POST'])
def ConformBiddingProduct():
    userid = session['user_id']
    print(userid)
    pid = request.form.get('pid')
    print(pid)
    qty = request.form.get('qty')
    print(qty)
    tmat = request.form.get('tmat')
    print(tmat)
    prd = request.form.get('prd')
    print(prd)
    pdes = request.form.get('pdes')
    print(pdes)
    img = request.form.get('img')
    print(img)
    cat = request.form.get('cat')
    print(cat)
    cursor.execute("""INSERT INTO `booking`(`uid`,`pid`,`pname`,`pqty`,`ptprice`,`pdiscription`,`cid`) VALUES ('{}','{}','{}','{}','{}','{}','{}'
    )""".format(userid, pid, prd, qty, tmat, pdes,cat))
    conn.commit()
    return jsonify(status="success")

@app.route('/myorder')
def myorder():
    userid = session['user_id']
    cursor.execute("""SELECT * FROM `booking` where uid like {}""".format(userid))
    booking = cursor.fetchall()
    return render_template("User/booking.html",data=booking)

if __name__ == "__main__":
    app.run(debug=True)
