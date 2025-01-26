"""
habit.py: Defines the Habit class for tracking habit completions and streaks.
"""

from datetime import datetime, timedelta

class Habit:
    """
    A class to represent a habit.

    Attributes:
        name (str): The name of the habit.
        frequency (str): The frequency of the habit ('daily' or 'weekly').
        creation_date (datetime): The date when the habit was created.
        completions (list): A list of datetime objects representing completion dates.
    """

    def __init__(self, name, frequency, creation_date=None):
        """
        Initializes a new Habit instance.

        Args:
            name (str): The name of the habit.
            frequency (str): The frequency of the habit ('daily' or 'weekly').
            creation_date (datetime, optional): The date when the habit was created. 
                Defaults to the current date and time if not provided.
        """
        self.name = name
        self.frequency = frequency.lower()
        self.creation_date = creation_date or datetime.now()
        self.completions = []

    def add_completion(self, date_time):
        """
        Adds a completion date to the habit.

        Args:
            date_time (datetime): The date and time when the habit was completed.
        """
        self.completions.append(date_time)

    def complete(self):
        """
        Marks the habit as completed by adding the current datetime to the completions list
        and printing a completion message.
        """
        completion_time = datetime.now()
        self.completions.append(completion_time)
        print(f"Habit '{self.name}' marked as completed on {completion_time.strftime('%Y-%m-%d %H:%M:%S')}.")

    def streak(self):
        """
        Calculates the longest streak of consecutive habit completions based on the habit's frequency.

        If the frequency is 'daily', it calculates the longest streak of consecutive days.
        If the frequency is 'weekly', it calculates the longest streak of consecutive weeks.

        Returns:
            int: The length of the longest streak of habit completions.
        """
        if not self.completions:
            return 0

        if self.frequency == 'daily':
            unique_dates = sorted({comp.date() for comp in self.completions})
            streak = 1
            longest_streak = 1
            for i in range(1, len(unique_dates)):
                if (unique_dates[i] - unique_dates[i - 1]).days == 1:
                    streak += 1
                    longest_streak = max(longest_streak, streak)
                else:
                    streak = 1 

        elif self.frequency == 'weekly':
            unique_weeks = sorted({comp.isocalendar()[:2] for comp in self.completions})
            streak = 1
            longest_streak = 1
            for i in range(1, len(unique_weeks)):
                prev_year, prev_week = unique_weeks[i - 1]
                curr_year, curr_week = unique_weeks[i]

                if (curr_year == prev_year and curr_week == prev_week + 1) or (
                    curr_year == prev_year + 1 and prev_week == 52 and curr_week == 1):
                    streak += 1
                    longest_streak = max(longest_streak, streak)
                else:
                    streak = 1 

        return longest_streak





