#!/bin/sh

# Apply database migrations
echo "Applying database migrations"
python manage.py migrate || { echo 'migrate failed' ; exit 1; }

# Create superuser
echo "Creating superuser"
python manage.py createsu || { echo 'createsu failed' ; exit 1; }

# Initialize LGAs
echo "Initializing LGAs"
python manage.py seed_lgas || { echo 'seed_lgas failed' ; exit 1; }

# Initialize crops
echo "Initialize crops"
python manage.py seed_crops || { echo 'seed_crops failed' ; exit 1; }

# Initialize animals
echo "Initialize animals"
python manage.py seed_animals || { echo 'seed_animals failed' ; exit 1; }

# Initialize crop varieties
echo "Initialize crop varieties"
python manage.py seed_crop_varieties || { echo 'seed_crop_varieties failed' ; exit 1; }

# Creating staticfiles dir
echo "Creating staticfiles dir"
mkdir staticfiles
