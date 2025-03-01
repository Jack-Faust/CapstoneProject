# Cocky Calendar
Our in-app experience allows users to see a calendar of events on/off campus alongside a calendar/planner of tasks concerning work, extracurriculars, and classes. This way, students can stay informed about campus events and stay on top of their coursework.

## External Requirements


## Setup
For this project we are running our code using pipenv and pipfiles. 
To setup pipenv on local computers navigate to the stajj2 repository and run:
```
sudo -H pip install -U pipenv
```
Then to activate pip virtual environment run:
```
pipenv shell
```
Then to run code:
```
python3 manage.py runserver
```


## Running

run from STAJJ/todolistComplete/todolist directory using command:
```
 $ python3 manage.py runserver
 ```
For MacOS and Linux:
```
 $ python manage.py runserver
 ```
It can be accessed locally at http://127.0.0.1:8000/

# Deployment

Deployed using Heroku found at link:
https://deploying-stajj.herokuapp.com/

# Testing

The unit tests are in users/tests.py, cockycal/tests.py, and cal/tests.py.
To run all unit tests, use the command: python3 manage.py test 

The behavioral tests are in /test/behavior.
To run the behavioral test:
1. Open the Command prompt and check if node.js and npm are installed
2. Install selenium-side-runner using the following command: npm install -g selenium-side-runner
3. Next, install the web driver to successfully run the selenium SIDE runner. For Chrome, users will need Chromedriver, for Firefox they need Geckodriver, for Edge they need Edgedriver, for IE it will be IEdriver, and for Safari it will be Safaridriver. use the following command to install the driver: npm install -g chromedriver
4. To run a test case or test suite in the Selenium SIDE runner, use the following command:selenium-side-runner /path/to/filename.side


## Testing Technology

For the behavioral tests, go to 'https://www.selenium.dev/selenium-ide/' and download the 'Selenium IDE' extension to Chrome.

## Running Tests

For the behavioral tests, we are using the Selenium IDE extension from Chrome. Using this IDE, we select the behavioral test we would like to run and, finally, click the 'run all tests' button. In our testing video, we will demonstrate running these behavioral tests using the command line runner. 
To run the behavioral test with the command line runner:
1. Open the Command prompt and check if node.js and npm are installed
2. Install selenium-side-runner using the following command: npm install -g selenium-side-runner
3. Next, install the web driver to successfully run the selenium SIDE runner. For Chrome, users will need Chromedriver, for Firefox they need Geckodriver, for Edge they need Edgedriver, for IE it will be IEdriver, and for Safari it will be Safaridriver. use the following command to install the driver: npm install -g chromedriver
4. To run a test case or test suite in the Selenium SIDE runner, use the following command:selenium-side-runner /path/to/filename.side

For the unit tests, run the following command to run the all the unit tests across our project.

For MacOS and Linux:
```
python3 manage.py test
```
For Windows:
```
python manage.py test
```

# Authors

Tom Crookes tcrookes@email.sc.edu
Ronald Faust rjfaust@email.sc.edu
Joe Foray jforay@email.sc.edu
Sarah Carlucci carluccs@email.sc.edu
Anne Tumlinm atumlin@email.sc.edu
