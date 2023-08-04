# By eykuklin, 2023

import requests
import time
from dotenv import dotenv_values
from loguru import logger

class ProcOncall:
    def __init__(self):
        """Load credentials from .env"""
        try:
            config = dotenv_values(".env")
        except IOError:
            logger.error("Could not open .env file. Quit...")
            exit()
        else:
            logger.info("Loaded .env file...")
        self.oncall_url = config['ONCALL_URL']
        self.user = config['USER']
        self.passwd = config['PASSWD']
        self.schedule_file= config['SCHEDULE_FILE']
        self.csrf_token = ''
        self.oncall_auth = ''

    def make_post_request(self, urn:str, json_data:dict):
        requests.post(url=f'{self.oncall_url}{urn}',
                      headers={'Content-Type': 'application/json', 'x-csrf-token': f'{self.csrf_token}'},
                      cookies={'oncall-auth': f'{self.oncall_auth}'}, json=json_data)

    def get_credentials(self):
        """Obtain cookie and csrf token"""
        success = True
        while success:
            try:
                logger.info("Obtaining credentials...")
                response = requests.post(url=f'{self.oncall_url}/login', headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                         data={'username': f'{self.user}', 'password': f'{self.passwd}'}, timeout=(2,3))
                self.csrf_token = response.json()['csrf_token']
                self.oncall_auth = response.cookies.get_dict()['oncall-auth']
            except requests.exceptions.RequestException as e:
                logger.error(e)
                time.sleep(60)
            else:
                success = False
                logger.info("...Done")

    def add_user(self, new_user: str):
        """Add a new user"""
        try:
            self.make_post_request('/api/v0/users', {'name': f'{new_user}'})
        except requests.exceptions.RequestException:
            logger.error(f'Failed to add a new user: {new_user}')
        else:
            logger.info(f'Adding a new user... {new_user}')

    def update_user(self, name: str, full_name: str, phone_number: str, email: str):
        """Update user info via put"""
        try:
            response = requests.put(url=f'{self.oncall_url}/api/v0/users/{name}',
                                    headers={'Content-Type': 'application/json', 'x-csrf-token': f'{self.csrf_token}'},
                                    cookies={'oncall-auth': f'{self.oncall_auth}'},
                                    json={'full_name': f'{full_name}',
                                          'contacts': {'call': f'{phone_number}', 'sms': f'{phone_number}', 'email': f'{email}'}})
        except requests.exceptions.RequestException:
            logger.error(f'Failed to update user: {name}')
        else:
            logger.info(f'Update user... {name}')

    def add_team(self, new_team: str, scheduling_timezone: str, email: str, slack_channel: str):
        """Add a new team"""
        try:
            self.make_post_request('/api/v0/teams', {'name': f'{new_team}', "scheduling_timezone": f'{scheduling_timezone}',
                                                     'email': f'{email}', 'slack_channel': f'{slack_channel}'})
        except requests.exceptions.RequestException:
            logger.error(f'Connection Error. Failed to add a new team: {new_team}')
        else:
            logger.info(f'Adding a new team... {new_team}')

    def add_roster(self, team:str):
        """Add a roster"""
        try:
            self.make_post_request(f'/api/v0/teams/{team}/rosters', {'name': 'some_roster'})
        except requests.exceptions.RequestException:
            logger.error(f'Connection Error. Failed to add roster to team: {team}')
        else:
            logger.info(f'Adding roster to team: {team}...')

    def user_to_roster(self, team:str, user:str):
        """Add the user to the team roster: some_roster"""
        try:
            self.make_post_request(f'/api/v0/teams/{team}/rosters/some_roster/users', {'name': f'{user}'})
        except requests.exceptions.RequestException:
            logger.error(f'Connection Error. Failed to add user {user} to team roster: {team}')
        else:
            logger.info(f'Adding user {user} to team roster: {team}...')

    def add_event(self, team:str, user:str, role:str, start:int, end:int):
        """Add an event for the user"""
        try:
            self.make_post_request('/api/v0/events', {"role":f'{role}', "user":f'{user}', "team":f'{team}', "start":start,"end":end})
        except requests.exceptions.RequestException:
            logger.error(f'Failed to add new event for user {user} in team: {team}')
        else:
            logger.info(f'Adding a new event for user {user} in team: {team} ...')

    def get_team_list(self):
        """Get list of teams"""
        try:
            response = requests.get(url=f'{self.oncall_url}/api/v0/teams',
                                    headers={'Content-Type': 'application/json', 'x-csrf-token': f'{self.csrf_token}'},
                                    cookies={'oncall-auth': f'{self.oncall_auth}'})
        except requests.exceptions.RequestException:
            logger.error(f'Failed to get team list...')
        else:
            logger.info(f'Received team list...')
            return response.json()

    def get_team_events(self, team:str):
        """Get list of teams"""
        try:
            response = requests.get(url=f'{self.oncall_url}/api/v0/events?team={team}',
                                    headers={'Content-Type': 'application/json', 'x-csrf-token': f'{self.csrf_token}'},
                                    cookies={'oncall-auth': f'{self.oncall_auth}'})
        except requests.exceptions.RequestException:
            logger.error(f'Failed to get team list...')
        else:
            logger.info(f'Received team list...')
            return response.json()

