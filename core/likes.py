import ipaddress

from django.conf import settings
from django.utils.crypto import salted_hmac


def _iter_trusted_proxy_ips():
    trusted_proxy_ips = getattr(settings, 'TRUSTED_PROXY_IPS', ())
    if isinstance(trusted_proxy_ips, str):
        trusted_proxy_ips = trusted_proxy_ips.split(',')
    for value in trusted_proxy_ips or ():
        value = str(value).strip()
        if value:
            yield value


def _normalize_ip(value):
    value = (value or '').strip()
    if not value:
        return ''
    if value.startswith('[') and ']' in value:
        value = value[1:value.find(']')]
    elif value.count(':') == 1:
        host, port = value.rsplit(':', 1)
        if port.isdigit():
            value = host
    try:
        return ipaddress.ip_address(value).compressed
    except ValueError:
        return value


def _is_trusted_proxy(remote_addr):
    remote_addr = _normalize_ip(remote_addr)
    if not remote_addr:
        return False
    try:
        remote_ip = ipaddress.ip_address(remote_addr)
    except ValueError:
        remote_ip = None

    for trusted_proxy in _iter_trusted_proxy_ips():
        trusted_proxy = trusted_proxy.strip()
        if remote_ip is not None:
            try:
                if remote_ip in ipaddress.ip_network(
                    trusted_proxy,
                    strict=False,
                ):
                    return True
                continue
            except ValueError:
                pass
        if remote_addr == _normalize_ip(trusted_proxy):
            return True
    return False


def _first_forwarded_ip(forwarded_for):
    for forwarded_ip in forwarded_for.split(','):
        forwarded_ip = _normalize_ip(forwarded_ip)
        if forwarded_ip:
            return forwarded_ip
    return ''


def client_ip(request):
    remote_addr = _normalize_ip(request.META.get('REMOTE_ADDR', ''))
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for and _is_trusted_proxy(remote_addr):
        return _first_forwarded_ip(forwarded_for) or remote_addr
    return remote_addr


def _ip_identity(request):
    ip = client_ip(request)
    if not ip:
        ip = 'unknown'
    return ip


def like_ip_hash(request):
    return salted_hmac('pinry.like.ip', _ip_identity(request)).hexdigest()


def anonymous_like_actor_key(request):
    actor_hash = salted_hmac(
        'pinry.like.actor.v1',
        _ip_identity(request),
    ).hexdigest()
    return 'anon:v1:{}'.format(actor_hash)


def legacy_like_actor_key(request):
    return 'ip:{}'.format(like_ip_hash(request))


def like_actor_key(request):
    user = getattr(request, 'user', None)
    if getattr(user, 'is_authenticated', False):
        return 'user:{}'.format(user.id)
    return anonymous_like_actor_key(request)


def like_actor_keys(request):
    keys = [like_actor_key(request)]
    for actor_key in (
        anonymous_like_actor_key(request),
        legacy_like_actor_key(request),
    ):
        if actor_key not in keys:
            keys.append(actor_key)
    return keys


# View records live in separate tables, so they can safely reuse the exact
# viewer identity used by likes. This keeps login/IP migration and legacy-key
# compatibility identical for both interactions.
def view_ip_hash(request):
    return like_ip_hash(request)


def anonymous_view_actor_key(request):
    return anonymous_like_actor_key(request)


def legacy_view_actor_key(request):
    return legacy_like_actor_key(request)


def view_actor_key(request):
    return like_actor_key(request)


def view_actor_keys(request):
    return like_actor_keys(request)
