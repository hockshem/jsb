import pandas as pd
from constants.directories import POINTS_DIR
from typing import Union

points_file_path = f'{POINTS_DIR}/jnwpoints.csv'
points_df = pd.read_csv(points_file_path, index_col=0)

column_names_map = {
    'id': 'Discord ID',
    'bal': 'Balance',
    'acc': 'Accumulated Points'
}

def get_acc_pts(user_id: int):
    return _get_pts(user_id, 'acc')

def get_bal_pts(user_id: int):
    return _get_pts(user_id, 'bal')

def _get_pts(user_id: int, pts_type: str):
    if user_id not in points_df.index:
        points_df.loc[user_id] = 0 
    return points_df.at[user_id, column_names_map[pts_type]]

def update_pts(user_id: Union[int, list[int]], change: int):
    if type(user_id) is int:
        user_id = [user_id]
    
    for id in user_id:
        if id not in points_df.index:
            points_df.loc[id] = 0 
        
        points_df.at[id, column_names_map['bal']] += change
        if change > 0:
            points_df.at[id, column_names_map['acc']] += change
    
    _flush_data()
    

def _flush_data():
    new_points_df = points_df.reset_index(names=column_names_map['id'])
    new_points_df.to_csv(points_file_path, index=False)