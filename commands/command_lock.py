
command_locks = {}

def acquire_lock(user_id: str, command_name: str) -> bool:

    if user_id in command_locks:
        return False
    
    command_locks[user_id] = command_name
    return True

def release_lock(user_id: str):

    command_locks.pop(user_id, None)

def is_locked(user_id: str) -> bool:

    return user_id in command_locks
