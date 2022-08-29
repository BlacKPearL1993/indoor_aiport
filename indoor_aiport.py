import random
import time
from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from DBConnection import Db

app = Flask(__name__)
app.secret_key="indoor"

static_path=r"E:\riss kannur\2022-2023 workspace\jamia\indoor_aiport\static\\"


@app.route('/', methods=['get', 'post'])
def login():
    if request.method=="POST":
        user = request.form['textfield']
        psw = request.form['textfield2']
        db = Db()
        res = db.selectOne("SELECT * FROM `login` WHERE `username`='" + user + "' AND `password`='" + psw + "'")
        if res != None:
            type = res['user_type']
            lid = res['login_id']
            session['lid'] = lid
            if type == "admin":
                return redirect(url_for('admin_home'))
            elif type == "dept":
                db=Db()
                res2=db.selectOne("SELECT * FROM department WHERE department_id='"+str(lid)+"'")
                session['log_name']=res2['dep_name']
                return redirect(url_for('dept_home'))
            elif type == "shop":
                db = Db()
                res2 = db.selectOne("SELECT * FROM shops WHERE shop_id='" + str(lid) + "'")
                session['log_name'] = res2['shop_name']
                return redirect(url_for('shop_home'))
            elif type == "staff":
                db=Db()
                res2=db.selectOne("SELECT * FROM `staffs`, `department` WHERE department.department_id=staffs.department_id AND staffs.staff_id='"+str(lid)+"'")
                session['log_name'] = res2['first_name'] + " " + res2['last_name']
                return redirect(url_for('staff_home'))
            else:
                return '<script>alert("Invalid user")</script>'
        else:
            return '<script>alert("Invalid username or password");window.location="/"</script>'
    return render_template("login.html")



@app.route('/admin_home')
def admin_home():
  return render_template("admin/admin_temp.html")


@app.route('/dept_add', methods=['get', 'post'])
def dept_add():
    if request.method=="POST":
        c=Db()
        name=request.form['textfield']
        details=request.form['textfield2']
        email = request.form['textfield3']
        phone = request.form['textfield4']
        password=random.randint(1000, 9999)
        lid=c.insert("INSERT INTO `login`(`username`,`password`,`user_type`)VALUES('"+email+"','"+str(password)+"','dept')")
        qy="INSERT INTO `department` VALUES ('"+str(lid)+"','"+name+"', '"+email+"', '"+phone+"', '"+details+"')"
        c.insert(qy)
        return redirect("/dept_add")
    return render_template("admin/dept_add.html")

@app.route('/dept_view')
def dept_view():
    db = Db()
    res = db.select("SELECT * FROM department")
    return render_template("admin/dept_view.html",data=res)

@app.route('/dept_delete/<lid>')
def dept_delete(lid):
    db=Db()
    db1 = Db()
    db.delete("DELETE FROM `department` WHERE `department_id`='"+lid+"'")
    db1.delete("DELETE FROM `login` WHERE `login_id`='"+lid+"'")
    return '<script>window.location="/dept_view"</script>'


@app.route("/admin_add_building", methods=['get', 'post'])
def admin_add_building():
    if request.method=="POST":
        name=request.form['textfield']
        floors=request.form['textfield2']
        db=Db()
        db.insert("INSERT INTO buildings(building_name, no_of_floors) VALUES('"+name+"', '"+floors+"')")
        return "<script>alert('Building added');window.location='/admin_add_building';</script>"
    return render_template("admin/building_add.html")

@app.route("/admin_view_building")
def admin_view_building():
    db=Db()
    res=db.select("SELECT * FROM buildings")
    return render_template("admin/building_view.html", data=res)

@app.route("/admin_delete_building/<bid>")
def admin_delete_building(bid):
    db=Db()
    db.delete("DELETE FROM `buildings` WHERE building_id='"+bid+"'")
    return redirect("/admin_view_building")

@app.route("/admin_shops_add/<bid>", methods=['get', 'post'])
def admin_shops_add(bid):
    if request.method=="POST":
        shop_name=request.form['textfield']
        shop_no=request.form['textfield2']
        email=request.form['textfield3']
        phone=request.form['textfield4']
        floor=request.form['textfield5']
        password=random.randint(1000, 9999)
        db=Db()
        lid=db.insert("INSERT INTO login(username, PASSWORD, user_type) VALUES('"+email+"', '"+str(password)+"', 'shop')")
        db.insert("INSERT INTO shops(shop_id, shop_name, shop_no, email, phone, floor_no, building_id) VALUES('"+str(lid)+"', '"+shop_name+"', '"+shop_no+"', '"+email+"', '"+phone+"', '"+floor+"', '"+bid+"')")
        return "<script>alert('Shop Added');window.location='/admin_shops_add/"+bid+"';</script>"
    db=Db()
    res=db.select("SELECT * FROM shops WHERE building_id='"+bid+"'")
    return render_template("admin/shop_add.html", data=res)

@app.route("/admin_delete_shops/<shopid>/<bid>")
def admin_delete_shops(shopid, bid):
    db=Db()
    db.delete("DELETE FROM login WHERE login_id='"+shopid+"'")
    db.delete("DELETE FROM shops WHERE shop_id='"+shopid+"'")
    return redirect("/admin_shops_add/"+bid)



@app.route('/admin_help_request')
def admin_help_request():
    db=Db()
    res=db.select("SELECT `help_request`.*,`passenger`.*, staffs.* FROM `passenger`,`help_request`, staffs WHERE `help_request`.`passenger_id`=`passenger`.`passenger_id` and help_request.staff_id=staffs.staff_id")
    return render_template("admin/view_help_request.html", data=res)


@app.route("/admin_add_service", methods=['get', 'post'])
def admin_add_service():
    if request.method=="POST":
        name=request.form['textfield']
        descr=request.form['textfield2']
        db=Db()
        db.insert("INSERT INTO service(service_name, description) VALUES('"+name+"', '"+descr+"')")
        return "<script> alert('Service Added');window.location='/admin_add_service';</script>"
    return render_template("admin/service_add.html")

@app.route("/admin_view_service")
def admin_view_service():
    db=Db()
    res=db.select("SELECT * FROM service")
    return render_template("admin/service_view.html", data=res)

@app.route("/admin_delete_service/<sid>")
def admin_delete_service(sid):
    db=Db()
    db.delete("DELETE FROM service WHERE service_id='"+sid+"'")
    return redirect("/admin_view_service")

@app.route("/add_schedule/<sid>", methods=['get', 'post'])
def add_schedule(sid):
    if request.method=="POST":
        src=request.form['textfield']
        dest=request.form['textfield2']
        date=request.form['textfield3']
        time=request.form['textfield4']
        db=Db()
        db.insert("INSERT INTO SCHEDULE(service_id, flight_from, flight_to, DATE, TIME) VALUES('"+sid+"', '"+src+"', '"+dest+"', '"+date+"', '"+time+"')")
        return "<script>alert('Schedule added');window.location='/admin_view_service';</script>"
    return render_template("admin/schedule_add.html")

@app.route("/admin_view_schedule/<sid>")
def admin_view_schedule(sid):
    session['servid']=sid
    db=Db()
    res=db.select("SELECT * FROM SCHEDULE WHERE service_id='"+sid+"'")
    return render_template("admin/schedule_view.html", data=res)

@app.route("/delete_schedule/<sid>")
def delete_schedule(sid):
    db=Db()
    db.delete("DELETE FROM SCHEDULE WHERE schedule_id='"+sid+"'")
    servid=session['servid']
    return redirect("/admin_view_schedule/"+servid)





################################################        DEPARTMENT

@app.route('/dept_home')
def dept_home():
  return render_template("department/dept_home.html")


@app.route('/add_staff', methods=['get', 'post'])
def add_staff():
    if request.method=="POST":
        c = Db()
        dept_lid = session['lid']
        fname = request.form['textfield']
        lname = request.form['textfield2']
        house = request.form['textfield3']
        place = request.form['textfield4']
        email = request.form['email']
        phone = request.form['phone']
        pswd = random.randint(1000, 9999)
        db = Db()
        lid = db.insert(
            "INSERT INTO `login`(`username`,`password`,`user_type`)VALUES('" + email + "','" + str(pswd) + "','staff')")
        qry = "INSERT INTO `staffs`(`staff_id`,`first_name`,`last_name`,`house_name`,`place`,`email`,`phone`,`department_id`)VALUES('" + str(
            lid) + "','" + fname + "','" + lname + "','" + house + "','" + place + "','" + email + "','" + phone + "','" + str(
            dept_lid) + "')"
        c.insert(qry)
        return '<script>alert("Success...");window.location="/add_staff"</script>'
    return render_template("Department/staff_add.html")



@app.route('/view_my_staff')
def view_my_staff():
    db=Db()
    lid = session['lid']
    res=db.select("SELECT * FROM `staffs` WHERE `department_id`='"+str(lid)+"'")
    if len(res)>0:
        return render_template('Department/staff_view.html',data=res)
    else:
        return '<script>alert("No data");window.location="/dept_home"</script>'

@app.route('/delete_staff/<id>')
def delete_staff(id):
    db=Db()
    db1 = Db()
    db.delete("DELETE FROM `staffs` WHERE `staff_id`='"+id+"'")
    db1.delete("DELETE FROM `login` WHERE `login_id`='"+id+"'")
    return redirect("/view_my_staff")

@app.route('/edit_staff/<id>', methods=['get', 'post'])
def edit_staff(id):
    if request.method=="POST":
        c = Db()
        fname = request.form['textfield']
        lname = request.form['textfield2']
        house = request.form['textfield3']
        place = request.form['textfield4']
        phone = request.form['phone']
        db = Db()
        qry = "UPDATE `staffs` SET `first_name`='" + fname + "',`last_name`='" + lname + "',`house_name`='" + house + "',`place`='" + place + "',`phone`='" + phone + "' WHERE `staff_id`='" + id + "'"
        c.update(qry)
        return '<script>alert("Updated...");window.location="/view_my_staff"</script>'
    db=Db()
    res=db.selectOne("SELECT * FROM `staffs` WHERE `staff_id`='"+id+"'")
    return render_template('Department/staff_edit.html',data=res)

@app.route('/add_work', methods=['get', 'post'])
def add_work():
    if request.method=="POST":
        c = Db()
        staff = request.form['select']
        title = request.form['textfield']
        description = request.form['textfield2']
        qry = "INSERT INTO `works`(`staff_id`,`title`,`description`,`date`,`time`,status) VALUES('" + staff + "','" + title + "','" + description + "',curdate(),curtime(),'pending')"
        c.insert(qry)
        return redirect("/add_work")
    db=Db()
    res=db.select("SELECT * FROM staffs WHERE department_id='"+str(session['lid'])+"'")
    return render_template('Department/assign_work.html', data=res)

@app.route('/dept_work_view')
def dept_work_view():
    db=Db()
    qry="SELECT * FROM `staffs`,`works` WHERE `works`.`staff_id`=`staffs`.`staff_id`"
    res=db.select(qry)
    return render_template("Department/assign_work_view.html",data=res)

@app.route('/delete_work/<wid>')
def delete_work(wid):
    qry="DELETE FROM `works` WHERE `work_id`='"+str(wid)+"'"
    db=Db()
    db.delete(qry)
    return redirect("/dept_work_view")

@app.route('/dept_compl_view')
def dept_compl_view():
    db=Db()
    res=db.select("SELECT `complaints`.*,`passenger`.`first_name`,`passenger`.`last_name` FROM `passenger`,`complaints` WHERE `complaints`.`passenger_id`=`passenger`.`passenger_id`")
    if len(res)>0:
        return render_template('Department/view_complaint.html', data=res)
    else:
        return '<script>alert("No complaints");window.location="/dept_home"</script>'

@app.route('/reply/<id>', methods=['get', 'post'])
def reply(id):
    if request.method=="POST":
        reply=request.form['textarea']
        db=Db()
        db.update("UPDATE complaints SET reply='"+reply+"' WHERE complaint_id='"+id+"'")
        return "<script>alert('Reply sent');window.location='/dept_compl_view';</script>"
    return render_template('Department/send_reply.html',cid=id)


@app.route('/dept_reply_send',methods=['post'])
def dept_reply_send():
   db=Db()
   cid=request.form['cid']
   reply=request.form['textarea']
   db.update("UPDATE `complaints` SET `reply`='"+reply+"' WHERE `complaint_id`='"+cid+"'")
   return redirect("/dept_compl_view")

@app.route('/dept_help_request')
def dept_help_request():
    db=Db()
    res=db.select("SELECT `help_request`.*,`passenger`.* FROM `passenger`,`help_request` WHERE `help_request`.`passenger_id`=`passenger`.`passenger_id` AND `help_request`.`status`='pending'")
    if len(res)>0:
        return render_template("Department/view_help_request.html",data=res)
    else:
        return '<script>alert("No data");window.location="/dept_home"</script>'

@app.route('/dept_allocate_request/<id>', methods=['get', 'post'])
def dept_allocate_request(id):
    if request.method=="POST":
        staffid=request.form['select']
        db=Db()
        db.update("UPDATE `help_request` SET `status`='allocated', staff_id='"+staffid+"' WHERE `help_request_id`='"+id+"'")
        return '<script>alert("Updated");window.location="/dept_help_request"</script>'
    else:
        db=Db()
        res=db.select("SELECT * FROM staffs WHERE department_id='"+str(session['lid'])+"' AND staff_id NOT IN (SELECT staff_id FROM `help_request` WHERE STATUS = 'allocated')")
        return render_template("department/allocate_request.html", data=res)






##########################################################              SHOP
@app.route("/shop_home")
def shop_home():
    return render_template("shop/shop_home.html")

@app.route("/shop_view_profile")
def shop_view_profile():
    db=Db()
    res=db.selectOne("SELECT * FROM shops, buildings WHERE shops.building_id=buildings.building_id and shop_id='"+str(session['lid'])+"'")
    return render_template("shop/view_profile.html", data=res)

@app.route("/shop_add_product", methods=['get', 'post'])
def shop_add_product():
    if request.method=="POST":
        pname=request.form['textfield']
        descr=request.form['textarea']
        amt=request.form['textfield2']
        fileField=request.files['fileField']
        fname=time.strftime("%Y%m%d_%H%M%S")+".jpg"
        fileField.save(static_path + "product\\" + fname)
        path="/static/product/" + fname
        db=Db()
        db.insert("INSERT INTO product(product_name, description, image, amount, shop_id) VALUES('"+pname+"', '"+descr+"', '"+path+"', '"+amt+"', '"+str(session['lid'])+"')")
        return "<script>alert('Product added');window.location='/shop_add_product';</script>"
    return render_template("shop/add_product.html")

@app.route("/shop_view_products")
def shop_view_products():
    db=Db()
    res=db.select("SELECT * FROM product WHERE shop_id='"+str(session['lid'])+"'")
    return render_template("shop/view_product.html", data=res)

@app.route("/shop_delete_product/<pid>")
def shop_delete_product(pid):
    db=Db()
    db.delete("delete from product where product_id='"+pid+"'")
    return redirect("/shop_view_products")






#####################################################           STAFF
@app.route("/staff_home")
def staff_home():
    return render_template("staff/staff_home.html")

@app.route("/staff_view_profile")
def staff_view_profile():
    lid=session['lid']
    db=Db()
    res = db.selectOne(
        "SELECT * FROM `staffs`, `department` WHERE department.department_id=staffs.department_id AND staffs.staff_id='" + str(
            lid) + "'")
    return render_template("staff/view_profile.html", data=res)

@app.route("/staff_view_assigned_work")
def staff_view_assigned_work():
    db=Db()
    res=db.select("SELECT * FROM works WHERE staff_id='"+str(session['lid'])+"'")
    return render_template("staff/view_allocated_work.html", data=res)

@app.route("/staff_update_work_status/<wid>", methods=['get', 'post'])
def staff_update_work_status(wid):
    if request.method=="POST":
        narr=request.form['textarea']
        db=Db()
        db.insert("INSERT INTO `work_status`(work_id, DATE, TIME, narration) VALUES('"+wid+"', CURDATE(), CURTIME(), '"+narr+"')")
        return "<script>alert('Work status updated');window.location='/staff_view_assigned_work';</script>"
    return render_template("staff/update_work_status.html")

@app.route("/staff_work_completed/<wid>")
def staff_work_completed(wid):
    db=Db()
    db.update("update works set status='Completed' where work_id='"+wid+"'")
    return redirect("/staff_view_assigned_work")


@app.route("/staff_view_previous_work")
def staff_view_previous_work():
    db=Db()
    res=db.select("SELECT * FROM works WHERE status='Completed' and staff_id='"+str(session['lid'])+"'")
    return render_template("staff/view_previous_work.html", data=res)

@app.route("/staff_view_reports/<wid>")
def staff_view_reports(wid):
    db=Db()
    res=db.select("SELECT * FROM work_status WHERE work_id='"+wid+"'")
    return render_template("staff/view_work_reports.html", data=res)

@app.route("/staff_view_allocated_request")
def staff_view_allocated_request():
    db=Db()
    res=db.select("SELECT `help_request`.*, passenger.first_name, passenger.last_name, passenger.phone FROM passenger, help_request WHERE passenger.passenger_id=help_request.passenger_id AND help_request.staff_id='"+str(session['lid'])+"' AND help_request.status='allocated'")
    return render_template("staff/view_allocated_request.html", data=res)

@app.route("/staff_update_help_request/<rid>")
def staff_update_help_request(rid):
    db=Db()
    db.update("update help_request set status='Completed' where help_request_id='"+rid+"'")
    return redirect("/staff_view_allocated_request")



############################################        ANDROID
@app.route("/and_reg", methods=['post'])
def and_reg():
    fname=request.form['fname']
    lname=request.form['lname']
    hname=request.form['hname']
    place=request.form['plc']
    passport=request.form['passport']
    phn=request.form['phn']
    email=request.form['email']
    psw=request.form['pass']
    db=Db()
    lid=db.insert("INSERT INTO login(username, PASSWORD, user_type) VALUES('"+email+"', '"+psw+"', 'user')")
    db.insert("INSERT INTO passenger VALUES('"+str(lid)+"', '"+fname+"', '"+lname+"', '"+hname+"', '"+place+"', '"+phn+"', '"+email+"', '"+passport+"')")
    return jsonify(status="ok")

@app.route('/and_login', methods=['post'])
def and_login():
    user = request.form['username']
    psw = request.form['password']
    db = Db()
    res = db.selectOne("SELECT * FROM `login` WHERE `username`='" + user + "' AND `password`='" + psw + "'")
    if res != None:
        type = res['user_type']
        lid = res['login_id']
        if type == "user":
            return jsonify(status="ok", lid=lid)
        else:
            return jsonify(status="no")
    else:
        jsonify(status="inv")


@app.route("/and_view_profile", methods=['post'])
def and_view_profile():
    lid=request.form['lid']
    db=Db()
    res=db.selectOne("SELECT * FROM passenger WHERE passenger_id='"+lid+"'")
    return jsonify(status="ok", fname=res['first_name'], lname=res['last_name'], house_name=res['house_name'], place=res['place'],
                   phone=res['phone'], email=res['email'], passport_no=res['passport_no'])

@app.route("/and_view_service", methods=['post'])
def and_view_service():
    db=Db()
    res=db.select("SELECT * FROM service")
    if len(res)>0:
        return jsonify(status="ok", data=res)
    else:
        return jsonify(status="no")

@app.route("/and_view_schedules", methods=['post'])
def and_view_schedules():
    sid=request.form['sid']
    db=Db()
    res=db.select("SELECT * FROM SCHEDULE WHERE service_id='"+sid+"'")
    if len(res)>0:
        return jsonify(status="ok", data=res)
    else:
        return jsonify(status="no")

@app.route("/and_view_shops", methods=['post'])
def and_view_shops():
    db=Db()
    res=db.select("SELECT * FROM shops")
    if len(res)>0:
        return jsonify(status="ok", data=res)
    else:
        return jsonify(status="no")

@app.route("/and_view_products", methods=['post'])
def and_view_products():
    sid=request.form['shopid']
    db=Db()
    res=db.select("SELECT * FROM product WHERE shop_id='"+sid+"'")
    if len(res)>0:
        return jsonify(status="ok", data=res)
    else:
        return jsonify(status="no")


@app.route("/and_view_request_status", methods=['post'])
def and_view_request_status():
    lid=request.form['lid']
    db=Db()
    res=db.select("SELECT * FROM help_request WHERE passenger_id='"+lid+"'")
    if len(res)>0:
        return jsonify(status="ok", data=res)
    else:
        return jsonify(status="no")

@app.route("/and_delete_request", methods=['post'])
def and_delete_request():
    rid=request.form['rid']
    db=Db()
    db.delete("DELETE FROM help_request WHERE help_request_id='"+rid+"'")
    return jsonify(status="ok")

@app.route("/and_send_request", methods=['post'])
def and_send_request():
    lid=request.form['lid']
    details=request.form['details']
    db=Db()
    db.insert("INSERT INTO `help_request`(passenger_id, request_details, DATE, TIME, staff_id, STATUS) VALUES('"+lid+"', '"+details+"', CURDATE(), CURTIME(), '0', 'pending')")
    return jsonify(status="ok")


if __name__ == '__main__':
    app.run(host="0.0.0.0")
