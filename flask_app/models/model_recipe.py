from flask_app.config.mysqlconnection import connectToMySQL
from flask_app import app_database, app, bcrypt
from flask_app.models import model_user
from flask import flash, session


class Recipe:

    def __init__(self, data):
        self.id = data['id']
        self.created_at = data['created_at']
        self.updated_at = data['updated_at']
        self.name = data['name']
        self.description = data['description']
        self.instructions = data['instructions']
        self.date = data['date']
        self.under_30 = data['under_30']
        self.user_id = data['user_id']
        self.user_info = {}

# ------------------------------ validate recipe ----------------------------- #
    @staticmethod
    def validate_recipe(form):

        is_valid = True

        # blank forms 
        if len(form['form_name']) < 1:
            flash('Please complete name field', 'recipe')
            is_valid = False
        if len(form['form_description']) < 1:
            flash('Please complete description field', 'recipe')
            is_valid = False
        if len(form['form_instructions']) < 1:
            flash('Please complete instructions field', 'recipe')
            is_valid = False
        if len(form['form_date']) < 1:
            flash('Please complete date field', 'recipe')
            is_valid = False
        if not (form.get('form_under_30')):
            flash('Please indicate if recipe requires less than 30 minutes', 'recipe')
            is_valid = False
        # required number of characters entered
        if len(form['form_name']) < 3:
            flash('Name must be at least 3 characters in length', 'recipe')
            is_valid = False
        if len(form['form_description']) < 3:
            flash('Description must be at least 3 characters in length', 'recipe')
            is_valid = False
        if len(form['form_instructions']) < 3:
            flash('Instructions must be at least 3 characters in length', 'recipe')
            is_valid = False
        
        return is_valid


# ---------------------------------- create recipe ---------------------------------- #
    @classmethod
    def create_recipe(cls, form):
        #| get data 
        query = """INSERT INTO recipes ( name, description, 
                instructions, date, under_30, user_id )
                VALUES ( %(form_name)s, %(form_description)s, %(form_instructions)s, 
                %(form_date)s, %(form_under_30)s, %(user_id)s );"""
        data = { **form, 'user_id' : session['user_id'] }

        return connectToMySQL(app_database).query_db(query, data)

# -------------------------------- update recipe -------------------------------- #
    @classmethod
    def update_recipe(cls, form):
        #| get data 
        query = """UPDATE recipes 
                SET name = %(form_name)s, description = %(form_description)s, 
                instructions = %(form_instructions)s,
                date = %(form_date)s, under_30 = %(form_under_30)s,
                updated_at = NOW()  
                WHERE id = %(form_id)s;"""
        data = { **form }

        return connectToMySQL(app_database).query_db(query, data)

# ------------------------------- read one recipe ------------------------------- #
    @classmethod
    def read_recipe(cls, pk):
        #| query + create instance
        query = """SELECT * FROM recipes
                LEFT JOIN users on recipes.user_id = users.id
                WHERE recipes.id = %(id)s;
                """
        data = {'id': pk}
        results = connectToMySQL(app_database).query_db(query, data)
        recipe = cls(results[0])

        # create class instance for joined table, add to array
        user_data = {**results[0],
                    'id' : results[0]['users.id'],
                    'created_at' : results[0]['users.created_at'],
                    'updated_at' : results[0]['users.updated_at'],
                    }
        recipe.user_info = ( model_user.User(user_data) )

        return recipe


# ----------------------------- read all recipes ----------------------------- #
    @classmethod
    def read_recipes_with_user(cls):
        #| read data
        query = """SELECT *
                FROM recipes
                LEFT JOIN users on recipes.user_id = users.id 
                ORDER BY recipes.created_at DESC
                """
        results = connectToMySQL(app_database).query_db(query)
        #| create list of dictionaries (rows) from data
        all_rows = []
        for dictionary in results:
            recipe = cls(dictionary)
            user_data = {**dictionary,
                        'id': dictionary['users.id'],
                        'created_at': dictionary['users.created_at'],
                        'updated_at': dictionary['users.updated_at']
                        }
            recipe.user_info = model_user.User(user_data)
            all_rows.append(recipe)

        return all_rows


# ------------------------------ delete recipe ------------------------------ #
    @classmethod
    def delete_recipe(cls, pk):
        
        query = """DELETE FROM recipes
                WHERE id = %(id)s;"""
        data = { 'id' : pk }

        return connectToMySQL(app_database).query_db(query, data)