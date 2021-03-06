#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *

from flask_migrate import Migrate
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database
migrate = Migrate(app, db)

# db.create_all()


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show',backref='venue',lazy=True)

    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows = db.relationship('Show',backref='artist')


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
# one show has one artist
# one show has one venue
# one venue has many shows
# one artist has many shows 
class Show(db.Model):
  __tablename__ = 'show'

  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer,db.ForeignKey('Artist.id'))
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'))
  starting_date = db.Column(db.DateTime)

  


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
 
  data=[]

  distinct_cities_and_states = Venue.query.distinct(Venue.city, Venue.state).all()
  for places in distinct_cities_and_states:
      area_venues = Venue.query.filter_by(state=places.state,city=places.city).all()
      print(area_venues)
      venues_list=[]
      for i in area_venues:
        venues_list.append({
          "id": i.id,
          "name": i.name
          # TODO upcoming shows
        })
      data.append({
          "city": places.city,
          "state": places.state,
          "venues":venues_list
      })
      # rs.execute('SELECT * FROM "Venue" WHERE ')

  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search = request.form['search_term']
  data = Venue.query.filter(Venue.name.ilike('%'+search+'%')).all()

  response = {
    "count": len(data),
    "data":data
  }
  

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
 


    show_venue = Venue.query.get(venue_id)

    past_shows = []
    upcoming_shows = []

    for show in show_venue.shows:

      # from https://stackoverflow.com/questions/53248537/typeerror-not-supported-between-instances-of-datetime-datetime-and-str
      show_sratin= show.starting_date
      start = datetime.strptime( show_sratin, '%Y-%m-%d %H:%M:%S')

      if start> datetime.now():
        upcoming_shows.append({
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
        "start_time": show.starting_date
        })
      else:
        past_shows.append({
          "artist_id": show.artist.id,
          "artist_name": show.artist.name,
          "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
          "start_time": show.starting_date
          })

    data= {
      "id": venue_id,
      "name": show_venue.name,
      "genres": show_venue.genres,
      "address": show_venue.address,
      "city": show_venue.city,
      "state": show_venue.state,
      "phone": show_venue.phone,
      "website": "https://www.themusicalhop.com",
      "facebook_link": show_venue.facebook_link,
      "seeking_talent": True,
      "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
      "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
      ,"past_shows": past_shows,
    "upcoming_shows":upcoming_shows
    }



      
    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead

      error = False
    # body={}
      # the_form = VenueForm(request.form)


      try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        address = request.form['address']
        genres = request.form.getlist('genres')
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']

        
  # TODO: modify data to be the data object returned from db insertion

        new_venue = Venue(
          name=name,
          city=city,
          state=state,
          address=address,
          phone=phone,
          facebook_link=facebook_link,
          genres=genres
          )
        # new_venue.add()
        db.session.add(new_venue)
        db.session.commit()
      except: 
        error = True
        db.session.rollback()
        # print(sys.exc_info())
      finally: 
        db.session.close()
      if error:
        # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')

        flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
      else: 
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
      # id= new_venue.id

      return render_template('pages/home.html')




  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    try:
        deleted_venue = Venue.query.get(venue_id)
        db.session.delete(deleted_venue)
        db.session.commit()
    except:
        db.session.rollback()
    finally:
        db.session.close()
        return render_template('pages/home.html')


  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  data = Artist.query.order_by('id').all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search = request.form['search_term']
  data = Artist.query.filter(Artist.name.ilike('%'+search+'%')).all()


  response={
    "count": len(data),
    "data":  data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


#https://stackoverflow.com/questions/59362348/reading-character-array-instead-of-string-array-from-flask-sqlalchemy
#quick fix for genres. I'm not sure why it's hapenning 
def fix_json_array(obj, attr):
    arr = getattr(obj, attr)
    if isinstance(arr, list) and len(arr) > 1 and arr[0] == '{':
        arr = arr[1:-1]
        arr = ''.join(arr).split(",")
        setattr(obj,attr, arr)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data = Artist.query.get(artist_id)
  #quick fix
  fix_json_array(data, "genres")
  # shown_venue= Venue.query.get(venue_id)


  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)


  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
      error = False
      artist = Artist.query.get(artist_id)


      try:
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.genres = request.form.getlist('genres')
        artist.phone = request.form['phone']
        artist.facebook_link = request.form['facebook_link']

        
        db.session.commit()
      except: 
        error = True
        db.session.rollback()
        # print(sys.exc_info())
      finally: 
        db.session.close()
      if error: 
        flash('An error occurred. ' + request.form['name']+ ' could not be listed.')
      else: 

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')


      return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  venue = Venue.query.get(venue_id)
  form = ArtistForm(obj=artist)


  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)


  error = False


  try:
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.genres = request.form.getlist('genres')
        venue.phone = request.form['phone']
        venue.facebook_link = request.form['facebook_link']

        
        db.session.commit()
  except: 
        error = True
        db.session.rollback()
  finally: 
      db.session.close()
      if error: 
        flash('An error occurred. Venue ' + request.form['name']+ ' could not be listed.')
      else: 
        flash('Venue ' + request.form['name'] + ' was successfully listed!')



  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
      error = False


      try:
        name = request.form['name']
        city = request.form['city']
        state = request.form['state']
        genres = request.form.getlist('genres')
        phone = request.form['phone']
        facebook_link = request.form['facebook_link']

        
    # TODO: modify data to be the data object returned from db insertion

        new_artist = Artist(
          name=name,
          city=city,
          state=state,
          phone=phone,
          facebook_link=facebook_link,
          genres=genres
          )
        db.session.add(new_artist)
        db.session.commit()
      except: 
        error = True
        db.session.rollback()
      finally: 
        db.session.close()
      if error:
      # TODO: on unsuccessful db insert, flash an error instead.
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')


        flash('An error occurred. ' + request.form['name']+ ' could not be listed.')
      else: 

        # on successful db insert, flash success
        flash('Artist ' + request.form['name'] + ' was successfully listed!')




      return render_template('pages/home.html')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  shows = Show.query.all()
  for show in shows:
    #I'm not sure If I should add some images
    data.append({
      "venue_id": show.venue_id,
      "venue_name": show.venue.name,
      "artist_id": show.artist_id,
      "artist_name": show.artist.name,
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": show.starting_date

    })

      


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
      error= False
      try:
        artist_id = request.form['artist_id']
        venue_id = request.form['venue_id']
        starting_time=request.form['start_time']

        new_show = Show(
          artist_id=artist_id,
          venue_id=venue_id,
          starting_date=starting_time
          )

        db.session.add(new_show)
        db.session.commit()
      except: 
        error = True
        db.session.rollback()
      finally: 
        db.session.close()
      if error:
        # e.g., flash('An error occurred. Show could not be listed.')

        flash('An error occurred. could not be listed.')
      else: 

        # TODO: on unsuccessful db insert, flash an error instead.
        flash('Show was successfully listed!')




      return render_template('pages/home.html')



  # TODO: on unsuccessful db insert, flash an error instead.
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
