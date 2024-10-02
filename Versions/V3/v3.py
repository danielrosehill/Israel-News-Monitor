import sys
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from PyQt5.QtWidgets import QApplication, QWidget, QGridLayout, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QSplitter
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import Qt, QUrl, QTimer
from PyQt5.QtGui import QFont, QGuiApplication

class BrowserWindow(QWebEngineView):
    def __init__(self, url):
        super().__init__()
        self.load(QUrl(url))

class Quadrant(QWidget):
    def __init__(self, title, options):
        super().__init__()
        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; background-color: rgba(0, 0, 0, 0.7); color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16))

        self.browser = BrowserWindow(options[0][1])

        button_layout = QHBoxLayout()
        for label, url in options:
            button = QPushButton(f"{label}")
            button.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
            button.clicked.connect(lambda _, u=url: self.browser.load(QUrl(u)))
            button_layout.addWidget(button)

        layout.addWidget(title_label)
        layout.addWidget(self.browser)
        layout.addLayout(button_layout)
        self.setLayout(layout)

class SocialMediaQuadrant(QWidget):
    def __init__(self, title, options):
        super().__init__()
        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; background-color: rgba(0, 0, 0, 0.7); color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16))

        splitter = QSplitter(Qt.Horizontal)
        twitter_view = BrowserWindow("https://twitter.com/search?q=israel&src=typed_query&f=top")
        red_alert_view = BrowserWindow("https://www.oref.org.il/eng/alerts-history")
        splitter.addWidget(twitter_view)
        splitter.addWidget(red_alert_view)

        layout.addWidget(title_label)
        layout.addWidget(splitter)
        self.setLayout(layout)

class PublicSheltersQuadrant(QWidget):
    def __init__(self, title, options):
        super().__init__()
        layout = QVBoxLayout()

        title_label = QLabel(title)
        title_label.setStyleSheet("font-weight: bold; background-color: rgba(0, 0, 0, 0.7); color: white; padding: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 16))

        self.browser = BrowserWindow(options[0][1])

        button_layout = QGridLayout()
        cities = [
            ("Tel Aviv", "https://www5.tel-aviv.gov.il/Tlv4U/Gis/Default.aspx?592"),
            ("Jerusalem", "https://www.jerusalem.muni.il/en/residents/safety-and-security/emergency-preparedness/public-shelters/"),
            ("Netanya", "https://www.netanya.muni.il/eng/?CategoryID=1928"),
            ("Haifa", "https://www.haifa.muni.il/emergency/"),
            ("Be'er Sheva", "https://www.beer-sheva.muni.il/residents/Emergency/Pages/SheltersList.aspx"),
            ("Ashdod", "https://www.ashdod.muni.il/en/residents/emergency-preparedness/"),
            ("Ashkelon", "https://www.ashkelon.muni.il/emergency/Pages/default.aspx")
        ]

        for i, (city, url) in enumerate(cities):
            button = QPushButton(city)
            button.setStyleSheet("font-weight: bold; font-size: 14px; padding: 8px;")
            button.clicked.connect(lambda _, u=url: self.browser.load(QUrl(u)))
            button_layout.addWidget(button, i // 3, i % 3)

        layout.addWidget(title_label)
        layout.addWidget(self.browser)
        layout.addLayout(button_layout)
        self.setLayout(layout)

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Israel Emergency Monitoring Portal")
        self.setWindowFlags(Qt.Window | Qt.CustomizeWindowHint | Qt.WindowStaysOnTopHint)
        
        screen = QGuiApplication.primaryScreen().geometry()
        self.setGeometry(screen)

        main_layout = QVBoxLayout()

        top_banner = QLabel("Israel Emergency Monitoring Portal")
        top_banner.setStyleSheet("font-weight: bold; background-color: #3498db; color: white; padding: 10px;")
        top_banner.setAlignment(Qt.AlignCenter)
        top_banner.setFont(QFont("Arial", 20))

        self.time_display = QLabel()
        self.time_display.setStyleSheet("font-weight: bold; color: white; padding: 5px; background-color: rgba(0, 0, 0, 0.7);")
        self.time_display.setAlignment(Qt.AlignRight | Qt.AlignBottom)
        self.time_display.setFont(QFont("Arial", 14))

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(60000)  # Update every 60 seconds
        self.update_time()

        grid_layout = QGridLayout()
        quadrants = [
            ("TV", [("Kan", "https://www.kan.org.il/live/tv.aspx?stationid=2"),
                    ("i24 English", "https://video.i24news.tv/live/brightcove/en"),
                    ("Reuters", "https://www.reuters.com/world/middle-east/")]),
            ("News", [("TOI", "https://www.timesofisrael.com/"),
                      ("n12", "https://www.n12.co.il/")]),
            ("Social Media", []),
            ("Public Shelters", [("Guidelines", "https://www.oref.org.il/eng/emergencies/protection-guidelines")])
        ]

        for i, (title, options) in enumerate(quadrants):
            if i == 2:  # Social Media quadrant
                quadrant = SocialMediaQuadrant(title, options)
            elif i == 3:  # Public Shelters quadrant
                quadrant = PublicSheltersQuadrant(title, options)
            else:
                quadrant = Quadrant(title, options)
            grid_layout.addWidget(quadrant, i // 2, i % 2)

        bottom_banner = QPushButton("Links")
        bottom_banner.setStyleSheet("font-weight: bold; background-color: #2ecc71; color: white; padding: 10px;")
        bottom_banner.setFont(QFont("Arial", 16))
        bottom_banner.clicked.connect(self.show_links_modal)

        close_button = QPushButton("Close")
        close_button.setStyleSheet("font-weight: bold; background-color: #e74c3c; color: white; padding: 10px;")
        close_button.setFont(QFont("Arial", 16))
        close_button.clicked.connect(self.close)

        main_layout.addWidget(top_banner)
        main_layout.addLayout(grid_layout)
        main_layout.addWidget(bottom_banner)
        main_layout.addWidget(self.time_display)
        main_layout.addWidget(close_button)
        self.setLayout(main_layout)

    def update_time(self):
        ist_time = datetime.now(ZoneInfo("Asia/Jerusalem")).strftime("%H:%M")
        utc_time = datetime.now(timezone.utc).strftime("%H:%M")
        self.time_display.setText(f"IST: {ist_time} / UTC: {utc_time}")

    def show_links_modal(self):
        # Implement the links modal functionality here
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())