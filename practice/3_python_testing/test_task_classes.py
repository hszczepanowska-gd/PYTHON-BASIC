"""
Write tests for classes in 2_python_part_2/task_classes.py (Homework, Teacher, Student).
Check if all methods working correctly.
Also check corner-cases, for example if homework number of days is negative.
"""
import pytest
from datetime import timedelta
module = __import__('2_python_part_2.task_classes', fromlist=['Teacher', 'Student', 'Homework'])
Teacher = module.Teacher
Student = module.Student
Homework = module.Homework


@pytest.fixture()
def homework():
    return Homework(text="Math", days_to_complete=3)

@pytest.fixture()
def expired_homework():
    return Homework(text="Math", days_to_complete=-2)

@pytest.fixture()
def student():
    return Student(last_name='Popov', first_name='Vladislav')

@pytest.fixture()
def teacher():
    return Teacher(last_name='Orlyakov', first_name='Dmitry')

def test_homework_init(homework):
    assert homework.text == "Math"
    assert homework.deadline == timedelta(3)

def test_student_init(student):
    assert student.last_name == 'Popov'
    assert student.first_name == 'Vladislav'

def test_teacher_init(teacher):
    assert teacher.last_name == 'Orlyakov'
    assert teacher.first_name == 'Dmitry'

def test_homework_is_active(homework):
    assert homework.is_active()

def test_homework_is_not_active(expired_homework):
    assert not expired_homework.is_active()
  
def test_create_homework(teacher):
    homework = teacher.create_homework(text="Math", days_to_complete=2)

    assert isinstance(homework, Homework)
    assert homework.text == "Math"
    assert homework.deadline == timedelta(2)
    
def test_do_homework_when_not_expired(homework, student):
    assert student.do_homework(homework=homework) == homework

def test_do_homework_when_expired(expired_homework, student):
    assert student.do_homework(homework=expired_homework) == None