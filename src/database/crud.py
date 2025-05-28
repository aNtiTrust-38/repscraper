def is_duplicate(post_id, processed_ids):
    return post_id in processed_ids

def mark_processed(post_id, processed_ids):
    processed_ids.add(post_id)
