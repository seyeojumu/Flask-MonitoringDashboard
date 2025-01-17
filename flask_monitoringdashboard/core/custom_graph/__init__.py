import atexit
import os

from apscheduler.schedulers import SchedulerAlreadyRunningError
from apscheduler.schedulers.background import BackgroundScheduler

from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.custom_graph import add_value, get_graph_id_from_name, get_graphs

scheduler = BackgroundScheduler()


def init(app):
    if not app.debug or os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        try:
            scheduler.start()
            # print('Scheduler started')
            atexit.register(lambda: scheduler.shutdown())
        except SchedulerAlreadyRunningError as err:
            print(err)


def register_graph(name):
    with session_scope() as db_session:
        return get_graph_id_from_name(db_session, name)


def add_background_job(func, graph_id, **schedule):
    def add_data():
        with session_scope() as db_session:
            add_value(db_session, graph_id, func())

    add_data()  # already call once, so it can be verified that the function works
    scheduler.add_job(func=add_data, trigger="interval", **schedule)


def get_custom_graphs():
    with session_scope() as db_session:
        result = get_graphs(db_session)
        db_session.expunge_all()
        return result
