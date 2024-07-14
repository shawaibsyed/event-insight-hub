import pandas as pd
from app.models.participant import Participant

def get_participants_data():
    participants = Participant.list()
    df = pd.DataFrame(participants)
    return df

def participants_events_attended():
    df = get_participants_data()
    participants_attended = df['EventsAttended'].apply(len)
    return participants_attended.describe().to_dict()
