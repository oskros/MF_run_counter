import time
from tk_utils import mbox
from init import *
from requests import request
GITHUB_API = "https://api.github.com"
_github_token_cli_arg = None


def _request(*args, **kwargs):
    with_auth = kwargs.pop("with_auth", True)
    token = _github_token_cli_arg
    if not token:
        token = os.environ.get("GITHUB_TOKEN", None)
    if token and with_auth:
        kwargs["auth"] = (token, 'x-oauth-basic')
    for _ in range(3):
        response = request(*args, **kwargs)
        is_travis = os.getenv("TRAVIS",  None) is not None
        if is_travis and 400 <= response.status_code < 500:
            print("Retrying in 1s (%s Client Error: %s for url: %s)" % (
                response.status_code, response.reason, response.url))
            time.sleep(1)
            continue
        break
    return response


# def _recursive_gh_get(href, items):
#     response = _request('GET', href)
#     response.raise_for_status()
#     items.extend(response.json())


def get_releases(repo_name):
    releases = []
    # _recursive_gh_get(
    #     GITHUB_API + '/repos/{0}/releases'.format(repo_name), releases)

    response = _request('GET', GITHUB_API + '/repos/{0}/releases'.format(repo_name), timeout=2)
    response.raise_for_status()
    releases.extend(response.json())

    return releases


def check_newest_version(release_repo):
    try:
        from packaging import version as pk_version
        latest = get_releases('oskros/MF_counter_releases')[0]
        latest_ver = latest['tag_name']
        if pk_version.parse(version) < pk_version.parse(latest_ver):
            mbox(b1='OK', b2='', msg='Your version is not up to date. Get the newest release from', title='New version', hyperlink=release_repo)
    except Exception as e:
        print(e)
        pass
