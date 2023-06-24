## Instalation without Docker
1. Update submodules
`git submodule update --init --recursive --remote`
2. Create a new virtual environment
`python -m venv venv`
3. Activate the virtual environment
`source venv/bin/activate`
4. Install the dependencies
`pip install -r requirements.txt
pip install -r ./QuizGeneratorModel/requirements.txt`
5. Prepare and apply migrations
`python manage.py makemigrations
python manage.py migrate`
6. Run the server
`python manage.py runserver`