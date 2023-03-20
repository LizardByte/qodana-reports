# standard imports
import os

# constants
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

directories = [CURRENT_DIR, os.path.join(CURRENT_DIR, 'qodana-reports')]

for directory in directories:
    TEMPLATE_FILE = os.path.join(directory, 'gh-pages-template', 'index_template.html')
    if os.path.exists(TEMPLATE_FILE):
        break

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
    for dirpath, dirnames, filenames in os.walk(os.getcwd()):
        for filename in [f for f in filenames if f == 'index.html']:
            # language is root directory
            language = dirpath.split(os.sep)[-1]

            # source is 2 above
            source = dirpath.split(os.sep)[-2]

            # report is 3 above
            repo = dirpath.split(os.sep)[-3]

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

                for item in reports[repo][item_type]:
                    print(f'Found {item_type}: {item}. for repo: {repo}')

                    # create a list item in html
                    list_item = f"""
                    <li>{item}
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
