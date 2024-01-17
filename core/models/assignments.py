import enum
from core import db
from core.apis.decorators import AuthPrincipal
from core.libs import helpers, assertions
from core.models.teachers import Teacher
from core.models.students import Student
from sqlalchemy.types import Enum as BaseEnum

class GradeEnum(str, enum.Enum):
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'

class AssignmentStateEnum(str, enum.Enum):
    DRAFT = 'DRAFT'
    SUBMITTED = 'SUBMITTED'
    GRADED = 'GRADED'

class Assignment(db.Model):
    __tablename__ = 'assignments'
    id = db.Column(db.Integer, db.Sequence('assignments_id_seq'), primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey(Student.id), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey(Teacher.id), nullable=True)
    content = db.Column(db.Text)
    grade = db.Column(BaseEnum(GradeEnum))
    state = db.Column(BaseEnum(AssignmentStateEnum), default=AssignmentStateEnum.DRAFT, nullable=False)
    created_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False)
    updated_at = db.Column(db.TIMESTAMP(timezone=True), default=helpers.get_utc_now, nullable=False, onupdate=helpers.get_utc_now)

    # def __repr__(self):
    #     return '<Assignment %r>' % self.id

    @classmethod
    def filter(cls, *criterion):
        db_query = db.session.query(cls)
        return db_query.filter(*criterion)

    @classmethod
    def get_by_id(cls, _id):
        return cls.filter(cls.id == _id).first()

    @classmethod
    def upsert(cls, assignment_new: 'Assignment'):
        assignment = Assignment.get_by_id(assignment_new.id)
        if assignment:
            assertions.assert_found(assignment, f'No assignment with ID {assignment_new.id} was found')
            assertions.assert_valid(assignment.state == AssignmentStateEnum.DRAFT,
                                    'Only assignments in draft state can be edited')
            assignment.content = assignment_new.content
        else:
            assignment = assignment_new
            db.session.add(assignment)

        db.session.flush()
        return assignment

    @classmethod
    def submit(cls, _id, teacher_id, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, f'No assignment with ID {_id} was found')
        assertions.assert_valid(assignment.student_id == auth_principal.student_id, 'This assignment belongs to another student')
        assertions.assert_valid(assignment.content is not None, 'Assignment with empty content cannot be submitted')

        assignment.teacher_id = teacher_id
        assignment.state = AssignmentStateEnum.SUBMITTED
        db.session.flush()

        return assignment

    @classmethod
    def mark_grade(cls, _id, grade, auth_principal: AuthPrincipal):
        assignment = Assignment.get_by_id(_id)
        assertions.assert_found(assignment, f'No assignment with ID {_id} was found')
        assertions.assert_valid(grade is not None, 'Assignment with empty grade cannot be graded')

        # if assignment.state == AssignmentStateEnum.DRAFT:
        #     raise ValueError('Cannot-grade a Draft assignment.')

        assignment.grade = grade
        assignment.state = AssignmentStateEnum.GRADED
        db.session.flush()

        return assignment

    @classmethod
    def get_assignments_by_student(cls, student_id):
        return cls.filter(cls.student_id == student_id).all()
    
    @classmethod
    def exists(cls, assignment_id):
        """Checks if an assignment with the given ID exists."""
        return db.session.query(db.exists().where(cls.id == assignment_id)).scalar()
    
    @classmethod
    def can_grade(cls, assignment_id, teacher_id):
        """Checks if a teacher is authorized to grade an assignment."""
        assignment = cls.query.get(assignment_id)

        # Check if assignment exists
        if assignment:
            # Fetch the Teacher instance corresponding to teacher_id
            teacher = Teacher.query.get(teacher_id)

            # Check if teacher exists and other conditions for grading authorization
            if teacher and assignment.state != AssignmentStateEnum.DRAFT and assignment.teacher_id == teacher.id:
                return True

        return False

    @classmethod
    def is_draft_assignment(cls, assignment_id):
        """Checks if an assignment is in draft state."""
        assignment = cls.get_by_id(assignment_id)

        # Check if the assignment exists
        # if not assignment:
        #     raise ValueError(f'No assignment with ID {assignment_id} was found')

        return assignment.state == AssignmentStateEnum.DRAFT

    
    @classmethod
    def get_assignments_by_teacher(cls, teacher_id):
        """
        Returns all assignments (including submitted and graded) for the given teacher.

        Parameters:
        - teacher_id (int): The ID of the teacher.

        Returns:
        - List[Assignment]: List of assignments for the teacher.
        """
        return cls.filter(
            (cls.teacher_id == teacher_id) & (
                (cls.state == AssignmentStateEnum.SUBMITTED) | (cls.state == AssignmentStateEnum.GRADED)
            )
        ).all()
    
 
    