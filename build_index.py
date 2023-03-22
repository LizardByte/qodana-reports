# standard imports
import os
import time
from typing import Callable, Optional

# lib imports
from dotenv import load_dotenv
import requests

# load environment variables
load_dotenv()

# constants
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_FILE = os.path.join(CURRENT_DIR, 'gh-pages-template', 'index_template.html')

if not os.path.exists(TEMPLATE_FILE):
    raise FileNotFoundError(f'Could not find template file: {TEMPLATE_FILE}')

NEW_FILE = os.path.join(CURRENT_DIR, 'gh-pages', 'index.html')

ICON_MAP = dict(
    default='https://jetbrains.gallerycdn.vsassets.io/extensions/jetbrains/qodana/2022.3.4/1676474458891/Microsoft'
            '.VisualStudio.Services.Icons.Default',
    dotnet='https://raw.githubusercontent.com/dotnet/brand/main/logo/dotnet-logo.svg?',
    go='https://app.lizardbyte.dev/uno/language-icons/Go.svg',
    java='https://app.lizardbyte.dev/uno/language-icons/Java.svg',
    js='https://app.lizardbyte.dev/uno/language-icons/JavaScript.svg',
    php='https://app.lizardbyte.dev/uno/language-icons/PHP.svg',
    python='https://app.lizardbyte.dev/uno/language-icons/Python.svg',
)

ITEM_TYPE_MAP = dict(
    branches='Branches',
    pulls='Pull Requests',
)

# GitHub headers
github_headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': f'Bearer {os.getenv("PAT_TOKEN") if os.getenv("PAT_TOKEN") else os.getenv("GH_TOKEN")}'
}


def requests_loop(url: str,
                  headers: Optional[dict] = None,
                  method: Callable = requests.get,
                  max_tries: int = 8,
                  allow_statuses: list = [requests.codes.ok]) -> requests.Response:
    count = 1
    while count <= max_tries:
        print(f'Processing {url} ... (attempt {count} of {max_tries})')
        try:
            response = method(url=url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f'Error processing {url} - {e}')
            time.sleep(2**count)
            count += 1
        except Exception as e:
            print(f'Error processing {url} - {e}')
            time.sleep(2**count)
            count += 1
        else:
            if response.status_code in allow_statuses:
                return response
            else:
                print(f'Error processing {url} - {response.status_code}')
                time.sleep(2**count)
                count += 1


def main():
    # delete new file if it exists
    if os.path.exists(NEW_FILE):
        os.remove(NEW_FILE)

    # load template file to string
    with open(file=TEMPLATE_FILE, mode='r') as f:
        template = f.read()

    # dictionary to store organize reports
    reports = dict()

    # walk the directory tree
    for dir_path, dir_names, filenames in os.walk(os.path.join(os.getcwd(), 'gh-pages')):
        for filename in [f for f in filenames if f == 'index.html']:
            print(f'Found file: {filename} in directory: {dir_path}.')

            # language is root directory
            language = dir_path.split(os.sep)[-1]

            # source is 2 above
            source = dir_path.split(os.sep)[-2]

            # report is 3 above
            repo = dir_path.split(os.sep)[-3]

            # determine if source is a branch or pull request
            try:
                int(source)
            except ValueError:
                item_type = 'branches'
            else:
                item_type = 'pulls'

            try:
                reports[repo]
            except KeyError:
                reports[repo] = dict(
                    branches=dict(),
                    pulls=dict(),
                )
            finally:
                try:
                    reports[repo][item_type][source]
                except KeyError:
                    reports[repo][item_type][source] = dict(
                        languages=[language],
                    )
                else:
                    reports[repo][item_type][source]['languages'].append(language)

    for repo in reports:
        print(f'Found repo: {repo}')

        # create a repo card in html
        card = f"""
            <div class="container mb-5 shadow border-0 bg-dark rounded-0 px-0">
                <div class="container py-4 px-1">
                    <div class="d-flex g-0 text-white">
                        <img class="d-flex d-column px-3 rounded-0 mx-auto"
                            src=https://app.lizardbyte.dev/uno/github/openGraphImages/{repo}_624x312.png
                            alt=""
                            style="min-width: 312px; max-width: 312px; min-height: 156px; max-height: 156px;
                            width: auto; object-fit: contain; object-position: center top;">
                        <div class="d-flex flex-column border-white px-3 border-start w-100">
                            <div>
                                <h4 class="card-title mb-3 fw-bolder ms-0 mx-2">{repo}</h4>
                                <div id="branches" class="d-none">
                                    <h5 class="mb-3 ms-0 mx-2">Branches</h5>
                                    <ul>
                                        <!-- branches -->
                                    </ul>
                                </div>
                                <div id="pulls" class="d-none">
                                    <h5 class="mb-3 ms-0 mx-2">Pull Requests</h5>
                                    <ul>
                                        <!-- pulls -->
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        """
        for item_type in reports[repo]:
            if reports[repo][item_type]:
                # replace d-none
                card = card.replace(f'<div id="{item_type}" class="d-none">', f'<div id="{item_type}">')

                # sort items
                if item_type == 'branches':
                    # alphabetical
                    reports[repo][item_type] = dict(sorted(reports[repo][item_type].items()))
                elif item_type == 'pulls':
                    # reversed numerical (the newest first)
                    reports[repo][item_type] = dict(
                        sorted(reports[repo][item_type].items(),
                               key=lambda x: int(x[0]),
                               reverse=True
                               )
                    )

                for item in reports[repo][item_type]:
                    print(f'Found {item_type}: {item}. for repo: {repo}')

                    # get info about the branch or pull request from GitHub api
                    item_response = requests_loop(
                        url=f'https://api.github.com/repos/LizardByte/{repo}/{item_type}/{item}',
                        headers=github_headers
                    )
                    item_info = item_response.json()

                    extra_info = ''
                    extra_url = ''
                    extra_class = ''
                    extra_font_awesome = ''

                    if item_type == 'branches':
                        extra_info = item_info['commit']['sha'][0:7]  # first 7 characters
                        extra_url = item_info['_links']['html']
                        extra_font_awesome = 'fas fa-code-branch'
                    elif item_type == 'pulls':
                        extra_info = f"{item_info['title']} ({item_info['user']['login']})"
                        extra_url = item_info['html_url']
                        pull_state = item_info['state']  # open or closed
                        pull_merged = item_info['merged']  # True or False
                        pull_draft = item_info['draft']  # True or False
                        extra_font_awesome = 'fas fa-code-pull-request'

                        if pull_state == 'open':
                            if pull_draft:
                                extra_font_awesome = 'fas fa-code-pull-request text-secondary'
                            else:
                                extra_font_awesome = 'fas fa-code-pull-request text-success'
                        elif pull_state == 'closed':
                            if pull_merged:
                                extra_class = 'pull-closed pull-merged d-none'
                                extra_font_awesome = 'fas fa-code-merge text-purple'
                            else:
                                extra_class = 'pull-closed pull-unmerged d-none'
                                extra_font_awesome = 'fas fa-code-merge text-danger'

                    font_awesome = f'<i class="{extra_font_awesome}"></i>'

                    # create a link to the branch or pull request
                    item_link = f"""
                        <a class="text-decoration-none text-white"
                            href="{extra_url}"
                            target="_blank"
                        >{font_awesome} {item} - {extra_info}</a>
                    """

                    # create a list item in html
                    list_item = f"""
                    <li class="list-group-item {extra_class}">{item_link}<br>
                        <!-- language -->
                    </li>
                    """

                    for language in reports[repo][item_type][item]['languages']:
                        print(f'Found language: {language}. for {item_type}: {item}. for repo: {repo}')

                        # create a language icon in html
                        language_icon = f"""
                        <a class="ms-2" href="{repo}/{item}/{language}/index.html">
                            <img src="{ICON_MAP.get(language, ICON_MAP['default'])}"
                                alt="{language}"
                                target="_blank"
                                style="min-width: 30px; max-width: 30px; min-height: 30px; max-height: 30px;"></a>
                        """

                        list_item = list_item.replace('<!-- language -->', f'{language_icon}<!-- language -->')

                    card = card.replace(f'<!-- {item_type} -->', f'{list_item}<!-- {item_type} -->')

        template = template.replace('<!-- REPLACE_ME -->', f'{card}<!-- REPLACE_ME -->')

    # create directories if they don't exist
    if not os.path.isdir(os.path.dirname(NEW_FILE)):
        os.makedirs(os.path.dirname(NEW_FILE))

    # write the template file to disk
    with open(file=NEW_FILE, mode='w') as f:
        print(f'Writing new file: {NEW_FILE}')
        f.write(template)


if __name__ == "__main__":
    main()
