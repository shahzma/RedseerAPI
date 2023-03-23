### Installation

_Below are the stpes, to installing and setting up your app._

1. Clone the repo
   ```sh
   git clone https://github.com/your_username_/Project-Name.git
   ```
2. Go inside and create virtual environment
   ```
   python -m venv ./venv
   ```
3. Initialize virtual enviroment
   ```
   source venv/bin/activate
   ```
4. Install dependencies using requirements.txt
   ```
   pip3 install -r requirements.txt
   ```

### Running the applications

_Below are the stpes, to run your app._

1. You can set the environment variable in .env or can pass during runtime
2. Run the following command
   ```sh
   DATABASE_URL=<DATABASE_URL> python manage.py runserver 0.0.0.0:<PORT> --noreload
   ```
3. where DATABASE_URL should in format 'mysql://user:pass@localhost:3000/dbname'
4. where PORT will be the port you want to host your project on
