from flask import Flask, render_template, request, redirect, url_for
import requests
import calendar
from datetime import datetime

app = Flask(__name__)

# Constants
API_KEY = "4aecb6ba"
BASE_URL = "http://www.omdbapi.com/"

def get_movie_by_title(title, year=None):
    """
    Fetches movie details from OMDb API by title and optional year.
    """
    params = {
        'apikey': API_KEY,
        't': title
    }
    
    # Add year parameter if provided
    if year:
        params['y'] = year
    
    # Send GET request to the API
    response = requests.get(BASE_URL, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        # Check if the API returned a valid response
        if data.get("Response") == "True":
            return data
        else:
            print(f"Error from API: {data.get('Error')}")
            return None
    else:
        print(f"HTTP Error: {response.status_code}")
        return None

def parse_release_date(movie_data):
    """
    Parses the 'Released' string from OMDb data into a Python datetime object.
    """
    release_date_str = movie_data.get("Released")
    if release_date_str and release_date_str != "N/A":
        try:
            # OMDb date format is typically "DD MMM YYYY" (e.g., "16 Jul 2010")
            date_object = datetime.strptime(release_date_str, '%d %b %Y')
            return date_object
        except ValueError:
            return None
    return None

def test_horror_movies_2020_to_today():
    """
    Test function to pull horror movies from 2020 through today's date and store in a .txt file
    """
    current_date = datetime.now()
    start_year = 2020
    
    # Known horror movies from 2020-2025 to test with
    test_horror_movies = [
        "The Invisible Man", "The Hunt", "Gretel & Hansel", "Brahms: The Boy II",  # 2020
        "A Quiet Place Part II", "Candyman", "Last Night in Soho", "Halloween Kills", "Malignant",  # 2021
        "Scream", "X", "The Black Phone", "Barbarian", "Smile", "Halloween Ends", "Nope",  # 2022
        "M3GAN", "Scream VI", "Evil Dead Rise", "Insidious: The Red Door", "Talk to Me", "The Nun II", "Saw X",  # 2023
        "Abigail", "A Quiet Place: Day One", "Longlegs", "Alien: Romulus", "Terrifier 3", "The Substance",  # 2024
        "Nosferatu", "Wolf Man", "28 Years Later", "Final Destination: Bloodlines", "The Conjuring: Last Rites"  # 2025
    ]
    
    horror_movies_found = []
    
    print(f"Testing horror movies from 2020 to {current_date.year}...")
    
    for movie_title in test_horror_movies:
        print(f"Searching for: {movie_title}")
        
        # Try to get movie details
        movie_data = get_movie_by_title(movie_title)
        
        if movie_data:
            # Parse release date
            release_date = parse_release_date(movie_data)
            
            if release_date:
                # Check if it's within our date range (2020 to current date)
                if (release_date.year >= start_year and release_date <= current_date):
                    # Check if it's actually a horror movie
                    genres = [g.strip().lower() for g in movie_data.get('Genre', '').split(',')]
                    
                    if 'horror' in genres:
                        movie_info = {
                            'title': movie_data.get('Title'),
                            'year': movie_data.get('Year'),
                            'released': movie_data.get('Released'),
                            'genre': movie_data.get('Genre'),
                            'director': movie_data.get('Director'),
                            'imdb_rating': movie_data.get('imdbRating'),
                            'imdb_id': movie_data.get('imdbID'),
                            'plot': movie_data.get('Plot', '')
                        }
                        
                        horror_movies_found.append(movie_info)
                        print(f"✓ Found: {movie_info['title']} ({movie_info['year']}) - Released: {movie_info['released']}")
                    else:
                        print(f"⚠ Not horror genre: {movie_title}")
                else:
                    print(f"⚠ Outside date range: {movie_title} ({release_date.year})")
            else:
                print(f"⚠ No valid release date: {movie_title}")
        else:
            print(f"✗ Not found: {movie_title}")
    
    # Sort movies by release date
    horror_movies_found.sort(key=lambda x: datetime.strptime(x['released'], '%d %b %Y'))
    
    # Write to file
    with open("horror_movies_2020_today.txt", "w") as log_file:
        log_file.write("Horror Movies Released from 2020 to Current Date\n")
        log_file.write("=" * 60 + "\n")
        log_file.write(f"Generated on: {current_date.strftime('%B %d, %Y')}\n")
        log_file.write(f"Total movies found: {len(horror_movies_found)}\n")
        log_file.write("=" * 60 + "\n\n")
        
        for movie in horror_movies_found:
            log_file.write(f"Title: {movie['title']}\n")
            log_file.write(f"Year: {movie['year']}\n")
            log_file.write(f"Released: {movie['released']}\n")
            log_file.write(f"Genre: {movie['genre']}\n")
            log_file.write(f"Director: {movie['director']}\n")
            log_file.write(f"IMDb Rating: {movie['imdb_rating']}\n")
            log_file.write(f"IMDb ID: {movie['imdb_id']}\n")
            log_file.write(f"Plot: {movie['plot'][:200]}...\n" if len(movie['plot']) > 200 else f"Plot: {movie['plot']}\n")
            log_file.write("-" * 50 + "\n")
    
    print(f"\nCompleted! Found {len(horror_movies_found)} horror movies from 2020 to current date.")
    print("Results saved to 'horror_movies_2020_today.txt'")
    
    return horror_movies_found

# Route for selecting a year
@app.route('/')
def select_year():
    return render_template('select_year.html')

# Route for selecting a month
@app.route('/select_month', methods=['POST'])
def select_month():
    selected_year = request.form.get('year')
    return render_template('select_month.html', year=selected_year)

# Route for displaying the calendar
def fetch_horror_movies(year, month):
    """
    Fetch horror movies from the local horror_movies_2020_today.txt file 
    and filter by the selected year and month
    """
    filtered_movies = []
    
    try:
        with open("horror_movies_2020_today.txt", "r") as file:
            content = file.read()
            
            # Split the content into individual movie entries
            movie_entries = content.split("--------------------------------------------------")
            
            for entry in movie_entries:
                if "Title:" in entry and "Released:" in entry:
                    lines = entry.strip().split('\n')
                    movie_data = {}
                    
                    # Parse each line to extract movie information
                    for line in lines:
                        if line.startswith("Title: "):
                            movie_data['title'] = line.replace("Title: ", "").strip()
                        elif line.startswith("Released: "):
                            movie_data['released'] = line.replace("Released: ", "").strip()
                    
                    # Check if we have both title and release date
                    if 'title' in movie_data and 'released' in movie_data:
                        try:
                            # Parse the release date in the format 'dd MMM yyyy'
                            parsed_date = datetime.strptime(movie_data['released'], '%d %b %Y')
                            
                            # Check if the movie matches the selected year and month
                            if parsed_date.year == int(year) and parsed_date.month == int(month):
                                filtered_movies.append({
                                    "title": movie_data['title'],
                                    "release_date": parsed_date.day
                                })
                        except ValueError:
                            continue  # Skip if the date format is invalid
    
    except FileNotFoundError:
        print("Error: horror_movies_2020_today.txt file not found")
        return []
    except Exception as e:
        print(f"Error reading horror movies file: {e}")
        return []
    
    return filtered_movies

@app.route('/calendar', methods=['POST'])
def display_calendar():
    selected_year = int(request.form.get('year'))
    selected_month = int(request.form.get('month'))
    
    # Get month name for display
    month_names = ["", "January", "February", "March", "April", "May", "June", 
                   "July", "August", "September", "October", "November", "December"]
    month_name = month_names[selected_month]
    
    print(f"Fetching horror movies for {month_name} {selected_year}...")
    movies = fetch_horror_movies(selected_year, selected_month)
    print(f"Found {len(movies)} horror movies for {month_name} {selected_year}")

    # Generate the calendar for the selected month and year
    cal = calendar.Calendar(firstweekday=6)  # Start with Sunday
    month_days = cal.monthdayscalendar(selected_year, selected_month)

    return render_template('calendar.html', year=selected_year, month=selected_month, month_name=month_name, movies=movies, calendar=month_days)

def log_horror_movies():
    api_url = "http://www.omdbapi.com/"
    api_key = "4aecb6ba"
    start_year = 2017
    current_year = datetime.now().year
    current_month = datetime.now().month
    current_day = datetime.now().day

    with open("horror_movies_log.txt", "w") as log_file:
        for year in range(start_year, current_year + 1):
            for month in range(1, 13):
                if year == current_year and month > current_month:
                    break
                params = {
                    "apikey": api_key,
                    "type": "movie",
                    "y": year
                }
                response = requests.get(api_url, params=params)
                if response.status_code == 200:
                    movies = response.json().get('Search', [])
                    for movie in movies:
                        if "action" in movie.get('Genre', '').lower():
                            log_file.write(f"{{Title: {movie.get('Title')}, Genre: {movie.get('Genre')}}}\n")

def log_horror_movies_for_year(year):
    api_url = "http://www.omdbapi.com/"
    api_key = "4aecb6ba"

    with open("horror_movies_log.txt", "a") as log_file:  # Append to the log file
        for month in range(1, 13):
            params = {
                "apikey": api_key,
                "type": "movie",
                "y": year
            }
            response = requests.get(api_url, params=params)
            if response.status_code == 200:
                movies = response.json().get('Search', [])
                for movie in movies:
                    genres = [genre.strip().lower() for genre in movie.get('Genre', '').split(',')]
                    if "horror" in genres:
                        log_file.write(f"{{Title: {movie.get('Title')}, Genre: {movie.get('Genre')}}}\n")

def search_movies_by_keyword(keyword, api_key):
    """Fetches a list of movie results from OMDb based on a general keyword."""
    BASE_URL = "http://www.omdbapi.com/"
    params = {
        "apikey": api_key,
        "s": keyword,  # 's' is for search by title
        "type": "movie"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if data.get("Response") == "True":
        return data.get("Search", [])
    else:
        print(f"Error searching for keyword '{keyword}': {data.get('Error')}")
        return []

def get_movie_details(imdb_id, api_key):
    """Fetches full details for a specific movie using its IMDb ID."""
    BASE_URL = "http://www.omdbapi.com/"
    params = {
        "apikey": api_key,
        "i": imdb_id,  # 'i' is for IMDb ID search
        "plot": "short"
    }
    response = requests.get(BASE_URL, params=params)
    data = response.json()
    
    if data.get("Response") == "True":
        return data
    else:
        print(f"Error fetching details for IMDb ID {imdb_id}: {data.get('Error')}")
        return None

def filter_movies_by_genre(keyword, target_genre, api_key):
    """
    Searches for movies by keyword and then filters the results by the 
    specified genre.
    """
    print(f"Searching for movies with keyword: '{keyword}'")
    movie_results = search_movies_by_keyword(keyword, api_key)
    
    if not movie_results:
        return []

    filtered_list = []
    for movie in movie_results:
        details = get_movie_details(movie['imdbID'], api_key)
        if details:
            # Genres are returned as a string, e.g., "Action, Adventure, Sci-Fi"
            genres = [g.strip().lower() for g in details.get('Genre', '').split(',')]
            if target_genre.lower() in genres:
                filtered_list.append({
                    'Title': details['Title'],
                    'Year': details['Year'],
                    'Genre': details['Genre'],
                    'Released': details.get('Released', 'Unknown'),
                    'IMDb ID': details['imdbID']
                })
    
    return filtered_list

def test_horror_movies_search():
    """Test function to search for horror movies using the new method"""
    api_key = "4aecb6ba"
    
    # Try different keywords that might return horror movies
    keywords = ["horror", "scary", "halloween", "nightmare", "zombie"]
    
    with open("horror_movies_test_log.txt", "w") as log:
        log.write("Horror Movies Found:\n")
        log.write("=" * 50 + "\n")
        
        for keyword in keywords:
            print(f"Searching for horror movies with keyword: '{keyword}'")
            horror_movies = filter_movies_by_genre(keyword, "Horror", api_key)
            
            if horror_movies:
                for movie in horror_movies:
                    log.write(f"Title: {movie['Title']}\n")
                    log.write(f"Year: {movie['Year']}\n")
                    log.write(f"Released: {movie['Released']}\n")
                    log.write(f"Genres: {movie['Genre']}\n")
                    log.write(f"IMDb ID: {movie['IMDb ID']}\n")
                    log.write("-" * 30 + "\n")
                    
            print(f"Found {len(horror_movies)} horror movies for keyword '{keyword}'")
    
    print("Horror movies logged to horror_movies_test_log.txt")

def log_movies_for_2017_corrected():
    """Corrected function using proper OMDb API methods"""
    api_key = "4aecb6ba"
    base_url = "http://www.omdbapi.com/"
    year = "2017"
    log_file = "action_movies_test_log.txt"
    
    # List of popular movies from 2017 to test with
    test_movies = [
        "Guardians of the Galaxy Vol. 2",
        "Wonder Woman", 
        "Spider-Man: Homecoming",
        "Thor: Ragnarok",
        "Justice League",
        "Fast & Furious 8",
        "John Wick: Chapter 2",
        "Kong: Skull Island",
        "The Mummy",
        "Transformers: The Last Knight"
    ]
    
    with open(log_file, "w") as log:
        log.write("Action Movies from 2017:\n")
        log.write("=" * 50 + "\n")
        
        for movie_title in test_movies:
            try:
                params = {
                    "apikey": api_key,
                    "t": movie_title
                }
                
                response = requests.get(base_url, params=params)
                if response.status_code == 200:
                    movie_data = response.json()
                    
                    if movie_data.get('Response') == "True" and movie_data.get('Year') == year:
                        genres = [g.strip().lower() for g in movie_data.get('Genre', '').split(',')]
                        
                        if 'action' in genres:
                            log.write(f"Title: {movie_data.get('Title')}\n")
                            log.write(f"Release Date: {movie_data.get('Released')}\n")
                            log.write(f"Genres: {movie_data.get('Genre')}\n")
                            log.write("-" * 30 + "\n")
                            
            except Exception as e:
                print(f"Error processing {movie_title}: {e}")
    
    print(f"Movies logged to {log_file}")

if __name__ == '__main__':
    log_horror_movies()
    app.run(debug=True)