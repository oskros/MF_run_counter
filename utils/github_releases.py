import time
from utils import tk_utils
from init import *
from requests import request
import logging
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


def get_releases(repo_name):
    releases = []
    response = _request('GET', GITHUB_API + '/repos/{0}/releases'.format(repo_name), timeout=2)
    response.raise_for_status()
    releases.extend(response.json())

    return releases


def check_newest_version(release_repo):
    try:
        from packaging import version as pk_version
        releases = get_releases('oskros/MF_run_counter')
        latest_ver = releases[0]['tag_name']
        if pk_version.parse(version) < pk_version.parse(latest_ver):
            tk_utils.MessageBox(b1='OK', b2='', msg='Your version is not up to date. Get the newest release from', title='New version', hyperlink=release_repo)
        return str(sum(r['assets'][0]['download_count'] for r in releases))
    except Exception as e:
        logging.debug(str(e))
        return ''
