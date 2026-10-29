from flask import Flask, make_response, request
from flask_migrate import Migrate
from models import db, Exercise, Workout, WorkoutExercise
from schemas import ExerciseSchema, WorkoutSchema, WorkoutExerciseSchema
from marshmallow import ValidationError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

migrate = Migrate(app, db)
db.init_app(app)

# Initialize Schemas
exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
workout_exercise_schema = WorkoutExerciseSchema()

@app.route('/')
def home():
    return make_response({"message": "Welcome to the Workout Tracking API!"}, 200)

# --- WORKOUT ENDPOINTS ---

@app.route('/workouts', methods=['GET'])
def get_workouts():
    workouts = Workout.query.all()
    return make_response(workouts_schema.dump(workouts), 200)

@app.route('/workouts/<int:id>', methods=['GET'])
def get_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return make_response({"error": "Workout not found"}, 404)
    return make_response(workout_schema.dump(workout), 200)

@app.route('/workouts', methods=['POST'])
def create_workout():
    data = request.get_json()
    try:
        validated_data = workout_schema.load(data)
        new_workout = Workout(
            date=validated_data['date'],
            duration_minutes=validated_data['duration_minutes'],
            notes=validated_data.get('notes')
        )
        db.session.add(new_workout)
        db.session.commit()
        return make_response(workout_schema.dump(new_workout), 201)
    except (ValidationError, ValueError) as err:
        return make_response({"errors": err.messages if hasattr(err, 'messages') else str(err)}, 400)

@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    workout = Workout.query.get(id)
    if not workout:
        return make_response({"error": "Workout not found"}, 404)
    
    WorkoutExercise.query.filter_by(workout_id=id).delete()
    db.session.delete(workout)
    db.session.commit()
    return make_response({}, 204)

# --- EXERCISE ENDPOINTS ---

@app.route('/exercises', methods=['GET'])
def get_exercises():
    exercises = Exercise.query.all()
    return make_response(exercises_schema.dump(exercises), 200)

@app.route('/exercises/<int:id>', methods=['GET'])
def get_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)
    return make_response(exercise_schema.dump(exercise), 200)

@app.route('/exercises', methods=['POST'])
def create_exercise():
    data = request.get_json()
    try:
        validated_data = exercise_schema.load(data)
        new_exercise = Exercise(
            name=validated_data['name'],
            category=validated_data['category'],
            equipment_needed=validated_data['equipment_needed']
        )
        db.session.add(new_exercise)
        db.session.commit()
        return make_response(exercise_schema.dump(new_exercise), 201)
    except (ValidationError, ValueError) as err:
        return make_response({"errors": err.messages if hasattr(err, 'messages') else str(err)}, 400)

@app.route('/exercises/<int:id>', methods=['DELETE'])
def delete_exercise(id):
    exercise = Exercise.query.get(id)
    if not exercise:
        return make_response({"error": "Exercise not found"}, 404)
    
    WorkoutExercise.query.filter_by(exercise_id=id).delete()
    db.session.delete(exercise)
    db.session.commit()
    return make_response({}, 204)

# --- WORKOUT EXERCISE (JOIN) ENDPOINT ---

@app.route('/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises', methods=['POST'])
def add_exercise_to_workout(workout_id, exercise_id):
    workout = Workout.query.get(workout_id)
    exercise = Exercise.query.get(exercise_id)
    if not workout or not exercise:
        return make_response({"error": "Workout or Exercise not found"}, 404)

    data = request.get_json() or {}
    try:
        workout_exercise = WorkoutExercise(
            workout_id=workout_id,
            exercise_id=exercise_id,
            reps=data.get('reps'),
            sets=data.get('sets'),
            duration_seconds=data.get('duration_seconds')
        )
        db.session.add(workout_exercise)
        db.session.commit()
        return make_response(workout_exercise_schema.dump(workout_exercise), 201)
    except ValueError as err:
        return make_response({"error": str(err)}, 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)