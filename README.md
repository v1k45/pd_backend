## Britecore Product Development Hiring Project

A system to store and represent generic risk models and their data.

### Approach

Overall idea is to build an Entity-Attribute-Value (EAV) data model to store risk type models. These risk models will be used as schemas to accept data to custom fields.

### TODO: Describe the data models and how things work in the project

### TODO: Describe development setup

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

