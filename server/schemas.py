from marshmallow import Schema, fields, validates, ValidationError

class ExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    category = fields.Str(required=True)
    equipment_needed = fields.Bool(required=True)

    @validates('name')
    def validate_name(self, value):
        if not value or not isinstance(value, str) or len(value.strip()) == 0:
            raise ValidationError("Exercise name cannot be empty.")

class WorkoutExerciseSchema(Schema):
    id = fields.Int(dump_only=True)
    workout_id = fields.Int(required=True)
    exercise_id = fields.Int(required=True)
    reps = fields.Int(allow_none=True)
    sets = fields.Int(allow_none=True)
    duration_seconds = fields.Int(allow_none=True)
    exercise = fields.Nested(ExerciseSchema, dump_only=True)

    @validates('sets')
    def validate_sets(self, value):
        if value is not None and value < 0:
            raise ValidationError("Sets must be a non-negative integer.")

class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    date = fields.Str(required=True)
    duration_minutes = fields.Int(required=True)
    notes = fields.Str(allow_none=True)
    workout_exercises = fields.List(fields.Nested(WorkoutExerciseSchema), dump_only=True)
    exercises = fields.List(fields.Nested(ExerciseSchema), dump_only=True)

    @validates('duration_minutes')
    def validate_duration(self, value):
        if value <= 0:
            raise ValidationError("Duration in minutes must be greater than zero.")