# glik-backend

## Run the database and backend using docker

Ask for the files **.env** and **gcd_credentials.json** both of them should be in the root of the project. Make sure you have all the variables in the .env.example

Requires Docker

```sh
$ docker-compose up
```

## TODO refactors

- Rename views to controllers
- Create services to each table that use the serializers (the validation is in the views)
- Create repositories for the database querysets
- Rename the urls to use the REST format of urls /user/id/address
- After this, simplify redundant endpoints and add logic to handle general cases

## TODO

- Create a user service with validations
- Create a lease service with all the counts
- Expiration of the tokens (authentication token and forgot password token)
- Create folders in GCP for each user userId/documents

## TODO DEVOPS

- Improve .env of staging/ci, new file to be included in the .gitignore
- Connect to the gcp database in staging/ci
- try to upload the container to gcp (push docker containers to gcp)
- Automate deployment with github actions
