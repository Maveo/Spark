from bot import DiscordBot


def main():
    from fastapi.openapi.utils import get_openapi
    from webserver.server import WebServer
    import json
    import os

    top_level_dir = os.path.join(os.path.realpath(os.path.dirname(__file__)), '..')

    app = WebServer(
        discord_bot=DiscordBot(
            current_dir=top_level_dir,
        ),
    ).app

    file_path = os.path.join(top_level_dir, 'docs', 'openapi.json')
    with open(file_path, 'w') as f:
        json.dump(get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            routes=app.routes,
        ), f)


if __name__ == '__main__':
    main()
