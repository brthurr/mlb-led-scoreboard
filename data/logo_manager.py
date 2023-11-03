import debug
import os
import requests
import cairosvg
from PIL import Image
from io import BytesIO
import pwd
import grp
import statsapi

class LogoManager:
    def __init__(self, base_path='assets/team_logos', reference_file='.permref'):
        self.base_path = base_path
        self.reference_file = reference_file
        self.uid, self.gid = self.get_permissions_from_reference()
        self.ensure_directory()
        
    def get_permissions_from_reference(self):
        if os.path.exists(self.reference_file):
            uid = os.stat(self.reference_file).st_uid
            gid = os.stat(self.reference_file).st_gid
            return uid, gid
        else:
            raise FileNotFoundError(f"Reference file {self.reference_file} not found.")

    def ensure_directory(self):
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)
            os.chown(self.base_path, self.uid, self.gid)

    def fetch_and_save_logo(self, team_id):
        url = f"https://www.mlbstatic.com/team-logos/{team_id}.svg"
        debug.info(f'{url}')
        response = requests.get(url)
        
        if response.status_code == 200:
            png_output = BytesIO()
            cairosvg.svg2png(bytestring=response.content, write_to=png_output)
            image = Image.open(png_output)
            image_resized = image.resize((32, 32), Image.Resampling.LANCZOS)
            
            logo_path = os.path.join(self.base_path, f'{team_id}.png')
            image_resized.save(logo_path, 'PNG')
            #os.chown(logo_path, self.uid, self.gid)
        else:
            debug.warning(f"Failed to fetch logo for team_id: {team_id}")

    def fetch_and_save_team_logos(self, home_abbr, away_abbr):
        home_id = self.lookup_team_id(home_abbr)
        away_id = self.lookup_team_id(away_abbr)
        if home_id:
            self.fetch_and_save_logo(home_id)
        if away_id:
            self.fetch_and_save_logo(away_id)

    def lookup_team_id(self, team_abbr):
        team_data = statsapi.lookup_team(team_abbr)
        return team_data[0]['id'] if team_data else None
