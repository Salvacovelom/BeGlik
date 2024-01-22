# The deploy to production is the same but changin ci to prod
docker build -t glik-ci .
docker tag glik-ci:latest angelvzla99/glik-ci
docker push angelvzla99/glik-ci
# google cloud console -> cloud run -> glik-ci -> implementar y editar una nueva revisión