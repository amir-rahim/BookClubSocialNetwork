# Novella Books - Team SEG Fault - SEG Major Group project

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
This project is called `BookClubSocialNetwork`. It currently consists of a single application: `BookClub`, and a recommender module with an evaluator tool as an extra component.

## Deployment Version
Our deployed version is linked [here](https://novella-books.herokuapp.com/) at novella-books.herokuapp.com/.

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

Seed the development database with deployment settings:


```
$ python3 manage.py seed --deploy
```

Seeding the development database with the "--load" option will allow you to choose a percentage of the data set CSVs to pass as a parameter (note: this takes approximately 45 minutes for 100% of the dataset):

```
$ python3 manage.py seed --load [PERCENTAGE]
```

To dictate the amount of clubs, use the --count option:

```
$ python3 manage.py seed --count [COUNT]
```

We would recommend running the following command, unless you wish to load a high percentage of the dataset:

```
python3 manage.py seed --deploy --count 5
```

To remove everything except the Book, User or BookReview objects, run:
```
$ python3 manage.py unseed
```

To remove everything, run:
```
$ python3 manage.py unseed --complete
```

## Creating a Super User

Create a Super User:
```
$ python3 manage.py createsuperuser
```

Please note: this is done in the seeder already.

## AI Commands

Prerequisites for running these commands are that the dependencies, as declared in the requirements.txt file, are installed and that the database has been migrated and seeded already.


###Popularity Recommender

First, you must run the popularity recommender. To train it, you need to run the following command:

```
$ python manage.py train_popularity_recommender [min_ratings_threshold]
```

To train the different algorithms that we have implemented for the AI, you only run one of the following commands for the chosen algorithm.

###Item-Based Recommender

To train the Item Based Recommender, there are two optional parameters "min_ratings_threshold" and "min_support":

```
$ python manage.py train_item_based_recommender [min_ratings_threshold] [min_support]
```

###Content-Based Recommender
To train the Content Based Recommender:
```
$ python manage.py train_content_based_recommender
```
###Parameters
Where "min_ratings_threshold" equals the minimum number of ratings a book needs for it to be included in our recommendation matrix. 
"minimum_support" is the minimum number of user ratings that two books must have in common for their similarity to be greater than 0.

###Evaluator Tool
To run the evaluator tool, there is one command to run for each algorithm:
```
$ python manage.py evaluate_content_based_recommenders

$ python manage.py evaluate_item_based_recommenders

$ python manage.py evaluate_popularity_recommenders
```

This will go through all specified parameters' possibilities and print out the values of the metrics for the given recommender and parameters.

## Testing and Code Coverage

Run all tests with:
```
$ python3 manage.py test
```
Run tests without recommender (quicker):
```
$ python3 manage.py test --exclude-tag=recommenders
```

Set of commands to get code coverage:
```
$ coverage run manage.py test

or

$ coverage run manage.py test --exclude-tag=recommenders
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
