# College Results Website

This project contains the source code for a responsive website that displays students results and also has an admin interface.

This website was built using Python, Flask, Jinja2, Bootstrap which makes it a complete responsive website.

Students can log in, view their profile, view their results, can change their contact details and password. And when ever a change to password or contact details is done, a mail is sent to the registered mail automatically.

This website also has an admin interface. Admin can view user profies and can make changes if necessary, add students marks to database etc. Admin can add students marks directly to database using excel sheet containing marks of students.

## Table of Contents

* [Requirements](#Requirements)

* [Instalation](#Instalation)

* [Usage](#Usage)
  * [For Students](#For-Students)
  * [For Admins](#For-Admins)
  * [Demo](#Demo)

* [Authors](#Authors)

* [License](#License)

## Requirements

* Python-3

* Flask

* MySQL Server

* Python modules required are mentioned in [requirements.txt](/requirements.txt)

## Instalation

Before hosting the app, make sure the [configuration.cfg](/configuration.cfg) file is filled completly and correctly.
And make sure python-3 is installed and all the required modules are installed. And an MySQL server is required. And run the [database.sql](/database.sql) script on the MySQL database server.

## Usage

### For Students

Students are required to login into the website using their registration number (provided by their institute) and password. For the first time the user's registration number will be their password. Later they are allowed to change it. And they are also allowed to change their Mail id and Phone numbers and Profile pic. And after loging in users are directed to their profile page.
Users can view their results of each semster along with their cpi and spi.

### For Admins

Admin are also required to login to the website using their registration number and password. Admin is allowed to view user profile and edit the user profiles too. But he is not allowed to change the password of an user account. And one of the feature the webiste has is that , it allows admin to directly add student marks in database using excel sheet. But care has to be taken in naming the columns and order of columns in the excel sheet. It should be of the format
|reg|sem|subject_code|grade|credits|
|---|---|------------|-----|-------|

### Demo

![Alt Website Demo Video](/docs/demo.gif)

The GIF shows demo of 2 profiles. First an user interface and then an admin interface.

[Click here to watch HD video on YouTube](https://youtu.be/zZruCSsxXVk)

## Authors

Tiruthani Yeswanth Kumar

## License

This project is licensed under MIT License - For more details read [LICENSE.txt](/LICENSE.txt) file
