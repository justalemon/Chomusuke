# Import our little set of tools
import argparse
import asyncio
import os
import sys
from bot import Chomusuke
from dotenv import load_dotenv


def main():
    """
    Our main function.
    """
    # Start by creating our parser
    parser = argparse.ArgumentParser()
    parser.add_argument("--manual-env", dest="manual_env", action="store_true", help="if the .env file should be loaded manually by the bot")
    # Parse our arguments
    args = parser.parse_args()

    # If the user requested the manual adition of .env, use python-dotenv
    if args.manual_env:
        load_dotenv()

    # If the discord token is not on the environment variables
    if "DISCORD_TOKEN" not in os.environ:
        # Exit with a code 2
        sys.exit(2)

    # If the bot prefix is not on the environment variables
    if "DISCORD_PREFIX" not in os.environ:
        # Exit with a code 3
        sys.exit(3)

    # Create a dictionary of keyword arguments
    kwargs = {
        "command_prefix": os.environ["DISCORD_PREFIX"]
    }

    # If there is a MongoDB database added
    if "MONGODB_URL" in os.environ:
        # Add the database to our keyword arguments
        kwargs["database"] = os.environ["MONGODB_URL"]

    # Create our bot instance
    bot = Chomusuke(**kwargs)

    # Iterate over the python files from the ext folder
    for file in [x for x in os.listdir("ext") if x.endswith(".py")]:
        # Try to load the extension
        try:
            bot.load_extension("ext." + os.path.splitext(file)[0])
        # If there was a problem, intercept the exception
        # TODO: Change to real logging
        except Exception:
            print(f"Unable to load {file}")

    # We have everything, start loading the bot
    try:
        # Get the event loop
        loop = asyncio.get_event_loop()
        # Log and connect the user
        loop.run_until_complete(bot.login(os.environ["DISCORD_TOKEN"]))
        loop.run_until_complete(bot.connect())
    except KeyboardInterrupt:
        # After a CTRL+C or CTRL+Z, log out the bot and disconnect everything
        loop.run_until_complete(bot.logout())
    finally:
        # Afer finishing, grab all tasks
        tasks = asyncio.all_tasks(loop)
        # Run all of the tasks until they have completed
        loop.run_until_complete(asyncio.gather(*tasks))
        # Only after the tasks have been completed, close the loop
        loop.close()
        # Finally, exit with a code zero
        sys.exit(0)


if __name__ == "__main__":
    main()
