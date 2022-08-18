from dataclasses import dataclass


@dataclass
class Schedule:
    app_pKey: str
    sortKey: str
    rotation: list
    start_dt: str


@dataclass
class User:
    app_pKey: str
    sortKey: str
    History: list


def create_history_item(start_dt, end_dt):
    return {'start_dt': start_dt, 'end_dt': end_dt}
