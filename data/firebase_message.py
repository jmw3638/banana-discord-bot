import os
import json
import firebase_admin
from firebase_admin import credentials, db
import config.firebase_config

async def set_message_mapping(original_message_id, forwarded_message_id):
    ref = db.reference(f'messages/{original_message_id}')
    ref.set(forwarded_message_id)

async def get_message_mapping(original_message_id):
    ref = db.reference(f'messages/{original_message_id}')
    print(ref.get())
    return ref.get()

async def remove_message_mapping(original_message_id):
    ref = db.reference(f'messages/{original_message_id}')
    ref.delete()
