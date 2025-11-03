# 🎃 Horror Movie Release Date Calendar

A Flask web application that displays horror movies on an interactive calendar based on their actual release dates. Users can select any year (2020-2025) and month to see which horror movies were released during that time period.

![Python](https://img.shields.io/badge/python-v3.7+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.0+-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🎬 Features

- **Year Selection**: Choose from 2020 to current year (2025)
- **Month Selection**: Select any month to view releases
- **Interactive Calendar**: Visual calendar display with movies on their release dates
- **Horror Movie Database**: 30+ horror movies with accurate release information
- **OMDb API Integration**: Fetches detailed movie information including ratings, directors, and plots
- **Responsive Design**: Clean, horror-themed interface with spooky styling

## 📅 Example Movies by Month

- **January 2025**: Wolf Man (Jan 17)
- **July 2023**: Insidious: The Red Door (Jul 7)
- **January 2023**: M3GAN (Jan 6)
- **October 2024**: Terrifier 3 (Oct 11)
- **September 2022**: Smile (Sep 30)

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- Flask 2.0+
- Requests library
- OMDb API key (included in project)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/PeakMade/Horror-Movie-Release-Date-Calendar.git
   cd Horror-Movie-Release-Date-Calendar
   ```

2. **Install dependencies**
   ```bash
   pip install flask requests
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Open your browser**
   ```
   http://127.0.0.1:5000
   ```

## 📁 Project Structure

```
Horror-Movie-Release-Date-Calendar/
├── app.py                          # Main Flask application
├── horror_movies_2020_today.txt    # Local horror movie database
├── templates/
│   ├── select_year.html            # Year selection page
│   ├── select_month.html           # Month selection page
│   └── calendar.html               # Calendar display page
├── static/                         # CSS/JS files (if any)
├── .gitignore                      # Git ignore file
└── README.md                       # Project documentation
```

## 🎯 How It Works

1. **Year Selection**: User selects a year between 2020-2025
2. **Month Selection**: User chooses a specific month
3. **Data Processing**: App reads from local movie database (`horror_movies_2020_today.txt`)
4. **Calendar Generation**: Creates calendar grid using Python's `calendar` module
5. **Movie Display**: Places movie titles on their respective release dates

## 🔧 Technical Details

### Key Functions

- `fetch_horror_movies(year, month)`: Filters movies by selected year/month
- `parse_release_date(movie_data)`: Converts date strings to datetime objects
- `get_movie_by_title(title, year)`: Fetches movie details from OMDb API
- `test_horror_movies_2020_to_today()`: Generates movie database from API

### API Integration

The app uses the OMDb API (Open Movie Database) to fetch:
- Movie titles and release dates
- Genre classification
- Director information
- IMDb ratings
- Plot summaries

### Data Source

Movies are sourced from a curated list of popular horror films (2020-2025) and verified through the OMDb API for accuracy.

## 🎨 Features in Detail

### Calendar Display
- **Visual Grid**: Traditional calendar layout with weekdays
- **Movie Indicators**: Horror movies appear on their release dates
- **Themed Styling**: Dark, spooky color scheme with horror emojis
- **Navigation**: Easy return to date selection

### Movie Information
Each movie entry includes:
- Title and release date
- Genre classification
- Director name
- IMDb rating
- Brief plot summary
- IMDb ID for reference

## 🛠️ Configuration

The app includes several configurable elements:

```python
# OMDb API Configuration
API_KEY = "4aecb6ba"  # Free API key included
BASE_URL = "http://www.omdbapi.com/"

# Date Range
START_YEAR = 2020
CURRENT_YEAR = 2025
```

## 📊 Movie Database Stats

- **Total Movies**: 30+ horror films
- **Year Range**: 2020-2025
- **Coverage**: Major theatrical releases and popular horror titles
- **Accuracy**: Verified release dates via OMDb API

## 🚧 Future Enhancements

- [ ] Add movie posters from OMDb API
- [ ] Implement search functionality
- [ ] Add movie trailers via YouTube API
- [ ] Create user favorites system
- [ ] Add movie ratings and reviews
- [ ] Implement mobile-responsive design
- [ ] Add more movie genres (thriller, sci-fi)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OMDb API**: For providing comprehensive movie data
- **Flask Community**: For the excellent web framework
- **Horror Movie Fans**: For inspiration and testing feedback

## 📞 Contact

Project Link: [https://github.com/PeakMade/Horror-Movie-Release-Date-Calendar](https://github.com/PeakMade/Horror-Movie-Release-Date-Calendar)

---

Made with ❤️ and 🎃 for horror movie enthusiasts