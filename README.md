# Employee Evaluation System
===============================

Employee Evaluation System is a piece of software designed for enterprise.
It is used to track employee performance. A task is assigned to an employee, an
evaluator is assigned to the employee. The employee gives updates on his progress
as he works on the assigned task. Once he/she is done, he/she indicates such
on the last progress update. An evaluator finally evaluates the task, recording
details about the evaluation. Such details can be used for analysing an employee's
performance over a specified period fo time, comparing the performance of
multiple employees etc

## Requirements
1. Python >=3.6
2. Git

## Setup
**Nb. This setup works on windows operating system**

```
    c:Users\user>powershell
    PS C:Users\user>cd documents
    PS C:Users\user\documents>mkdir newfolder
    PS C:Users\user\documents\newfolder>git clone https://github.com/anosike-ikenna/employee-evaluator.git
    PS C:Users\user\documents\newfolder>python -m venv virtual
    PS C:Users\user\documents\newfolder>./virtual/scripts/activate
    (virtual) PS C:Users\user\documents\newfolder>cd employee-evaluator
    (virtual) PS C:Users\user\documents\newfolder\employee-evaluator>pip install -r requirements.txt
```

## Database Configuration
```
    (virtual) C:Users\user\documents\newfolder\employee-evaluator>python manage.py makemigrations
    (virtual) C:Users\user\documents\newfolder\employee-evaluator>python manage.py migrate
```

## Running
```
   (virtual) C:Users\user\documents\newfolder\employee-evaluator>python manage.py runserver
```
* Load up your browser and type into the address bar *http://localhost:8000/* 