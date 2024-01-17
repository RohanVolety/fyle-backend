from flask import Blueprint
from core.apis import decorators
from core.apis.responses import APIResponse
from core.models.assignments import Assignment, AssignmentStateEnum
from .schema import AssignmentSchema ,AssignmentGradeSchema 
from core import db
from core.models.teachers import Teacher

principal_assignments_resources = Blueprint('principal_assignments_resources', __name__)
principal_teachers_resources = Blueprint('principal_teachers_resources', __name__)

@principal_assignments_resources.route('/assignments', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_principal_assignments(p):
    """Returns list of submitted and graded assignments for the principal"""
    principal_assignments = Assignment.get_assignments_by_teacher(p.principal_id)
    principal_assignments_dump = AssignmentSchema().dump(principal_assignments, many=True)
    return APIResponse.respond(data=principal_assignments_dump)



@principal_teachers_resources.route('/teachers', methods=['GET'], strict_slashes=False)
@decorators.authenticate_principal
def list_teachers(p):
    """List all teachers"""
    teachers = Teacher.query.all()

    teachers_data = [
        {
            "created_at": teacher.created_at.isoformat(),
            "id": teacher.id,
            "updated_at": teacher.updated_at.isoformat(),
            "user_id": teacher.user_id
        }
        for teacher in teachers
    ]

    return APIResponse.respond(data=teachers_data)


@principal_assignments_resources.route('/assignments/grade', methods=['POST'], strict_slashes=False)
@decorators.accept_payload
@decorators.authenticate_principal
def grade_principal_assignment(p, incoming_payload):
    """Grade or re-grade an assignment"""
    grade_assignment_payload = AssignmentGradeSchema().load(incoming_payload)

    graded_assignment = Assignment.get_by_id(grade_assignment_payload.id)

    graded_assignment = Assignment.mark_grade(
        _id=grade_assignment_payload.id,
        grade=grade_assignment_payload.grade,
        auth_principal=p
    )
    
    db.session.commit()
    graded_assignment_dump = AssignmentSchema().dump(graded_assignment)
    response_data = {'data': graded_assignment_dump,
                     'state': graded_assignment.state,
                     'grade':graded_assignment.grade}
    return APIResponse.respond(response_data)
    # return APIResponse.respond({'data': graded_assignment_dump})
