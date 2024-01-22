# run with: bash scripts/generate_translations.sh
python manage.py makemessages -l es --ignore=env
python manage.py compilemessages --ignore=env
# TODO: run the translation script 
# TODO: copy locale in any application