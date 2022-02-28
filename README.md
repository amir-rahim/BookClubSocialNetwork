# Team SEG Fault - Major Group project

## Team members
The members of the team are (alphabetical order):
- Amir Rahim
- Jack Curtis
- Jessy Briard
- Marsha Seen Yee (Marsha) Lau
- Musa (Moose) Ghafoor
- Ravshanbek (Rav) Rozukulov
- Raymond Chung
- Sebastian Malos
- Zafira (Zaf) Shah

## Project structure
The project is called `BookClubSocialNetwork`.  It currently consists of a single app `BookClub`.

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:
```
$ pip3 install -r requirements.txt
```

Make migrations for the database:
```
$ python3 manage.py makemigrations
```

Migrate the database:
```
$ python3 manage.py migrate
```

## Seed and Unseed Commands

Seed the development database with:
```
$ python3 manage.py seed
```

Alternatively, you can specify the number of clubs:
```
$ python3 manage.py seed *int: number*
```

Unseed the development database with:
```
$ python3 manage.py unseed
```

## Creating a Super User

Create a Super User:
```
$ python3 manage.py createsuperuser
```

## Testing and Code Coverage

Run all tests with:
```
$ python3 manage.py test
```

Set of commands to get code coverage:
```
$ coverage run manage.py test
```

To get the results in the command line:
```
$ coverage report
```

To generate a HTML report of the coverage:
```
$ coverage html
```

## Sources
The packages used by this application are specified in `requirements.txt`
