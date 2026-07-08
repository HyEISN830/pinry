from django.utils.crypto import salted_hmac


def client_ip(request):
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def like_ip_hash(request):
    ip = client_ip(request)
    if not ip:
        ip = 'unknown'
    return salted_hmac('pinry.like.ip', ip).hexdigest()


def like_actor_key(request):
    if request.user.is_authenticated:
        return 'user:{}'.format(request.user.id)
    return 'ip:{}'.format(like_ip_hash(request))


def like_actor_keys(request):
    keys = [like_actor_key(request)]
    ip_key = 'ip:{}'.format(like_ip_hash(request))
    if ip_key not in keys:
        keys.append(ip_key)
    return keys
