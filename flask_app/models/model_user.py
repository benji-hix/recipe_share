from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app_database, app, bcrypt
from flask import flash, session
from flask_app.models import model_recipe

import re
email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')


class User:

    def __init__(self, data):
        self.id = data['id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.email = data['email']
        self.password = data['password']
        self.recipes_list = []

#* ----------------------------- validate register ---------------------------- #
    @staticmethod
    def validate_register(form): 
        # preserve text input fields, clear login text
        session['form_first_name_register'] = form['form_first_name']
        session['form_last_name_register'] = form['form_last_name']
        session['form_email_register'] = form['form_email']
        session['form_email_login'] = ''

        is_valid = True

        #* blank forms
        if len(form['form_first_name']) < 1:
            flash('Please enter first name', 'register')
            is_valid = False
        if len(form['form_last_name']) < 1:
            flash('Please enter last name', 'register')
            is_valid = False
        if len(form['form_email']) < 1:
            flash('Please enter email', 'register')
            is_valid = False
        
        #* first + lst name must be at least 2 characters
        if len(form['form_first_name']) < 1 or len(form['form_last_name']) < 1:
            flash('First name and Last name must be at least 2 characters long', 'register')
            is_valid = False

        #* validate email format + test for unique email 
        query = "SELECT * FROM users WHERE email = %(email)s"
        data = { 'email': form['form_email']}
        unique_fail = connectToMySQL(app_database).query_db(query, data) 
        if not email_regex.match(form['form_email']):
            flash('Invalid email format', 'register')
            is_valid = False
        if unique_fail:
            flash('Email already exists in database', 'register') 
            is_valid = False

        #* confirm password entered and confirmed correctly 
        if len(form['form_password']) < 1 or len(form['form_confirm_password']) < 1:
            flash('Please enter and confirm password', 'register')
            is_valid = False
        if form['form_password'] != form['form_confirm_password']:
            flash('Passwords do not match', 'register')
            is_valid = False
        #* password must have at least 1 uppercase and 1 number, be at least 8 characters
        if not (any(char.isdigit() for char in form['form_password']) 
        and any(char.isupper() for char in form['form_password']) 
        and len(form['form_password']) >= 8):
            flash('Password must be at least 8 characters and contain at least one uppercase letter and one number', 'register')
            is_valid = False

        return is_valid 

#* ------------------------------ validate login ------------------------------ #
    @staticmethod
    def validate_login(form):
        # preserve text input field, clear register text 
        session['form_email_login'] = form['form_email']
        session['form_first_name_register'] = ''
        session['form_last_name_register'] = ''
        session['form_email_register'] = ''
        
        is_valid = True

        #* blank forms
        if len(form['form_email']) < 1:
            flash('Please enter email', 'login')
            is_valid = False
        if len(form['form_password']) < 1:
            flash('Please enter password', 'login')
            is_valid = False

        #* email format
        if not email_regex.match(form['form_email']):
            flash('Invalid email address', 'login')
            is_valid = False

        #! stop early to avoid query issues if invalid text input
        if not is_valid: return is_valid

        #* check if email exists in database
        query = "SELECT * FROM users WHERE email = %(email)s"
        data = { 'email': form['form_email']}
        found_user = connectToMySQL(app_database).query_db(query, data)
        if len(found_user) < 1:
            flash ('Invalid email/password', 'login')
            is_valid = False
            return is_valid #! password only checked if user is found 

        #* check password against hash
        found_user = found_user[0]
        if not bcrypt.check_password_hash(found_user['password'], form['form_password']):
            flash ('Invalid email/password', 'login')
            is_valid = False

        # update session
        if is_valid:
            session['logged_in'] = True
            session['user_id'] = found_user['id']
        return is_valid

#~ ---------------------------------- register ---------------------------------- #
    @classmethod
    def register(cls, form):
        #| generate password hash
        password_hash = bcrypt.generate_password_hash(form['form_password'])
        session['logged_in'] = True

        query = """INSERT INTO users ( first_name, last_name, email, password )
                VALUES ( %(form_first_name)s, %(form_last_name)s, %(form_email)s, %(password)s );"""
        data = {
                **form,
                'password' : password_hash
                }

        return connectToMySQL(app_database).query_db(query, data)

#~ --------------------------------- log in  --------------------------------- #
    @classmethod
    def login(cls, pk):

        query = """SELECT * FROM users
                WHERE id = %(id)s;
                """
        data = {'id': pk}
        results = connectToMySQL(app_database).query_db(query, data)

        return cls(results[0])

#`` -------------------------- read all of one user's recipes -------------------------- #
    @classmethod
    def user_with_recipes(cls, pk):
        query = """SELECT * FROM users
                LEFT JOIN recipes 
                ON users.id = recipes.user_id
                WHERE users.id = %(id)s
                ORDER BY users.updated_at DESC
                """
        data = { 'id' : pk }
        results = connectToMySQL(app_database).query_db(query, data)
        #| create instance for user
        user = cls(results[0])
        #| parse data for each instance of recipe 
        for row in results:
            if row['recipes.id'] == None:
                break
            recipe_data = {**row,
                            'id' : row['recipes.id'],
                            'created_at' : row['recipes.created_at'],
                            'updated_at' : row['recipes.updated_at'],
                            }
            user.recipes_list.append( model_recipe.Recipe(recipe_data) )

        return user 