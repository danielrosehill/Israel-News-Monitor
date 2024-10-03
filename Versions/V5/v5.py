import sys
import json
import requests
import feedparser
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QScrollArea, QGridLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QFont, QGuiApplication

class BrowserWindow(QWebEngineView):
    def __init__(self, url):
        super().__init__()
        self.load(QUrl(url))

class TVWidget(QWidget):
    def __init__(self, title, options):
        super().__init__()
        layout = QVBoxLayout()
        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; background-color: rgba(0, 0, 0, 0.7); color: white; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 12))
        self.browser = BrowserWindow(options[0][1])
        button_layout = QHBoxLayout()
        for label, url in options:
            button = QPushButton(label)
            button.setStyleSheet("font-size: 10px; padding: 5px;")
            button.clicked.connect(lambda _, u=url: self.browser.load(QUrl(u)))
            button_layout.addWidget(button)
        layout.addWidget(title_label)
        layout.addWidget(self.browser)
        layout.addLayout(button_layout)
        self.setLayout(layout)

class RSSWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.scroll_area = QScrollArea()
        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)

        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.scroll_content)
        self.layout.addWidget(self.scroll_area)

        self.setLayout(self.layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_feed)
        self.timer.start(300000)  # Update every 5 minutes

        self.update_feed()

    def update_feed(self):
        feed_url = "https://www.timesofisrael.com/feed/"
        feed = feedparser.parse(feed_url)

        # Clear previous content
        for i in reversed(range(self.scroll_layout.count())): 
            self.scroll_layout.itemAt(i).widget().setParent(None)

        # Add title
        title = QLabel("The Times of Israel - Latest News")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        title.setAlignment(Qt.AlignCenter)
        self.scroll_layout.addWidget(title)

        # Add feed entries
        for entry in feed.entries[:10]:  # Display the latest 10 entries
            title = QLabel(entry.title)
            title.setStyleSheet("font-weight: bold;")
            title.setWordWrap(True)
            self.scroll_layout.addWidget(title)

            summary = QLabel(entry.summary)
            summary.setWordWrap(True)
            self.scroll_layout.addWidget(summary)

            self.scroll_layout.addWidget(QLabel(""))  # Spacer

        self.scroll_layout.addStretch()

class PublicSheltersTab(QWidget):
    def __init__(self, shelters_data):
        super().__init__()
        layout = QVBoxLayout()
        scroll_area = QScrollArea()
        scroll_content = QWidget()
        grid_layout = QGridLayout(scroll_content)
        row, col = 0, 0
        for city, url in shelters_data.items():
            button = QPushButton(city)
            button.setStyleSheet("font-size: 10px; padding: 5px;")
            button.clicked.connect(lambda _, u=url: self.load_shelter_url(u))
            grid_layout.addWidget(button, row, col)
            col += 1
            if col > 4:
                col = 0
                row += 1
        scroll_area.setWidget(scroll_content)
        scroll_area.setWidgetResizable(True)
        self.shelter_view = QWebEngineView()
        layout.addWidget(scroll_area, 1)
        layout.addWidget(self.shelter_view, 1)
        self.setLayout(layout)

    def load_shelter_url(self, url):
        self.shelter_view.load(QUrl(url))

def load_shelters_data():
    try:
        url = "https://raw.githubusercontent.com/danielrosehill/Public-Shelter-Lists-Israel/bdf68675fa68a70b69436c222b12e6ef59ea801f/Listings/021024/shelters.json"
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            print(f"Failed to fetch data: HTTP {response.status_code}")
            return {}
    except Exception as e:
        print(f"Error loading shelters data: {e}")
        return {}

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Israeli News Dashboard")
        self.setWindowFlags(Qt.Window | Qt.WindowMinMaxButtonsHint | Qt.WindowCloseButtonHint)
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        main_layout = QVBoxLayout()
        title_label = QLabel("Israeli News Dashboard")
        title_label.setStyleSheet("font-weight: bold; background-color: #3498db; color: white; padding: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Helvetica", 18))
        main_layout.addWidget(title_label)

        subtitle_label = QLabel("By: Claude Sonnet 3.5 & Daniel Rosehill")
        subtitle_label.setStyleSheet("background-color: #3498db; color: white; padding: 2px;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setFont(QFont("Arial", 10))
        main_layout.addWidget(subtitle_label)

        content_layout = QHBoxLayout()

        left_pane = QVBoxLayout()
        kan_tv = TVWidget("Kan", [("Kan 11", "https://www.kan.org.il/live/tv.aspx?stationid=2"),
                                  ("Kan 12", "https://www.kan.org.il/live/tv.aspx?stationid=23"),
                                  ("Kan 13", "https://www.kan.org.il/live/tv.aspx?stationid=24")])
        i24_tv = TVWidget("i24 English", [("i24", "https://www.i24news.tv/en/tv/live")])
        left_pane.addWidget(kan_tv)
        left_pane.addWidget(i24_tv)
        content_layout.addLayout(left_pane, 1)

        middle_pane = RSSWidget()
        content_layout.addWidget(middle_pane, 1)

        right_pane = QTabWidget()
        red_alerts_tab = BrowserWindow("https://www.oref.org.il/en")
        
        shelters_data = load_shelters_data()
        public_shelters_tab = PublicSheltersTab(shelters_data)
        
        guidance_tab = BrowserWindow("https://www.oref.org.il/eng/emergencies/protection-guidelines")
        right_pane.addTab(red_alerts_tab, "Red Alerts")
        right_pane.addTab(public_shelters_tab, "Public Shelters")
        right_pane.addTab(guidance_tab, "Guidance")
        content_layout.addWidget(right_pane, 1)

        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.showMaximized()
    sys.exit(app.exec_())