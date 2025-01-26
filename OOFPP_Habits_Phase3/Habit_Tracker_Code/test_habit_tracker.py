import pytest
from datetime import datetime, timedelta
from habit import Habit
from habit_tracker import HabitTracker

# Test the Habit class
def test_habit_creation():
    habit = Habit("Do degree work", "daily")
    assert habit.name == "Do degree work"
    assert habit.frequency == "daily"
    assert isinstance(habit.creation_date, datetime)
    assert habit.completions == []

def test_habit_add_completion():
    habit = Habit("Do degree work", "daily")
    completion_time = datetime.now()
    habit.add_completion(completion_time)
    assert completion_time in habit.completions

def test_habit_complete():
    habit = Habit("Do degree work", "daily")
    habit.complete()
    assert len(habit.completions) == 1

def test_habit_streak_daily():
    habit = Habit("Do degree work", "daily")
    habit.add_completion(datetime.now() - timedelta(days=2))
    habit.add_completion(datetime.now() - timedelta(days=1))
    habit.add_completion(datetime.now())
    assert habit.streak() == 3

def test_habit_streak_weekly():
    habit = Habit("Learn something new", "weekly")
    habit.add_completion(datetime.now() - timedelta(weeks=3))
    habit.add_completion(datetime.now() - timedelta(weeks=2))
    habit.add_completion(datetime.now() - timedelta(weeks=1))
    assert habit.streak() == 3

@pytest.fixture
def habit_tracker():
    habit_tracker = HabitTracker(":memory:")
    # Cleanup: Drop the tables explicitly before each test if needed.
    habit_tracker.connection.execute('DELETE FROM habits')
    habit_tracker.connection.execute('DELETE FROM completions')
    yield habit_tracker
    # Explicitly closing the connection and ensuring no lingering state.
    habit_tracker.connection.close()

def test_create_habit(habit_tracker):
    habit_tracker.create_habit("Eat savory breakfast", "daily")
    habit = habit_tracker.find_habit("Eat savory breakfast")
    assert habit is not None
    assert habit.name == "Eat savory breakfast"
    assert habit.frequency == "daily"

def test_complete_habit(habit_tracker):
    habit_tracker.create_habit("Water plants", "daily")
    habit_tracker.complete_habit("Water plants")
    habit = habit_tracker.find_habit("Water plants")
    assert len(habit.completions) == 1

def test_longest_streak_for_habit(habit_tracker, capsys):
    habit_tracker.create_habit("Workout", "daily")
    habit_tracker.complete_habit("Workout")
    
    # Get the habit ID for 'Workout'
    habit_id = habit_tracker.connection.execute('SELECT id FROM habits WHERE name = ?', ("Workout",)).fetchone()[0]
    
    # Insert two completions directly into the database with printed timestamps
    now = datetime.now()
    completion1 = (now - timedelta(days=2)).isoformat()
    completion2 = (now - timedelta(days=1)).isoformat()
    
    with habit_tracker.connection:
        habit_tracker.connection.execute(
            'INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)', 
            (habit_id, completion1)
        )
        habit_tracker.connection.execute(
            'INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)', 
            (habit_id, completion2)
        )
    
    # Print completion times
    print(f"Inserted completion 1: {completion1}")
    print(f"Inserted completion 2: {completion2}")
    
    # Calculate and check the longest streak
    habit_tracker.longest_streak_for_habit("Workout")
    captured = capsys.readouterr()
    assert "Longest streak for 'Workout': 3" in captured.out

def test_longest_streak_of_all_habits(habit_tracker, capsys):
    # Create habits
    habit_tracker.create_habit("Pray", "daily")
    habit_tracker.create_habit("Go to gym", "weekly")
    habit_tracker.list_habits()
    
    # Complete habits
    habit_tracker.complete_habit("Pray")
    habit_tracker.complete_habit("Go to gym")
    
    # Get the habit IDs for 'Pray' and 'Go to gym'
    pray_habit_id = habit_tracker.connection.execute('SELECT id FROM habits WHERE name = ?', ("Pray",)).fetchone()[0]
    gym_habit_id = habit_tracker.connection.execute('SELECT id FROM habits WHERE name = ?', ("Go to gym",)).fetchone()[0]
    
    # Insert two completions for 'Pray' and one completion for 'Go to gym' into the database with printed timestamps
    now = datetime.now()
    
    # For 'Pray', insert two rows (one day apart)
    pray_completion1 = (now - timedelta(days=2)).isoformat()
    pray_completion2 = (now - timedelta(days=1)).isoformat()
    
    # For 'Go to gym', insert one row
    gym_completion = (now - timedelta(days=1)).isoformat()

    # Insert completions into the database
    with habit_tracker.connection:
        habit_tracker.connection.execute(
            'INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)', 
            (pray_habit_id, pray_completion1)
        )
        habit_tracker.connection.execute(
            'INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)', 
            (pray_habit_id, pray_completion2)
        )
        habit_tracker.connection.execute(
            'INSERT INTO completions (habit_id, completion_date) VALUES (?, ?)', 
            (gym_habit_id, gym_completion)
        )
    
    # Print completion times to verify what we inserted
    print(f"Inserted Pray completion 1: {pray_completion1}")
    print(f"Inserted Pray completion 2: {pray_completion2}")
    print(f"Inserted Go to gym completion: {gym_completion}")
    
    # Call the method to compute the longest streak across all habits
    habit_tracker.longest_streak_of_all_habits()

    # Capture and print the output to debug
    captured = capsys.readouterr()
    print(captured.out)  # Print the captured output for debugging purposes
    
    # Now check if the longest streak is correct
    assert "Longest streak of all habits: 3 (Habit: 'Pray')" in captured.out




