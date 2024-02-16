"""Seed database with sample data from CSV Files."""

from csv import DictReader
from app import db
from models import User, Garden, Plant, GardenPlant


db.drop_all()
db.create_all()

with open('generator/users.csv') as users:
    db.session.bulk_insert_mappings(User, DictReader(users))

# with open('generator/messages.csv') as messages:
#     db.session.bulk_insert_mappings(Message, DictReader(messages))

# with open('generator/follows.csv') as follows:
#     db.session.bulk_insert_mappings(Follows, DictReader(follows))
    
admin_user = User(username='russ', password='$2b$12$2NxxoOLs2q0wSCZ8T2udN.VyJm6/nuWi/fDXBbd/U0Nj.XF6HR7ba')
db.session.add(admin_user)

db.session.commit()

GardenPlant.query.delete()
Garden.query.delete()
Plant.query.delete()

# Add Playlists
garden1 = Garden(name='Garden-1', description='Garden 1 desc', user_id=301)
garden2 = Garden(name='Garden-2', description='Garden 2 desc', user_id=301)
garden3 = Garden(name='Garden-3', description='Garden 3 desc', user_id=301)
garden4 = Garden(name='Garden-4', description='Garden 4 desc', user_id=301)

db.session.add_all([garden1,garden2,garden3,garden4])

#Add Songs
# plant1 = Plant(name='Plant 1', api_id=1)
# plant2 = Plant(name='Plant 2', api_id=2)
# plant3 = Plant(name='Plant 3', api_id=3)
# plant4 = Plant(name='Plant 4', api_id=4)

# db.session.add_all([plant1,plant2,plant3,plant4])

db.session.commit()

#Add GardenPlant Connections
# garden_plant1 = GardenPlant(garden_id=garden1.id, plant_id=plant1.id)
# garden_plant2 = GardenPlant(garden_id=garden1.id, plant_id=plant2.id)
# playlist_song3 = GardenPlant(playlist_id=list2.id, song_id=a1song4.id)

# db.session.add_all([garden_plant1,garden_plant2])

# Commit--otherwise, this never gets saved!
db.session.commit()
