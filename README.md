## Britecore Product Development Hiring Project

### Problem Statement

Develop an API backend which allows insurers to define their own custom data model for their risks. There should be no database tables called `automobiles`, `houses`, or `prizes`. Instead, insurers should be able to create their own risk types and attach as many different fields as they would like.

Fields are bits of data like first name, age, zip code, model, serial number, Coverage A limit, or prize dollar amount. Fields can also be of different types, like text, date, number, currency, and so forth.

### Approach

Overall idea is to build an Entity-Attribute-Value (EAV) data model to store risk objects. Risk objects are based on the template/fields specified in risk type objects.

Risk types contain information such as name, description and a list of fields along with their types. These fields will have attributes such as name and field_type. Fields can support 4 datatypes: text, number, date and enum. Enum values (options) are store in a separate column and are linked to field by a m2m relationship.

The risk type is then used as a schema to show a dynamic form to the user based on specified fields. The collected data are stored as "field values". Field values are field:value pairs stored in a same table. Each data type is stored in a seprately column as opposed to a single one.

### The API

While the requirements only mentioned of a risk type list and detail API, this project includes APIs to create/view/delete risk types as well as risk objects. Updating resources is unsupported for both APIs.

The API documentation is generated using docstrings and help text inside code. Swagger is used for documentation UI.

API is live demo at: https://9ijcyflrlc.execute-api.us-east-1.amazonaws.com/prod/api/

API docs: https://9ijcyflrlc.execute-api.us-east-1.amazonaws.com/prod/docs/

Frontend for interacting with the API: http://britecore.v1k45.com/

Note: Frontend does not support creating risk types.

### Development setup

#### Install requirements

```
pip install -r requirements.txt
```

#### Setup environment variables

Create a `.env` file in the project root and insert config values like secret key, debug mode and database URL in it.

An example `.env` file provided with this repository. Check `.env.example` for reference.

#### Migrate database

```
./manage.py migrate
```

#### Run development server

```
./manage.py runserver
```

### Deployment setup
Deployments are done to AWS lambda using Zappa.

#### Initial deployment setup:
A reference `zappa_settings.json` file is included in the repository.

1. Setup AWS account credentials with appropriate permissions and save it in `~/.aws/credentials`
2. Generate initial Zappa config using `zappa init` command.
3. Create a `.production.env` file for production use and include it's name in `zappa_settings.json` as environment variables.
4. Create a database using AWS RDS. Include the subnet ids and security groups in zappa_settings so that AWS Lambda can access the database. Include the database url in  `.production.env` file.
5. Run `zappa manage prod migrate` to migrate the database.
6. Create an S3 bucket which which will be used to store django static files. Include the bucket name in `.production.env` file.
7. Run `export ENV_FILE_NAME=.production.env;./manage.py collectstatic --noinput` to collect all django static files and upload them to s3.
8. Run `zappa deploy prod`. Copy the lambda function link to .env file `ALLOWED_HOSTS` list.
9. Run `zappa update prod` to finally update prod and make it usable.

#### Deploy updates:

Execute `zappa manage prod migrate` if there are any migrations.

Execute `export ENV_FILE_NAME=.production.env;./manage.py collectstatic --noinput` if there are any django static files have changed.

Run `zappa update prod` to deploy code changes in project.

