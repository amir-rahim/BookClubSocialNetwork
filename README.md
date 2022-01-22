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

Migrate the database:

```
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`
