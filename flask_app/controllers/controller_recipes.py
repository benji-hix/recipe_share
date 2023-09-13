from flask_app import app
from flask import render_template, redirect, request, session, flash
from flask_app.models import model_recipe, model_user


# ----------------- post-validation, redirect to landing page ---------------- #
@app.route('/recipes')
def all_recipes():
    #| validate user logged in
    if not session['logged_in']: return redirect('/')
    #* insert additional data/class methods

    return render_template('all-recipes.html', user=model_user.User.login(session['user_id']),
                            all_recipes=model_recipe.Recipe.read_recipes_with_user())


# ------------------------------ read one recipe ----------------------------- #
@app.route('/recipes/<int:pk>')
def read_recipe(pk):

    recipe = model_recipe.Recipe.read_recipe(pk)

    return render_template('recipe-view.html', recipe = recipe)


# ---------------------------- create recipe page ---------------------------- #
@app.route('/recipe-create')
def create_recipe():
    
    if not session['logged_in']: return redirect('/')

    return render_template('recipe-create.html')


#* ------------------------------- submit recipe ------------------------------ #
@app.route('/submit-recipe', methods=['POST'])
def submit_recipe():
    

    if not session['logged_in']: return redirect('/') #| validate login
    if not model_recipe.Recipe.validate_recipe(request.form): return redirect('/recipe-create') #| validate recipe

    return redirect('/recipes')


# ----------------------------- update recipe page ----------------------------- #
@app.route('/recipes/edit/<int:pk>')
def update_recipe(pk):

    if not session['logged_in']: return redirect('/') #| validate login
    
    return render_template('recipe-edit.html', recipe = model_recipe.Recipe.read_recipe(pk) )


#* --------------------------- submit recipe update --------------------------- #
@app.route('/submit-update/<int:pk>', methods = ['POST'])
def submit_update(pk):

    if not session['logged_in']:  return redirect('/') #| validate login
    if not model_recipe.Recipe.validate_recipe(request.form): return redirect('/recipes/edit/' + str(pk)) #| validate recipe
    model_recipe.Recipe.update_recipe(request.form)

    return redirect('/recipes')


# ------------------------------ delete recipe ------------------------------ #
@app.route('/recipes/delete/<int:pk>')
def delete_recipe(pk):

    if not session['logged_in']: return redirect('/') #| validate login
    model_recipe.Recipe.delete_recipe(pk)

    return redirect('/recipes')


# ------------------------------ delete recipe ------------------------------ #
@app.route('/recipes/user/delete/<int:pk>')
def delete_user_recipe(pk):

    if not session['logged_in']: return redirect('/') #| validate login
    model_recipe.Recipe.delete_recipe(pk)

    return redirect('/recipes/user/' + str(session['user_id']))
