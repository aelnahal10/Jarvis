import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_session(user_id):
    return r.get(user_id)

def update_session(user_id, data):
    r.set(user_id, data)
