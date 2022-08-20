from ast import Try
import os


from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS,cross_origin


from flask_sqlalchemy import SQLAlchemy

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import  requires_auth,AuthError
db=SQLAlchemy()
app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"*": {"origins": "*"}})

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()


# ROUTES

# route to get drinks

@app.route("/drinks", methods=["GET"])
@cross_origin()
@requires_auth(permission='get:drinks')
def getdrinks():
    
    try:
        drinks=Drink.query.all()
        drink = [drinks.long()]
               
        if len(drink) == 0:
            abort(404)
        else:
            return jsonify({
            'success': True,
            'drinks': drink.long()
           })
    except:
        abort(422)       


#----------------implementation of drink-details---------------------------------------

@app.route("/drinks-detail", methods=["GET"])
@cross_origin()
@requires_auth('get:drinks-detail')
def getDetails():
    try:
        drinks=Drink.query.all()
        drink = [drinks.long()]
               
        if len(drink) == 0:
            abort(404)
        else:
            return jsonify({
            'success': True,
            'drinks': drink.long()
           })
    except:
        abort(422)       




#-------------------------- route to save new drink  implementation-------------------------------------


@app.route('/drinks', methods = ["POST"])
@cross_origin(headers=["Content-Type", "Authorization"])
@requires_auth(permission='post:drinks')
def postNewDrink():
    try:
        body = request.get_json()
        new_title = body.get('title', None)
        new_recipe = body.get('recipe', None)

      
        drinks = Drink(
        title=new_title,
        recipe=new_recipe
         )

        
        Drink.insert(drinks)
        
        drink = [drinks.long()]
        return jsonify({
            "success": True,
            "drinks": drink
        })
    except:
        db.session.rollback()
        abort(403)
    finally:
        db.session.close()
        
        


#---------------------implementation of patch/update specific drink ------------------ 


@app.route("/drinks/<int:id>",methods=["PATCH"])
@cross_origin()
@requires_auth('patch:drinks')
def update_drinks():

    drink=Drink.query.get_or_404(id) 
    body = request.get_json()
    drink.title=body.get('title',None)
    drink.recipe.name=body.get('name',None)
    drink.recipe.color=body.get('color',None)
    drink.recipe.parts=body.get('parts',None)
    db.session.commit()
    return jsonify({
        "success":True,
        "drinks":drink
    })



# --------------------implementation of delete specific drink----------------------

@app.route("/drinks/<int:id>", methods=["DELETE"])
@cross_origin()
@requires_auth('delete:drinks')
def delete_drink(id):
    drink=Drink.query.get_or_404(id) 
    Drink.delete(drink)
    return jsonify({
        "success":True,
        "delete":drink.id
    })
    






'''



@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''



@app.errorhandler(400)
def bad_request(error):
    jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request"
        }), 400

@app.errorhandler(404)
def not_found(error):
    jsonify({
        "success": False,
        "error": 404,
        "message": "Request not Found"
        }), 404






'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''



#@app.errorhandler(AuthError)
#def handle_auth_error(ex):
    #return jsonify({
        #"message":"Please provide Authorization token header",
        #"error":ex.error,
        #"status_code":ex.status_code
    #}),401
    



        

@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
        

# @authorize(users=usernames)  we will use this in above codes(routes flask apis) to authorize
