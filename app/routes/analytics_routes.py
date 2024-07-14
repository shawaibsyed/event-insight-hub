from flask import jsonify
from . import analytics_bp
from app.analytics.event_analytics import events_per_month, events_per_organizer, aggregate_feedback
from app.analytics.participant_analytics import participants_events_attended

@analytics_bp.route('/events-per-month', methods=['GET'])
def get_events_per_month():
    events_data = events_per_month()
    return jsonify(events_data)

@analytics_bp.route('/events-per-organizer', methods=['GET'])
def get_events_per_organizer():
    events_data = events_per_organizer()
    return jsonify(events_data)

@analytics_bp.route('/participants-events-attended', methods=['GET'])
def get_participants_events_attended():
    participants_data = participants_events_attended()
    return jsonify(participants_data)

@analytics_bp.route('/feedback-analysis', methods=['GET'])
def get_feedback_analysis():
    feedback_data = aggregate_feedback()
    return jsonify(feedback_data)
