import os
from flask import Flask, request, render_template, jsonify, flash, abort
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, db_create_all, return_db, ClimbingSpot, Climber, VisitedSpot

app = Flask(__name__)
app.secret_key = os.urandom(32)

setup_db(app)
db = return_db()
db_create_all()

def get_climbing_spots():
    spot =[]
    for climbingspot in ClimbingSpot.query.order_by('id').all():
        spot.append({
            "id" : climbingspot.id,
            "name" : climbingspot.name,
            "location" : climbingspot.location
        })
    spots = {
        "spot" : spot
    }
    return spots

def get_climbers():
    climber = []
    for climb in Climber.query.order_by('id').all():
        visitedspot = []
        for visited in VisitedSpot.query.filter_by(climber_id=climb.id).all():
            climbingspot = ClimbingSpot.query.filter_by(id=visited.climbing_spot_id).one_or_none()
            visitedspot.append(climbingspot.name)
        climber.append({
            "id" : climb.id,
            "name" : climb.name,
            "state" : climb.state,
            "visited_spots" : visitedspot
        })
    climbers = {
        "climber" : climber
    }
    return climbers

@app.route('/')
def index():
    return render_template('home.html')

#=================CLIMBING SPOT ENDPOINTS=================

@app.route('/climbing-spots', methods=['GET'])
@app.route('/api/climbing-spots', methods=['GET'])
def climbing_spots():
    spots = get_climbing_spots()
    if request.path == '/api/climbing-spots':
        return jsonify({
            'success': True,
            'spots': spots
        })
    return render_template('climbing-spots.html', spots=spots)

@app.route('/climbing-spots', methods=['POST'])
@app.route('/api/climbing-spots', methods=['POST'])
def add_climbing_spots():
    error = False
    try:
        name = request.json['name']
        location = request.json['location']

        climbing_spot = ClimbingSpot(name=name, location=location)
        db.session.add(climbing_spot)
        db.session.commit()
        
        spots = get_climbing_spots()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
#        flash('An error occurred. Climbing spot ' + request.json['name'] + ' could not be added.')
        abort(400)
    else:
#        flash('Climbing spot ' + request.json['name'] + ' was successfully added!')
        if request.path == '/api/climbing-spots':
            return jsonify({
                'success': True,
                'spots': spots
            })
        return render_template('climbing-spots.html', spots=spots)

@app.route('/climbing-spots/<int:climbingspot_id>', methods=['PATCH'])
@app.route('/api/climbing-spots/<int:climbingspot_id>', methods=['PATCH'])
def edit_climbingspots(climbingspot_id):
    error = False
    try:
        name = request.json['name']
        location = request.json['location']
        
        climbingspot = ClimbingSpot.query.get(climbingspot_id)
        climbingspot.name = name
        climbingspot.location = location
        db.session.commit()
        
        spots = get_climbing_spots()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
#        flash('An error occurred. Climbing spot ' + request.json['name'] + ' could not be added.')
        abort(400)
    else:
#        flash('Climbing spot ' + request.json['name'] + ' was successfully added!')
        if request.path == '/api/climbing-spots/' + str(climbingspot_id):
            return jsonify({
                'success': True,
                'id': climbingspot_id,
                'name' : name,
                'location' : location
            })
        return render_template('climbing-spots.html', spots=spots)

@app.route('/climbing-spots/<int:climbingspot_id>', methods=['DELETE'])
@app.route('/api/climbing-spots/<int:climbingspot_id>', methods=['DELETE'])
def remove_climbingspots(climbingspot_id):
    error = False
    try:
        climbingspot = ClimbingSpot.query.get(climbingspot_id)
        name = climbingspot.name
        location = climbingspot.location
        db.session.delete(climbingspot)
        db.session.commit()
        
        spots = get_climbing_spots()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
#        flash('An error occurred. Climbing spot ' + request.json['name'] + ' could not be added.')
        abort(400)
    else:
#        flash('Climbing spot ' + request.json['name'] + ' was successfully added!')
        if request.path == '/api/climbing-spots/' + str(climbingspot_id):
            return jsonify({
                'success': True,
                'id': climbingspot_id,
                'name' : name,
                'location' : location
            })
        return render_template('climbing-spots.html', spots=spots)
    
#=================CLIMBER ENDPOINTS=================    
    
@app.route('/climbers', methods=['GET'])
@app.route('/api/climbers', methods=['GET'])
def climbers():
    climbers = get_climbers()
    if request.path == '/api/climbers':
        return jsonify({
            'success': True,
            'climbers': climbers
        })
    return render_template('climbers.html', climbers=climbers)

@app.route('/climbers', methods=['POST'])
@app.route('/api/climbers', methods=['POST'])
def add_climbers():
    error = False
    try:
        name = request.json['name']
        state = request.json['state']
        visited_spots = request.json['visited_spots']

        climber = Climber(name=name, state=state)
        db.session.add(climber)
        db.session.flush()
        for spot_id in visited_spots:
            visitedspots = VisitedSpot(climbing_spot_id=spot_id, climber_id=climber.id)
            db.session.add(visitedspots)
        db.session.commit()
        
        climbers = get_climbers()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
#        flash('An error occurred. Climbing spot ' + request.json['name'] + ' could not be added.')
        abort(400)
    else:
#        flash('Climbing spot ' + request.json['name'] + ' was successfully added!')
        if request.path == '/api/climbers':
            return jsonify({
                'success': True,
                'climbers': climbers
            })
        return render_template('climbers.html', climbers=climbers)

@app.route('/climbers/<int:climber_id>', methods=['PATCH'])
@app.route('/api/climbers/<int:climber_id>', methods=['PATCH'])
def edit_climbers(climber_id):
    error = False
    try:
        name = request.json['name']
        state = request.json['state']
        new_visited_spots = request.json['visited_spots']
        
        climber = Climber.query.get(climber_id)
        climber.name = name
        climber.state = state
        
        old_visited_spots = VisitedSpot.query.filter_by(climber_id=climber_id)
        for new_spot_id in new_visited_spots:
            visited = old_visited_spots.filter_by(climbing_spot_id=new_spot_id).one_or_none()
            if visited == None:
                visitedspots = VisitedSpot(climbing_spot_id=new_spot_id, climber_id=climber_id)
                db.session.add(visitedspots)
        for old_spot in old_visited_spots.all():
            count = 0
            for new_spot in new_visited_spots:
                if old_spot.climbing_spot_id == new_spot:
                    count = count + 1
            if count == 0:
                specific_spot = old_visited_spots.filter_by(climbing_spot_id=old_spot.climbing_spot_id).one_or_none()
                db.session.delete(specific_spot)
        db.session.commit()
        
        climbers = get_climbers()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
#        flash('An error occurred. Climbing spot ' + request.json['name'] + ' could not be added.')
        abort(400)
    else:
#        flash('Climbing spot ' + request.json['name'] + ' was successfully added!')
        if request.path == '/api/climbers/' + str(climber_id):
            return jsonify({
                'success': True,
                'id': climber_id,
                'name' : name
            })
        return render_template('climbers.html', climbers=climbers)    
    
@app.route('/climbers/<int:climber_id>', methods=['DELETE'])
@app.route('/api/climbers/<int:climber_id>', methods=['DELETE'])
def remove_climbers(climber_id):
    error = False
    try:
        visited_spots = VisitedSpot.query.filter_by(climber_id=climber_id)
        for visited_spot in visited_spots.all():
            specific_spot = visited_spots.filter_by(climbing_spot_id=visited_spot.climbing_spot_id).one_or_none()
            db.session.delete(specific_spot)
        
        climber = Climber.query.get(climber_id)
        name = climber.name
        db.session.delete(climber)
        
        db.session.commit()
        
        climbers = get_climbers()
    except:
        db.session.rollback()
        error = True
    finally:
        db.session.close()
    if error:
#        flash('An error occurred. Climbing spot ' + request.json['name'] + ' could not be added.')
        abort(400)
    else:
#        flash('Climbing spot ' + request.json['name'] + ' was successfully added!')
        if request.path == '/api/climbers/' + str(climber_id):
            return jsonify({
                'success': True,
                'id': climber_id,
                'name' : name
            })
        return render_template('climbers.html', climbers=climbers)    
    
#if __name__ == '__main__': 
#    app.run(host='127.0.0.1', port=81, debug=True)
    
if __name__ == '__main__':
    app.run(debug=True)