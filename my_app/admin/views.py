from my_app.admin import admin
from .classes import check_admin,MarksExcel,MarksUpdate
from my_app.main.classes import check_login,DBcursor
from flask import render_template,request,current_app,flash
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
import pandas as pd
import os

@admin.route("/update_page")
@check_login
@check_admin
def update_page():
    """Admin can select various types of updates that he/she can do.

    The admin is given various options to update database.
    He is also given option to view user profiles like contact information etc.
    """
    return render_template('admin_update_select.html')

@admin.route('/update_marks_excel', methods = ['GET','POST'])
@check_login
@check_admin
def update_marks_excel():
    """Updates the marks_table from the data in the excel sheet uploaded.
    
    This view functions takes the uploaded excel sheet and adds the values to the marks_table of the database.
    So that the admin is not required to enter each of the records into the database explicitly.

    Note:The uploaded excel sheet should of the format (reg,sem,subject_code,grade,credits).
                                                        ----------------------------------- 
    """
    form = MarksExcel()
    if request.method == 'POST' and form.validate_on_submit():
        sheet = form.excel
        temp_path = os.path.join(current_app.config['UPLOAD_FOLDER'],secure_filename(sheet.data.filename))
        sheet.data.save(temp_path)
        dbu=pd.read_excel(temp_path)
        base_sql = "INSERT INTO marks_table VALUES "
        for x in dbu.values:
            base_sql += str(tuple(x))+','
        base_sql = base_sql[:-1]+";"
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(base_sql)
        os.remove(temp_path)
        flash("Updated database successfully.", category = "success")
        return render_template('admin_update.html', form = form)
    return render_template('admin_update.html', form = form)

@admin.route('/select_db_details', methods = ['GET','POST'])
@check_login
@check_admin
def select_db_details():
    """Select the options that you want to update.
    
    This functions renders a template 'select_details.html' where admin can select what fields he wants to update.
    And after selecting the fields he will be redirected to 'update_details.html' where they enter the details to be updated.
    """
    fields=['name','father_name','DOB','current_sem','mail','phone','nationality','category','religion','caste','blood_group','branch']
    if request.method == 'POST':
        options=request.form.getlist('check')
        if len(options) == 0:
            flash("Atleast one field has to be selected to update Database.", category = "warning")
            return render_template('select_details.html', fields = fields)
        return render_template('update_details.html', fields = options)
    return render_template('select_details.html', fields = fields)

@admin.route("/update_db_details", methods = ['GET','POST'])
@check_login
@check_admin
def update_db_details():
    """Updates the database with the given details.
    
    After entering the details in 'update_details.html', the form is checked if all selected 
    fields are filled. And then the database is updated.

    Later the admin is taken back to 'update_details.html' again with the same fields.This is
    due to the case that the admin may be required to change the same details for each person
    (for eg : While registering students for a new sem).
    """
    if request.method == 'POST':
        base_sql = "UPDATE main_table SET "
        for i in request.form.to_dict().keys():
            base_sql += i+"=%s ,"
        base_sql = base_sql[:-1]+"WHERE reg="+request.form['reg']+";"
        detail_values=[]
        detail_keys=[]
        for i,j in request.form.to_dict().items():
            detail_values.append(j)
            detail_keys.append(i)
        detail_keys.remove('reg')
        if "" in detail_values:
            flash("All fields are required.", category = "warning")
            return render_template('update_details.html', fields = detail_keys)
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(base_sql, tuple(detail_values))
        flash("Updated Database Successfully.", category = "success")
        return render_template('update_details.html', fields = detail_keys)
    return render_template('admin_update_select.html')      

@admin.route('/update_db_marks', methods = ['GET','POST'])
@check_login
@check_admin
def update_db_marks():
    """Updates students marks, if there was a mistake.
    
    The admin is required to enter the registration number of the student,subject code, correct grade and credits.
    """
    form = MarksUpdate()
    if request.method == 'POST' and form.validate_on_submit():
        base_sql="UPDATE marks_table SET grade=%s,credits=%s WHERE reg=%s AND sem=%s AND subject_code=%s"
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(base_sql,(request.form['grade'], request.form['credit'], request.form['reg'], request.form['sem'], request.form['sub_code']))
        flash("Updated Database Successfully.", category = "success")
        return render_template('update.html', form = form)
    return render_template('update.html', form = form)

@admin.route('/add_db_student', methods = ['GET','POST'])
@check_login
@check_admin
def add_db_student():
    """Adds a new user to the database.
    
    This function is used to add a new user to database.
    Initially the registration number is the password of the users.
    But they  are allowed to change their passwords by logging into website with their registration number as their password.
    """
    fields = ['name','father_name','DOB','current_sem','mail','phone','nationality','category','religion','caste','blood_group','branch']
    if request.method == 'POST':
        base_sql = "INSERT INTO main_table (reg,password,name,father_name,DOB,current_sem,mail,phone,nationality,category,religion,caste,blood_group,branch) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(base_sql,(request.form['reg'], generate_password_hash(request.form['reg']), request.form['name'], request.form['father_name'], request.form['DOB'], request.form['current_sem'], request.form['mail'], request.form['phone'], request.form['nationality'], request.form['category'], request.form['religion'], request.form['caste'], request.form['blood_group'], request.form['branch']))
        flash("Inserted User successfully into Database.", category = "success")
        return render_template('insert_user.html', fields = fields)
    flash("Make sure the user is not already present in the database.", category = "info")
    return render_template('insert_user.html', fields = fields)

@admin.route('/remove_db_student', methods = ['GET','POST'])
@check_login
@check_admin
def remove_db_student():
    """Removes an user completly from the database.
    
    This function is used to delete all the records of the user from both the main table as well as the marks table.
    A warning is also displayed to first remove the user as admin, in case if the user who is going to be deleted is an admin.
    """
    if request.method == 'POST':
        base_sql = "DELETE FROM main_table WHERE reg=%s"
        base_sql2 = "DELETE from marks_table WHERE reg=%s"
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(base_sql2,(request.form['reg'],))
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(base_sql, (request.form['reg'],))
        flash("Removed user successfully.", category = "success")
        flash("Make sure the user you want to remove from database exists in database.", category = "warning")
        return render_template('remove.html', title = "Remove an User")
    flash("Make sure the user you want to remove from database exists in database.", category = "warning")
    flash("Before you delete admin details first remove him/her as admin.", category = "info")
    return render_template('remove.html', title = "Remove an User")

@admin.route('/update_db_admin', methods = ['GET','POST'])
@check_login
@check_admin
def update_db_admin():
    """Makes an user admin or removes an admin.
    
    This function is used to remove admin status of an admin.
    And this is also used to make an user an admin.
    """
    if request.method == 'POST':
        if request.form['option'] == 'ADD' and request.form["reg"]:
            base_sql="INSERT INTO admin_table  VALUES (%s);"
        elif request.form['option'] == 'DELETE' and request.form['reg']:
            base_sql="DELETE FROM admin_table WHERE reg=%s;"
        else:
            flash("Atleast one option should be selected, enter a valid Registration number",category = "warning")
            return render_template('add_remove_admin.html')
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(base_sql, (request.form['reg'],))
        flash("Updated Database successfully", category = "success")
        flash("Make sure that the admin being added is alredy an user.", category="info")
        return render_template('add_remove_admin.html')
    flash("Make sure that the admin being added is alredy an user.", category="info")
    return render_template('add_remove_admin.html')

@admin.route('/view_user_profile', methods = ['GET','POST'])
@check_login
@check_admin
def view_user_profile():
    """Admin can view user profiles.
    
    This function is used by the admin to view user profiles.
    And an update button is displayed below the user profiles, so the admin can make changes to profile.
    """
    if request.method == 'POST':
        if (request.form['reg'] == ""):
            flash("Registration number field is mandatory", category="warning")
            return render_template('remove.html', title = "View an User profile")
        base_sql = "SELECT * FROM main_table WHERE reg=%s;"
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(base_sql, (request.form['reg'],))
            user_data = cursor.fetchone()
        if not user_data:
            flash("Enter a valid registration number.", category="warning")
            return render_template('remove.html', title = "View an User profile")
        user_img=os.path.join(current_app.config['RELATIVE_FOLDER'], request.form['reg']+'.jpg')
        return render_template('profile.html', user_image = user_img, name = user_data[2], reg = user_data[0], branch = user_data[13], sem = (user_data[5] if int(user_data[5]) !=9 else "Passed Out"), DOB = user_data[4], father = user_data[3], mail = user_data[6], phone = user_data[7])
    return render_template('remove.html', title = "View an User profile")