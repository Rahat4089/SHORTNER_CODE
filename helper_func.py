import base64
import random
import string
from shortzy import Shortzy
from database import db_verify_status, db_update_verify_status

# Get verification status from database
async def get_verify_status(user_id):
    verify = await db_verify_status(user_id)
    return verify

# Update the user's verification status in the database
async def update_verify_status(user_id, verify_token="", is_verified=False, verified_time=0, link=""):
    current = await db_verify_status(user_id)
    current['verify_token'] = verify_token
    current['is_verified'] = is_verified
    current['verified_time'] = verified_time
    current['link'] = link
    await db_update_verify_status(user_id, current)

# Generate a short URL using Shortzy API
async def get_shortlink(url, api, link):
    shortzy = Shortzy(api_key=api, base_site=url)
    return await shortzy.convert(link)

# Get readable time for token expiry
def get_exp_time(seconds):
    periods = [('days', 86400), ('hours', 3600), ('mins', 60), ('secs', 1)]
    result = ''
    for period_name, period_seconds in periods:
        if seconds >= period_seconds:
            period_value, seconds = divmod(seconds, period_seconds)
            result += f'{int(period_value)}{period_name}'
    return result
