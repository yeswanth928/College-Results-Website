#This file contains view functions and error handlers.

from my_app.main.classes import LoginForm, ForgotPasword, DBcursor, PasswordForm, MailForm, PhoneForm, ImageForm, sendmail_asynchroously, check_login
from flask import request, session, redirect, render_template, url_for, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import RequestEntityTooLarge
from random import choice, randint
from my_app.main import main
import string
import os

@main.route('/', methods = ['POST','GET'])
@main.route('/login',methods = ['POST','GET'])
def login_user():
    """The purpose of this view function is to check if the enetered registration number and password exists in a database.
    
    If the details match and the user is an admin then he is redirected to the update_page where he can make changes.
    If the details match and the user is not an admin,the user is logged in and redirected to the user profile page.
    Else it will display the login form again and the user is not allowed to visit rest of the website.
    """
    form=LoginForm()
    if request.method =='POST' and form.validate_on_submit():
        name1 = form.user_na.data
        pass1 = form.user_psw.data
        _sql1 = "SELECT password FROM main_table WHERE reg=%s;"
        _sql2 = "SELECT reg FROM admin_table WHERE reg=%s;"
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(_sql1,(form.user_na.data,))
            user_data1 = cursor.fetchone()
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(_sql2,(form.user_na.data,))
            user_data2 = cursor.fetchone()
        if check_password_hash(user_data1[0], form.user_psw.data) and user_data2:
            session['name'] = name1
            session['admin'] = True
            return redirect(url_for('main.profile_page'))
        elif check_password_hash(user_data1[0], form.user_psw.data):
            session['name'] = name1
            session['admin'] = False
            return redirect(url_for('main.profile_page'))
        else:
            flash("Please enter the correct password", category="danger")
            return render_template('login.html', form=form, disp = True)
    return render_template('login.html', form=form, disp = True)



@main.route('/forgot_password', methods = ['POST', 'GET'])
def forgot_password():
    """This function is used when a user forgets his password.
    
    This function sends a new temporary password to user via mail.
    And the user can change the password later.
    """
    form = ForgotPasword()
    session.clear()
    if request.method == "POST":
        _sql2 = "SELECT mail FROM main_table WHERE reg=%s;"
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(_sql2,(form.user_na.data,))
            user_data2 = cursor.fetchone()
        if not user_data2:
            flash("Please enter a valid Registration number and then press Forgot Password", category = "info")
            return render_template('login.html', form = form, disp = False)    
        characters=string.ascii_letters+string.digits+"#@$~!_%"
        pass_string="".join(choice(characters) for i in range(randint(8,19)))
        _sql="UPDATE main_table SET password=%s WHERE reg=%s;"
        with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
            cursor.execute(_sql,(generate_password_hash(pass_string),form.user_na.data))
        sendmail_asynchroously(to = [user_data2[0]], subject = "password has been updated", message = "", template="Your temporary password is :<strong>"+pass_string+"</strong>")
        flash("A temporary password has been sent to your registererd Mail address. Login with the password.", category="success")
        flash("Incase of any trouble contact adminstration.",category="info")
        return render_template('login.html', form = form, disp = False)
    return render_template('login.html', form = form, disp = False)



@main.route('/profile')
@check_login
def profile_page():
    """This view function is for the Profile page of the user.
    
    This function loads the details of the user from the database, sends the details to the profile.html template .So that it can display the user profile.
    This function also sets some session variables that can be used by other view functions.
    """
    _sql = "SELECT * FROM main_table WHERE reg=%s;"
    with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
        cursor.execute(_sql,(session['name'],))
        user_data = cursor.fetchone() 
    session['mail'] = user_data[6]  #we are setting session variables.
    if not session['admin']:
        session['current_sem'] = int(user_data[5])
    session['password'] = user_data[1]
    user_img=os.path.join(current_app.config['RELATIVE_FOLDER'], session['name']+'.jpg')
    return render_template('profile.html', user_image=user_img, name=user_data[2], reg=user_data[0], branch=user_data[13], sem=(user_data[5] if(user_data is not None or int(user_data[5]) !=9) else "Passed Out"), DOB=user_data[4], father=user_data[3], mail=user_data[6], phone=user_data[7])


# In this page we will provide links to the sem they want to select 
@main.route('/select_sem')
@check_login
def select_sem():
    """This view function is used to dispaly the select_sem.html page.
    
    The user selects the particular sem for which he wants to view his results.
    """
    return render_template('select_sem.html',sem=session['current_sem'])


@main.route('/results/<sem>',methods=['GET'])
@check_login
def results(sem):
    """This is used to display the selected semster's CPI,SPI,grades of that particular sem."""

    _sql = "SELECT sem,subject_code,grade,credits FROM marks_table WHERE reg=%s AND sem < %s"
    with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
        cursor.execute(_sql,(session['name'], session['current_sem']))
        user_data = cursor.fetchall()
    current_sem_list = []
    num1,num,den,den1,cpi,spi = [0.0,0.0,0.0,0.0,0.0,0.0]
    for row in user_data:
        if row[0]<=int(sem):
            num += row[2]*row[3]
            den += row[3]
            if int(sem) == row[0]:
                num1 += row[2]*row[3]
                den1 += row[3]
                current_sem_list.append((row[1], row[2], row[3]))
    spi = round(num1/den1,2)
    cpi = round(num/den,2)
    return render_template('display_results.html',sem_list=current_sem_list,cpi=cpi,spi=spi,sem=sem)

# Now we will write a function to display the contacts page
@main.route('/contact')
@check_login
def contact():
    """Used to display the contact page.
    
    When a user clicks help or feedback button the mail address and subject columns are automatically filled in users mail.
    He is only required to fill body and send it.
    """
    return render_template('contact.html', mail="mailto:"+current_app.config['MAIL_USERNAME']+"?subject=") 

#Now we will write a view function to update user details.
@main.route('/update_select', methods = ['POST','GET'])
@check_login
def update_details():
    """This view functions displays a page where the user can select what to update from options available."""

    return render_template('select_update.html')

@main.route('/update_mail', methods = ['POST','GET'])
@check_login
def update_mail():
    """Updtaes user mail id.
    
    If the password entered matches then the mail is updated.
    Then a mail is sent both to old and new mail describing that the mail has been updated with the new mail id.
    """
    form=MailForm()
    if request.method =="POST" and form.validate_on_submit():
        if check_password_hash(session['password'], form.user_psw.data):
            _sql = "UPDATE main_table SET mail=%s WHERE reg=%s;"
            with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
                cursor.execute(_sql,(form.new_mail.data,session['name']))
            sendmail_asynchroously(to = [form.new_mail.data,session['mail']], subject = "Mail ID has been updated", message = "Your mail id has been changed to "+form.new_mail.data+" if you didn't do it please contact adminstration.")
            flash("Updated mail id successfully",category = "success")
            session['mail']=form.new_mail.data
            return redirect(url_for('main.update_details'))
        else:
            flash("Please enter your current password,The password entered doesn't match", category = "danger")
    return render_template('update.html', form=form, disp = True)
            
@main.route('/update_phone', methods = ['POST','GET'])
@check_login
def update_phone():
    """Updates user phone number.
    
    If the password entered matches then the phone number is updated.
    Then a mail is sent to the mail id of the user describing  the phone number has been changed along with the new phone number.
    """
    form=PhoneForm()
    if request.method == "POST" and form.validate_on_submit():
        if check_password_hash(session['password'],form.user_psw.data):
            _sql = "UPDATE main_table SET phone=%s WHERE reg=%s;"
            with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
                cursor.execute(_sql,(form.new_phone.data,session['name']))
            sendmail_asynchroously(to = [session['mail']], subject = "Phone Number has been updated", message = "Your phone number has been changed to "+form.new_phone.data+" if you didn't do it please contact adminstration.")
            flash("Updated phone number successfully", category = "success")
            return redirect(url_for('main.update_details'))
        else:
            flash("Please enter your current password,The password entered doesn't match", category = "danger")
    return render_template('update.html', form = form, disp = True)

@main.route('/update_password', methods = ['POST','GET'])
@check_login
def update_password():
    """Updates user login password.
    
    In this the user is required to enter the new password of string length 8 to 20 . And the user is asked to reenter the same password to make sure that he entered what he was typing.
    Then a mail is sent to registered mail of the user.
    """
    form=PasswordForm()
    if request.method == "POST" and form.validate_on_submit():
        if check_password_hash(session['password'], form.user_psw.data):
            _sql="UPDATE main_table SET password=%s WHERE reg=%s;"
            with DBcursor(**current_app.config['DATABASE_CONNECTIVITY']) as cursor:
                cursor.execute(_sql,(generate_password_hash(form.new_pass.data), session['name']))
            sendmail_asynchroously(to = [session['mail']], subject = "password has been updated", message = "Your Password has been changed , if you didn't do it please contact adminstration.")
            flash("Updated Password successfully", category = "success")
            return redirect(url_for('main.logout'))
        else:
            flash("Please enter your current password,The password entered doesn't match", category = "danger")
    return render_template('update.html', form = form, disp = True)

@main.route('/update_pic', methods = ['POST','GET'])
@check_login
def update_pic():
    """Updates the user profile pic.
    
    Note that the file uoloaded size can not exceed MAX_CONTENT_LENGTH of configuration file.
    If the file uploaded size exceeds limit then, 413 error is raised ,and a custom error page is displayed.
    And only jpg,png and jpeg files are allowed to be uploaded.
    """
    form=ImageForm()
    if request.method=='POST' and form.validate_on_submit():
        file=form.photo
        if os.path.exists(os.path.join(os.getcwd(),session['name']+'.jpg')):
            os.remove(os.path.join(os.getcwd(),session['name']+'.jpg'))
        file.data.save(os.path.join(current_app.config['UPLOAD_FOLDER'],session['name']+'.jpg'))
        return redirect(url_for('main.update_details'))
    flash("The maximum file upload size is 8MB", category = "info")
    return render_template('update.html', form = form)


@main.route('/logout')
@check_login
def logout():
    """Logs out the user and clears all the session variables."""

    session.clear()
    return redirect(url_for('main.login_user'))

#Now we will create custom error handlers
@main.app_errorhandler(404)
@check_login
def not_found(e) -> 'template':
    """Displays a custom 404 error handler page."""

    return render_template('error_handler.html', code = 404, message = "The file you requested is not found", url = url_for('main.profile_page'), back_to = 'Profile Page'), 404

@main.app_errorhandler(500)
@check_login
def server_prob(e) -> 'template':
    """Displays a custom 500 error handler page."""

    return render_template('error_handler.html', code = 500, message = "Internal Server Error", url = url_for('main.profile_page'), back_to = 'Profile Page'), 500

@main.app_errorhandler(413)
@main.app_errorhandler(RequestEntityTooLarge)
@check_login
def large_file(e) -> 'template':
    """Displays a custom 413 error handler page."""

    return render_template('error_handler.html', code = 413, message = "The file you uploaded was too large to upload", url = url_for('main.update_pic'), back_to = 'Update Pic'), 413

@main.app_errorhandler(400)
@check_login
def bad_request(e) -> 'template':
    """Displays a custom 400 error handler page."""

    return render_template('error_handler.html', code = 400, message = "Bad request", url = url_for('main.profile_page'), back_to = 'Profile Page'), 400 