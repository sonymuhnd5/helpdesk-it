from database import initialize_database
from ui import HelpDeskApp


def main():
    initialize_database()
    app = HelpDeskApp()
    app.mainloop()


if __name__ == "__main__":
    main()
