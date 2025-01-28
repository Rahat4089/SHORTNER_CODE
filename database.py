import motor.motor_asyncio
from config import DB_URI, DB_NAME

dbclient = motor.motor_asyncio.AsyncIOMotorClient(DB_URI)
database = dbclient[DB_NAME]
user_data = database['users']

# New user template
def new_user(id):
    return {
        '_id': id,
        'verify_status': {
            'is_verified': False,
            'verified_time': 0,
            'verify_token': "",
            'link': ""
        }
    }

# Check if user exists in the database
async def present_user(user_id):
    found = await user_data.find_one({'_id': user_id})
    return bool(found)

# Add new user to the database
async def add_user(user_id):
    user = new_user(user_id)
    await user_data.insert_one(user)

# Get user's verification status
async def db_verify_status(user_id):
    user = await user_data.find_one({'_id': user_id})
    if user:
        return user.get('verify_status', new_user(user_id)['verify_status'])
    return new_user(user_id)['verify_status']

# Update verification status in the database
async def db_update_verify_status(user_id, verify):
    await user_data.update_one({'_id': user_id}, {'$set': {'verify_status': verify}})
