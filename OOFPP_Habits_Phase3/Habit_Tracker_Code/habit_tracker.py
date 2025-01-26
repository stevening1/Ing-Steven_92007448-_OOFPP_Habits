"""
habit_tracker.py: Defines the HabitTracker class for managing habits and completions.
"""

from functools import reduce
import sqlite3
from datetime import datetime, timedelta
import random
from habit import Habit  # Import the Habit class

class HabitTracker:
    """
    A class to manage habit tracking and interactions with a database.

    Attributes:
        connection (sqlite3.Connection): The connection to the SQLite database.
    """
    def __init__(self, db_name="habit_tracker.db"):
        """
        Initialize the HabitTracker instance and create tables if necessary.

        Args:
            db_name (str): The name of the SQLite database file. Defaults to 'habit_tracker.db'.
        """
        self.connection = sqlite3.connect(db_name)
        self.create_tables()
        self.add_predefined_habits()

    def create_tables(self):
        """
        Create tables for storing habits and completions in the database.
        """
        with self.connection:
            self.connection.execute('''CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                frequency TEXT,
                creation_date TEXT
            )''')
            self.connection.execute('''CREATE TABLE IF NOT EXISTS completions (
                habit_id INTEGER,
                completion_date TEXT,
                FOREIGN KEY (habit_id) REFERENCES habits (id)
            )''')

    def add_predefined_habits(self):
        """
        Add predefined habits to the database with simulated completion data.
        """
        predefined_habits = [
            ("Sleep at 10:30pm", "daily"),
            ("Eat one vegetable", "daily"),
            ("Read the bible", "daily"),
            ("Drink 4L of water", "daily"),
            ("Go to church", "weekly")
        ]
        with self.connection:
            for name, frequency in predefined_habits:
                try:
                    self.connection.execute('INSERT INTO habits (name, frequency, creation_date) VALUES (?, ?, ?)',
                                            (name, frequency, (datetime.now() - timedelta(weeks=4)).isoformat()))
                    habit_id = self.connection.execute('SELECT id FROM habits WHERE name = ?', (name,)).fetchone()[0]
                    for week in range(4):
                        start_date = datetime.now() - timedelta(weeks=4 - week)
                        if frequency == "daily":
                            for day in range(7):
                                date = start_date + timedelta(days=day)
                                if random.choice([True, False]):  # Randomly mark some days as completed
                                    self.connection.execute('INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)',
                                                            (habit_id, date.isoformat()))
                        else:  # Weekly habit
                            if random.choice([True, False]):  # Randomly mark some weeks as completed
                                self.connection.execute('INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)',
                                                        (habit_id, start_date.isoformat()))
                except sqlite3.IntegrityError:
                    pass  # Skip if the predefined habit already exists

    def get_habits(self):
        """
        Retrieve all habits from the database.

        Returns:
            list: A list of tuples representing habits with their details.
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, name, frequency, creation_date FROM habits')
        return cursor.fetchall()

    def list_habits(self):
        """
        Display all predefined and user-created habits.
        """
        habits = self.get_habits()
        predefined_habit_names = {"Sleep at 10:30pm", "Eat one vegetable", "Read the bible", "Drink 4L of water", "Go to church"}

        predefined_habits = [habit for habit in habits if habit[1] in predefined_habit_names]
        user_created_habits = [habit for habit in habits if habit[1] not in predefined_habit_names]

        if predefined_habits:
            print("Predefined Habits:")
            for habit_data in predefined_habits:
                print(f"- {habit_data[1]}")

        if user_created_habits:
            print("\nUser-Created Habits:")
            for habit_data in user_created_habits:
                print(f"- {habit_data[1]}")

        if not habits:
            print("No habits found.")

    def list_habits_by_frequency(self, frequency):
        """
        List habits by a specific frequency.

        Args:
            frequency (str): The frequency ('daily' or 'weekly') to filter habits.
        """
        habits = self.get_habits()
        filtered_habits = filter(lambda h: h[2].lower() == frequency.lower(), habits)
        for habit_data in filtered_habits:
            habit = self.find_habit(habit_data[1])
            print(f"Habit: {habit.name} (Frequency: {habit.frequency})\n")

    def longest_streak_of_all_habits(self):
        """
        Calculate and display the longest streak across all habits and the habit associated with it.
        """
        habits = self.get_habits()
        streaks = map(lambda h: (self.find_habit(h[1]), self.find_habit(h[1]).streak()) if self.find_habit(h[1]) else (None, 0), habits)
        longest_habit, longest_streak = max(streaks, key=lambda x: x[1], default=(None, 0))

        if longest_habit:
            print(f"Longest streak of all habits: {longest_streak} (Habit: '{longest_habit.name}')")
        else:
            print("No habits found.")

    def longest_streak_for_habit(self, name):
        """
        Display the longest streak for a specific habit.

        Args:
            name (str): The name of the habit.
        """
        habit = self.find_habit(name)
        if habit:
            print(f"Longest streak for '{name}': {habit.streak()}")
        else:
            print(f"Habit '{name}' not found.")

    def find_habit(self, name):
        """
        Find a habit by name and populate its completion data.

        Args:
            name (str): The name of the habit.

        Returns:
            Habit: A Habit object populated with its completions, or None if not found.
        """
        cursor = self.connection.cursor()
        cursor.execute('SELECT id, name, frequency, creation_date FROM habits WHERE name = ?', (name,))
        row = cursor.fetchone()
        if row:
            habit = Habit(row[1], row[2], datetime.fromisoformat(row[3]))
            cursor.execute('SELECT completion_date FROM completions WHERE habit_id = ?', (row[0],))
            completions = cursor.fetchall()
            for completion in completions:
                habit.add_completion(datetime.fromisoformat(completion[0]))
            return habit
        return None

    def create_habit(self, name, frequency):
        """
        Create a new habit and store it in the database.

        Args:
            name (str): The name of the habit.
            frequency (str): The frequency of the habit ('daily' or 'weekly').
        """
        with self.connection:
            try:
                self.connection.execute('INSERT INTO habits (name, frequency, creation_date) VALUES (?, ?, ?)',
                                        (name, frequency.lower(), datetime.now().isoformat()))
                print(f"Habit '{name}' with frequency '{frequency}' created successfully.")
            except sqlite3.IntegrityError:
                print(f"Habit '{name}' already exists.")

    def complete_habit(self, name):
        """
        Mark a habit as completed for the current date and time.

        Args:
            name (str): The name of the habit to complete.

        Raises:
            ValueError: If the habit does not exist.
        """
        habit = self.find_habit(name)
        if habit:
            completion_time = datetime.now()
            with self.connection:
                habit_id = self.connection.execute('SELECT id FROM habits WHERE name = ?', (name,)).fetchone()[0]
                self.connection.execute('INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)',
                                        (habit_id, completion_time.isoformat()))
            habit.complete()
        else:
            print(f"Habit '{name}' not found.")

    def __del__(self):
        """
        Close the database connection when the object is deleted.
        """
        self.connection.close()

# User Interface to interact with the app

if __name__ == "__main__":
    tracker = HabitTracker()

    while True:
        print("\n--- Habit Tracker ---")
        print("1. Create a new habit")
        print("2. Mark a habit as completed")
        print("3. List all habits")
        print("4. List habits by frequency")
        print("5. Longest streak of all habits")
        print("6. Longest streak for a specific habit")
        print("7. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            name = input("Enter habit name: ")
            frequency = input("Enter frequency (daily/weekly): ")
            tracker.create_habit(name, frequency)
        elif choice == "2":
            name = input("Enter habit name to mark as completed: ")
            tracker.complete_habit(name)
        elif choice == "3":
            tracker.list_habits()
        elif choice == "4":
            frequency = input("Enter frequency (daily/weekly): ")
            tracker.list_habits_by_frequency(frequency)
        elif choice == "5":
            tracker.longest_streak_of_all_habits()
        elif choice == "6":
            name = input("Enter habit name: ")
            tracker.longest_streak_for_habit(name)
        elif choice == "7":
            print("Exiting Habit Tracker. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")
