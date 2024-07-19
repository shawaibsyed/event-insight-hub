import pandas as pd
from app.models.event import Event

def get_events_data():
    events = Event.list()
    df = pd.DataFrame(events)
    df['EventDateTime'] = pd.to_datetime(df['EventDateTime'], format='ISO8601')
    return df

def events_per_month():
    df = get_events_data()
    df['Month'] = df['EventDateTime'].dt.to_period('M').astype(str)
    events_per_month = df.groupby('Month').size()
    return events_per_month.astype(str).to_dict()

def events_per_organizer():
    df = get_events_data()
    events_per_organizer = df.groupby('OrganizerID').size()
    return events_per_organizer.to_dict()

def aggregate_feedback():
    df = get_events_data()

    # Example: Aggregate feedback ratings for each event
    df['AverageRating'] = df['Feedback'].apply(lambda x: sum([int(entry.get('Rating', 0)) for entry in x]) / len(x) if x else 0)

    # Example: Identify common themes in feedback comments
    feedback_comments = df['Feedback'].apply(lambda x: [entry.get('Comment', '') for entry in x])
    common_themes = pd.Series([comment for sublist in feedback_comments for comment in sublist]).value_counts().to_dict()

    return {
        'average_ratings': df[['EventID', 'Name', 'AverageRating']].to_dict(orient='records'),
        'common_themes': common_themes
    }
